'''//////////////DATABASE for PORTSCANNER/////////////////'''
import sqlite3
from datetime import date,datetime
try:
	database = sqlite3.connect('portdb')
	cursor = database.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS IPINFO(IP TEXT,TYPE INTEGER,ALIVE BOOLEAN,TIME DATETIME, PRIMARY KEY(IP,TIME))''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS PORTDATA(PORT INTEGER,IP TEXT, TIME DATETIME,ALIVE BOOLEAN,FOREIGN KEY(IP,TIME) REFERENCES IPINFO(IP,TIME) )''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS IPDATA(IP TEXT,ALIVE BOOLEAN,TIME DATETIME,FOREIGN KEY(IP,TIME) REFERENCES IPINFO(IP,TIME) )''')
	database.commit()
except Exception as e:
	database.rollback()
	raise e
finally:
	database.close()
