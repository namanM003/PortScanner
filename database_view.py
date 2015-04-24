import sqlite3
conn = sqlite3.connect('portdb')
cursor = conn.execute("SELECT * from IPINFO")
for roe in cursor:
	print roe
cursor = conn.execute("SELECT * from PORTDATA")
for row in cursor:
	print 'x'
print "Printing the whole table"

cursor = conn.execute("SELECT * from IPDATA")
for row in cursor:
        print row

print " PRINTTING"
date = "2015-04-24 21:58:05.598864"
cursor = conn.execute('SELECT * FROM IPDATA WHERE TIME=?',[date])
for row in cursor:
	print row
