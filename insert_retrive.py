'''Function to insert and retrive from database'''
import sqlite3
from datetime import date,datetime
today = datetime.now()
#print "Date" + str(today)
db = sqlite3.connect('portdb')


today=datetime.now()
cursor = db.cursor()
ip     = "192.232.23.11"
block  = "yes"
port   = "yes"
cursor.execute('''INSERT INTO IPINFO(IP,BLOCK_IP,PORT,TIME)VALUES(?,?,?,?)''',(ip,block,port,today))
db.commit()
print " Here after committed "
cursor.execute("SELECT * FROM IPINFO")
data = cursor.fetchall()
print " Data " + str(data)
for wor in data:
	print wor

def insert(ip,block,port):
	try:
		today=datetime.now()
		cursor = db.cursor()
		cursor.execute('''INSERT INTO IPINFO(IP,BLOCK_IP,PORT,TIME)VALUES(?,?,?,?)''',(ip,block,port,today))

		
		 #cursor.execute('''INSERT INTO PORTDATA(PORT))
		
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()

 
