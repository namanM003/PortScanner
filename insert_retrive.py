'''Function to insert and retrive from database'''
import sqlite3
from datetime import date,datetime
today = date.today()
db = sqlite3.connect('portdb')
def insert(ip,block,port):
	try:
		cursor = db.cursor()
		cursor.execute('''INSERT INTO IPINFO(IP,BLOCK_IP,PORT,TIME)VALUES(?,?,?,?)''',(ip,block,port,today))
		#cursor.execute('''INSERT INTO PORTDATA(PORT))
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()

