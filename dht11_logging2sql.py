import RPi.GPIO as GPIO
import dht11
import time
import datetime
import MySQLdb

# define
SQL_USER = 'XXXX'
SQL_PASSWD = 'XXXX'
SQL_HOST = 'XXXX'
SQL_DATABASE = 'XXXX'
MAX_RETRY = 30


# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# SQL
cnx = None
cursor = None

# read data using pin 14
dht = dht11.DHT11(pin=14)

def sql_connect():
	global cnx, cursor
	cnx = MySQLdb.connect(
		user = SQL_USER,
		password = SQL_PASSWD,
		host = SQL_HOST,
		database = SQL_DATABASE
	)
	cursor = cnx.cursor()

def sql_insertDHTdata(date, time, temp, humid):
	global cnx, cursor
	sql = (
		'''
		INSERT INTO dht11
			(date, time, temp, humid)
		VALUES
			(%s, %s, %s, %s)
		'''
	)
	
	data = (date, time, temp, humid)
	cursor.execute(sql, data)
	cnx.commit()
	cursor.close()

def sql_disconnect():
	cnx.close()
	
def dht_getdata():
    retry_count = 0
    while True:
        result = dht.read()
        if result.is_valid():
            ret = dict(date=datetime.datetime.now().date().strftime("%Y-%m-%d"),
					   time=datetime.datetime.now().time().strftime("%H:%M:%S.%f"),
                       temperature=result.temperature,
                       humidity=result.humidity,
                      )
            break
        else:
            retry_count += 1
            time.sleep(0.5)

        if retry_count == MAX_RETRY:
            ret = dict(date="err",
					   time="err",
                       temperature="err",
                       humidity="err"
					   )
            break
    return ret

def trig_getdata():
	if datetime.datetime.now().second == 0:
		return True
	else:
		return False

def main():
	if trig_getdata():
		dhtdata = dht_getdata()
		if not (dhtdata["date"] == "err"):
			sql_connect()
			sql_insertDHTdata(
				dhtdata["date"],
				dhtdata["time"],
				dhtdata["temperature"],
				dhtdata["humidity"]
			)
			sql_disconnect()
			time.sleep(1)
			print("Data is stored.")
		else:
			print("Failed getting data.")

while True:
	main()
