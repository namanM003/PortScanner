import socket
import sys
import thread
import time
from threading import Thread, Lock
from threading import Condition
import random
import cPickle as pickle
from datatypes import *
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import sqlite3
from datetime import datetime
#from datatypes import Request


PORT_NUMBER = 8070
db = sqlite3.connect('portdb')
cursor = db.cursor()
#This class will handles any incoming request from
#the browser 

clients = []
queue = []
response_queue = []

condition = Condition()
condition_response = Condition()

def add_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = ('localhost', 10000)
    
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    sock.listen(5)
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        clients.append(client_address)
        
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.close()
        # Create a TCP/IP socket


def client_listen():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock1.bind(server_address)
    
    sock1.listen(5)
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock1.accept()
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            data = connection.recv(11000)
	    response = pickle.loads(data)
	    print >>sys.stderr, 'received "%s"' % response.result_dict
	    ProducerResponse(response);
                
        finally:
            # Clean up the connection
            connection.close()
        # Create a TCP/IP socket

def broadcast_message():
    
    while 1:
        time.sleep(4)
        for i in range(len(clients)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_address = clients[i]
            sock.connect(client_address)
            try:
                # Send data
                print "here1"
                request = Request(1,"120.120.120.120",200,10,20)
                print "here2"
                data_string = pickle.dumps(request, -1)
                print "here3" 
                #print data_string            
                #print >>sys.stderr, 'sending "%s"' % data_string
                sock.sendall(data_string)
            finally:
                print >>sys.stderr, 'closing socket'
                sock.close()

def send_client(client_address, request, port_start, port_end):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(client_address)
	port_list = []
	for i in range(port_start,port_end+1):
		port_list.append(i)
        client_request = ClientRequest(request.type,request.ip_addr,0,port_start,port_end, port_list, request.date_today,request.port_scanning_mode)
        data_string = pickle.dumps(client_request, -1)
        print 'sending' + str(client_request.type) + ' to ' , client_address
        sock.sendall(data_string)
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
        

class ConsumerThread(Thread):
    def run(self):
        global queue
        while True:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
                condition.wait()
                print "Producer added something to queue and notified the consumer"
            request = queue.pop(0)
            print "Consumed", request.ip_addr , request.type
            if request.type == 3:
                no_of_ports = request.port_end - request.port_start + 1
                length = len(clients)
                ports = no_of_ports/length
                start = request.port_start
                end = start + ports - 1
                i = 0
                while True:
                    if (end >=  request.port_end):
                        if (start <= request.port_end):
                            send_client(clients[i], request, start, request.port_end)
                        break
                    else :
                        send_client(clients[i], request, start, end)
                        i = (i + 1)%length
                        start = end + 1
                        end = start + ports - 1
            condition.release()
            time.sleep(1)
 
def Producer(request):
    global queue   
    condition.acquire()
    length = len(queue)
    queue.append(request)
    print "Produced", request 
    if length == 0:
        print "Notifying"
        condition.notify()
    condition.release()

class ConsumerResponseThread(Thread):
    def run(self):
        global response_queue
        while True:
            condition_response.acquire()
            if not response_queue:
                print "Nothing in queue, consumer is waiting"
                condition_response.wait()
                print "Producer added something to queue and notified the consumer"
            response = response_queue.pop(0)
            print "Consumed", response.ip_addr , response.type, str(response.result_dict())
            if response.type == 1:
                print " In type 1 "
		for k,v in response.result_dict.items():
			cursor.execute('''UPDATE IPINFO SET ALIVE = ? WHERE IP = ? AND TIME = ? ''',(v,response.ip_addr,response.date_today)) #We assume there will be only one result
	    if response.type == 2:
                print " In type 2 "
		for k,v in response.result_dict.items():
            		cursor.execute('''INSERT INTO IPINFO(IP,TYPE,ALIVE,TIME)VALUES(?,?,?,?)''',(k,2,v,response.date_today))
	    if response.type == 3:
                print " In type 3 "
                for k,v in response.result_dict.items():
                	cursor.execute('''INSERT INTO PORTDATA(PORT,IP,TIME,ALIVE)VALUES(?,?,?,?)''',(k,response.ip_addr, response.date_today,v))
            db.commit()
	    condition_response.release()
            time.sleep(1)
    
def ProducerResponse(response):
    global response_queue   
    condition_response.acquire()
    length = len(response_queue)
    response_queue.append(response)
    print "Produced", response 
    if length == 0:
        print "Notifying"
        condition_response.notify()
    condition_response.release()    
# Listen for incoming connections
#try:
#    thread.start_new_thread(add_client, () )
 #   thread.start_new_thread(broadcast_message,( ))
#    thread.start_new_thread(client_listen,( ))
#    ConsumerThread().start()
#except:
#   print "Error: unable to start thread"

#while 1:
#   pass
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
	# this line will be for host scan 
        def do_POST(self):
                if self.path=="/ports":
                        form = cgi.FieldStorage(
                                fp=self.rfile,
                                headers=self.headers,
                                environ={'REQUEST_METHOD':'POST',
                                 'CONTENT_TYPE':self.headers['Content-Type'],
                        })
			type_scan = 3
			'''	
			internet_protocol = form["IP"].value
			start_port = form["start"].value
			end_port = form["end"].value
			random = form["random"].value
			'''
			today = datetime.now()
			#request = Request(type_scan,internet_protocol,0,start_port,end_port,random,today)
			request = Request(3,"216.178.46.224",0,79,84,False,today,1)
			#today = datetime.now()
			#cursor.execute('''INSERT INTO IPINFO(IP,TYPE,ALIVE,TIME)VALUES(?,?,?,?)''',(form["IP"].value,type_scan,NULL,today))
			db.commit()
			Producer(request)
			return
		if self.path == "/hosts":
			form = cgi.FieldStorage(
				fp = self.rfile,
				headers = self.headers,
				environ={'REQUEST_METHOD':'POST',
				 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			today = datetime.now()
			if form["Multi-Host"].value == False:
#IN UI GIVE THIS FUNCTIONALITY OF MULTI_HOST This value should come from UI by checking IP
				type_scan = 1
				internet_protocol = form["IP"].value
				start_port = 0
				end_port = 0 
				request = Request(type_scan, internet_protocol,0,start_port,end_port)
				random = form["random"].value
				cursor.execute('''(INSERT INTO IPINFO(IP, TYPE, ALIVE, TIME)VALUES(?,?,?,?)''',(form["IP"].value,type_scan,NULL,today))
				db.commit()
				Producer(request)
				print "Perfectly Received Request"
				return
			if form["Multi-Host"].value == True:
				type_scan = 2
				internet_protocol = form["IP"].value
				start_port = 0
				end_port = 0
				random = form["random"].value	#We have still not sending this field value as a parameter in request object
				request = Request(type_scan, internet_protocol, 0, start_port, end_port)
				cursor.execute('''(INSERT INTO IPINFO(IP, TYPE, ALIVE, TIME)VALUES(?,?,?,?)''',(form["IP"].value,type_scan,NULL,today))
				db.commit()
				Producer(request)
				print "Perfectly Received Request"
				return
		'''
		if self.path == "/results":
			form = cgi.FieldStorage(
				fp = self.rfile,
				headers = self.headers,
				environ={'REQUEST_METHOD':'POST',
				 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			if form['Result'].value == "HostScanning":
				if form["IP"].value == "none"
					
					con=cursor.execute("SELECT * FROM IPINFO WHERE TIME > form["Date"].value AND TIME < form["Date"].value+1)
					rows = con.fetchall()
					for row in rows:
						result_host = {
							'IP': row.IP,
							'ALIVE' : row.ALIVE}
						results_host.append(result_host)
				else:
					con = cursor.execute("SELECT * FROM IPINFO WHERE IP = form["IP"].value AND TIME > form["Date"].value AND TIME < form["Date"].value+1")
					rows = con.fetchall()
					for row in rows:
						result_host = {
							'IP' : row.IP,
							'ALIVE':row.ALIVE}
						results_host.append(result_host)
 
			if form["Result"].value == "PortScanning":
				if form["IP"] == "none"
					con =cursor.execute("SELECT * FROM PORTDATA WHERE TIME > form["DATE"].value AND TIME < form["DATE"].value+1"
					rows = con.fetchall()
					for row in rows:
						result_port = {
							'IP': row.IP,
							'PORT': row.PORT,
							'Open': row.ALIVE}
						results_port.append(result_port)
				else:
					#con = cursor.execute("SELECT ALIVE FROM IPINFO WHERE IP = form["IP"].value AND TIME > form["DATE"].value AND TIME < form["DATE"].value+1")
					#validator = con.fetchall()
					
					con = cursor.execute("SELECT * FROM PORTDATA WHERE IP = form["IP"].value AND TIME > form["DATE"].value AND TIME < form["DATE"].value+1")
					rows = con.fetchall()
					for row in rows:
						result_host = {
							'IP' : row.IP,
							'PORT': row.PORT,
							'OPEN':row.ALIVE}
						results_port.append(result_port)
		'''
		# Complete this method for type 2 which is IP Subnet type
		#if self.path == "/
	 			
		# Here we will write for another function for port scan instead of host scan
		#if self.path=="/portscan"  Define complete method
                        #print "Your name is: %s" % form["IP"].value

                        #self.send_response(200)
                        #self.end_headers()
                        #self.wfile.write("Thanks %s %s %s!" % form["IP"].value)
                        #today = datetime.now()
                        #print "here1" 
                        #print "here1" 
                        #print "here1" 
                        #cursor.execute('''INSERT INTO IPINFO(IP,BLOCK_IP,PORT,TIME)VALUES(?,?,?,?)''',(form["IP"].value,form["block"].value,form["port"].value,today))
                        #db.commit()
                        #cursor.execute("SELECT * FROM IPINFO")
                        #data = cursor.fetchall()
                        #print " Data " + str(data)
                        #print "Before Request"
                        #from Server import Producer
                        #request = Request(1,"120.120.120.120",200,10,20)
                        #Producer(request)
                        #print "After Producer"
                        #return


try:
        #Create a web server and define the handler to manage the
        #incoming request

        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER
	thread.start_new_thread(add_client, () )
 #   thread.start_new_thread(broadcast_message,( ))
    	thread.start_new_thread(client_listen,( ))
	ConsumerThread().start()

        #Wait forever for incoming htto requests
        server.serve_forever()

except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()




