'''//////////////DATABASE for PORTSCANNER/////////////////'''
import sqlite3
from datetime import date,datetime
try:
	database = sqlite3.connect('portdb')
	cursor = database.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS IPINFO(IP TEXT,BLOCK_IP BOOLEAN,PORT BOOLEAN,TIME DATE, PRIMARY KEY(IP,TIME))''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS PORTDATA(PORT BOOLEAN,IP TEXT, TIME DATE,FOREIGN KEY(IP,TIME) REFERENCES IPINFO(IP,TIME) )''')
	database.commit()
except Exception as e:
	database.rollback()
	raise e
finally:
	database.close()
