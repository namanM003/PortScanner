#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import sqlite3
from datetime import datetime 
from Server import Producer
from datatypes import Request

PORT_NUMBER = 8070
db = sqlite3.connect('portdb')
cursor = db.cursor()
#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
	#	if self.path=="/send":
	#		form = cgi.FieldStorage(
	#			fp=self.rfile, 
	#			headers=self.headers,
	#			environ={'REQUEST_METHOD':'POST',
	#	                 'CONTENT_TYPE':self.headers['Content-Type'],
	#		})

	#		print "Your name is: %s" % form["IP"].value
			
	#		self.send_response(200)
	#		self.end_headers()
	#		#self.wfile.write("Thanks %s %s %s!" % form["IP"].value)
	#		today = datetime.now()
        #               print "here1" 	
	#		cursor.execute('''INSERT INTO IPINFO(IP,BLOCK_IP,PORT,TIME)VALUES(?,?,?,?)''',(form["IP"].value,form["block"].value,form["port"].value,today))
         #               db.commit()
         #               cursor.execute("SELECT * FROM IPINFO")
         #               data = cursor.fetchall()
         #               print " Data " + str(data)a
			request = Request(1,"120.120.120.120",200,10,20)
			Producer(Request)
			return			
			
			
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	thread.start_new_thread(add_client, ())
	thread.start_new_thread(client_listen, ())
 	print "Started"	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
	
