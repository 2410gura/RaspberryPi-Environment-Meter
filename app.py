import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from flask import Flask, render_template, request
import logging
import MySQLdb

# define
SQL_USER = 'XXXX'
SQL_PASSWD = 'XXXX'
SQL_HOST = 'XXXX'
SQL_DATABASE = 'XXXX'
LOGFILE = 'XXXX'
APP_HOST = 'XXXX'
APP_PORT = XXXX


#Flask設定
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOGFILE)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
app.logger.addHandler(fh)

# SQL
cnx = None
cursor = None

def sql_connect():
	global cnx, cursor
	cnx = MySQLdb.connect(
		user = SQL_USER,
		password = SQL_PASSWD,
		host = SQL_HOST,
		database = SQL_DATABASE
	)
	cursor = cnx.cursor()

def sql_getDHTdata(display_hour):
	global cnx, cursor
	ret_datetime = []
	ret_temp = []
	ret_humid = []
	
	sql = (
		f'''
		SELECT DATE_ADD(date, INTERVAL time HOUR_SECOND), temp, humid
		    FROM dht11 
			WHERE
			DATE_ADD(date, INTERVAL time HOUR_SECOND)
			>= DATE_SUB(NOW(),INTERVAL {display_hour} HOUR)
		'''
	)
	
	cursor.execute(sql)
	for row in cursor:
		ret_datetime.append(row[0])
		ret_temp.append(row[1])
		ret_humid.append(row[2])
	
	cnx.commit()
	cursor.close()
	ret = dict(datetime=ret_datetime, 
			   temp=ret_temp, 
			   humid=ret_humid
			   )
	return ret

def sql_disconnect():
	cnx.close()

def makeGraph_th(datetime, temp, humid):
	fig = plt.figure(figsize=(6, 4))
	ax1 = fig.add_subplot(1, 1, 1)
	ln1 = ax1.plot(datetime, temp, color="deeppink", label="Temperature")
	ax2 = ax1.twinx()
	ln2 = ax2.plot(datetime, humid, color="dodgerblue", label="Humidity")
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
	h1, l1 = ax1.get_legend_handles_labels()
	h2, l2 = ax2.get_legend_handles_labels()
	ax1.legend(h1+h2, l1+l2, loc="upper right")
	ax1.set_xlabel("TIME")
	ax1.set_ylabel("TEMP[℃]")
	ax2.set_ylabel("HUMID[%]")
	plt.savefig("static/graph_th.png", format="png", dpi=300)

@app.route('/', methods=['GET', 'POST'])
def index():
	display_hour = 24
	if request.method == 'POST':
		display_hour = request.form['display_hour']
	sql_connect()
	ContentsData = sql_getDHTdata(display_hour)
	makeGraph_th(ContentsData["datetime"], ContentsData["temp"], ContentsData["humid"])
	sql_disconnect()
	return render_template('index.html',
                            datetime=ContentsData['datetime'][-1],
                            temperature=ContentsData['temp'][-1],
                            humidity=ContentsData['humid'][-1],
							display_hour=display_hour
                           )

if __name__ == '__main__':
    app.run(host=APP_HOST, port=APP_PORT, debug=False)