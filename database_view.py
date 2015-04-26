import sqlite3
conn = sqlite3.connect('portdb')
cursor = conn.execute("SELECT * from IPINFO ORDER BY TIME DESC")

for roe in cursor:
	print roe
print " See till here "
cursor = conn.execute("SELECT * from PORTDATA")
for row in cursor:
	print 'x'
print "Printing the whole table"

cursor = conn.execute("SELECT * from IPDATA")
for row in cursor:
        print row

print " PRINTTING"
date = "2015-04-25"
cursor = conn.execute('SELECT * FROM IPINFO WHERE DATE1=? ORDER BY TIME DESC',[date])

for row in cursor:
	print row
