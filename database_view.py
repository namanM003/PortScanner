import sqlite3
conn = sqlite3.connect('portdb')
cursor = conn.execute("SELECT * from IPINFO")
for roe in cursor:
	print roe
cursor = conn.execute("SELECT * from PORTDATA")
for row in cursor:
	print row

