'''////////////////Python DATABASE////////'''
import sqlite3
from datetime import date, datetime
try:
	db = sqlite3.connect('webdb')
	cursor = db.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS portscanned(id INTEGER PRIMARY KEY, IP TEXT,Ports int,Time DATE)''')
	db.commit()
	id1 = 1
	ip = '1.1.1.1'
	port1 = 65536
	today = date.today()
	cursor.execute('''INSERT INTO portscanned(id,IP,Ports,Time)VALUES(?,?,?,?)''',(id1,ip,port1,today))
	print('First Port inserted')
	db.commit()
except Exception as e:
	db.rollback()
	raise e
finally:
	db.close()
