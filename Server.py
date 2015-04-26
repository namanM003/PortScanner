import socket
import sys
import thread
import time
import os
from threading import Thread, Lock
from threading import Condition
from netaddr import IPNetwork
import logging
from random import shuffle
import cPickle as pickle
from datatypes import *
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import sqlite3
import json
import datetime
import math

PORT_NUMBER = 8070
db = sqlite3.connect('portdb', check_same_thread=False)
cursor = db.cursor()
#This class will handles any incoming request from
#the browser 

clients = []
queue = []
response_queue = []

condition = Condition()
condition_response = Condition()

logger = None

def InitializeLogger(Name): 
    logger = logging.getLogger(Name) 
    hdlr = logging.FileHandler(Name + '.log') 
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') 
    hdlr.setFormatter(formatter) 
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

def add_client():
    global logger
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
	#logger.info("New Client added : " + str(client_address))
        
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(100)
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
    global logger
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock1.bind(server_address)
    
    sock1.listen(5)
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
	#logger.info("Waiting for response from clients")
        connection, client_address = sock1.accept()
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            data = connection.recv(11000)
	    response = pickle.loads(data)
	    print >>sys.stderr, 'received "%s"' % response.result_dict
            print " Got Response " + str(response.result_dict)
	    #logger.info("Got response " + str(response.ip_addr) + ":" + str(response.date_today))
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
                request = Request(1,"120.120.120.120",200,10,20)
                data_string = pickle.dumps(request, -1)
                #print data_string            
                #print >>sys.stderr, 'sending "%s"' % data_string
                sock.sendall(data_string)
            finally:
                print >>sys.stderr, 'closing socket'
                sock.close()

def send_client(client_address, request,start, end, ip_list):
    global logger
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(client_address)
	if request.type == 1:
		client_request = ClientRequest(request.type, request.ip_addr,0,0,0,0,request.date_today,request.port_scanning_mode,request.date_only)	
	if request.type == 2:
		ip = []
		for i in range(start, end + 1):
			ip.append(ip_list[i])
		if request.random == True:
			shuffle(ip)
                        print " GOT RANDOM REQUEST "
		client_request = ClientRequest(request.type, request.ip_addr, request.ip_subnet, start,end,ip,request.date_today,request.port_scanning_mode,request.date_only)
	if request.type == 3:
		port_list = []
		for i in range(start,end+1):
			port_list.append(i)
		if request.random == True:
			shuffle(port_list)
                        print " GOT RANDOM REQUEST "
       		client_request = ClientRequest(request.type,request.ip_addr,0,start,end, port_list, request.date_today,request.port_scanning_mode,request.date_only)
        data_string = pickle.dumps(client_request, -1)
	print 'sending' + str(client_request.type) + ' to ' , client_address
	#logger.info("Sending request to client : "+str(client_address)+" : " + str(request.ip_addr) + ":" + str(request.date_today))
	sock.sendall(data_string)
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
        

class ConsumerThread(Thread):
    global logger
    def run(self):
        global queue
        while True:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
		#logger.info("Nothing in queue, consumer is waiting")
                condition.wait()
                print "Producer added something to queue and notified the consumer"
		#logger.info("Producer added something to queue and notifies the consumer")
            request = queue.pop(0)
            print "Consumed", request.ip_addr , request.type
	    #logger.info("Consumed :" + str(request.ip_addr) + ":" + str(request.date_today))
	    if request.type == 1:
		send_client(clients[0], request, 0, 0, None)
	    if request.type == 2:
		ip_with_subnet = str(request.ip_addr) + "/" + str(request.ip_subnet)
		total_list = list()
		for ip in IPNetwork(ip_with_subnet):
   			total_list.append(str(ip))
		length = len(clients)
		no_of_ips = len(total_list)
		ips = no_of_ips/length
		start = 0
		end = start + ips - 1
		i = 0
		while True:
		    if (end >= len(total_list)-1):
			if (start <= len(total_list)-1):
		              send_client(clients[i],request,start,len(total_list)-1,total_list)
		    	break
		    else :
			send_client(clients[i],request,start,end,total_list)
			i = (i+1)%length
			start = end + 1
			end = start + ips -1
            if request.type == 3:
                no_of_ports = request.port_end - request.port_start + 1
                length = len(clients)
                ports = int(math.ceil(no_of_ports/float(length)))
                print "Ports " + str(ports)
                start = request.port_start
                end = start + ports - 1
                i = 0
                while True:
                    if (end >=  request.port_end):
                        if (start <= request.port_end):
                            send_client(clients[i], request, start, request.port_end,None)
                        break
                    else :
                        send_client(clients[i], request, start, end,None)
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
            print "Consumed_Response Thred", response.ip_addr , response.type, str(response.result_dict)
            if response.type == 1:
                print " In type 1 "
		for k,v in response.result_dict.items():
			cursor.execute('''UPDATE IPINFO SET ALIVE = ? WHERE IP = ? AND TIME = ?''',(v,response.ip_addr,response.date_today)) #We assume there will be only one result
	    if response.type == 2:
                print " In type 2 "
		for k,v in response.result_dict.items():
            		cursor.execute('''INSERT INTO IPDATA(IP,ALIVE,TIME,DATE1)VALUES(?,?,?,?)''',(k,v,response.date_today,response.date_only))
	    if response.type == 3:
                print " In type 3 "
                for k,v in response.result_dict.items():
                	if v=="HostDown":
				cursor.execute('''INSERT INTO PORTDATA(PORT,IP,TIME,ALIVE)VALUES(?,?,?,?)''',(k,response.ip_addr, response.date_today,None))
				cursor.execute('''UPDATE IPINFO SET ALIVE = ? WHERE IP = ? AND TIME = ?''',(False, response.ip_addr, response.date_today))
			else:
				print response.date_today
				cursor.execute('''INSERT INTO PORTDATA(PORT,IP,TIME,ALIVE)VALUES(?,?,?,?)''',(k,response.ip_addr, response.date_today,v))
				cursor.execute('''UPDATE IPINFO SET ALIVE = ? WHERE IP = ? AND TIME = ?''',(True, response.ip_addr, response.date_today))
            db.commit()
	    condition_response.release()
            time.sleep(1)
    
def ProducerResponse(response):
    global response_queue   
    condition_response.acquire()
    length = len(response_queue)
    response_queue.append(response)
    print "Produced_response", response 
    if length == 0:
        print "Notifying"
        condition_response.notify()
    condition_response.release()    

class myHandler(BaseHTTPRequestHandler):

        #Handler for the GET requests
        def do_GET(self):
                if self.path=="/":
                        self.path="/index.html"
		if self.path=="/?":
			self.path="/index.html"
		if self.path== "/\\":
			self.path="/index.html"
		if self.path == "/\\index.html?":
			self.path = "/index.html"
		if self.path == "/index.html?":
			self.path = "/index.html"
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
				
			#################################################
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
			self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.path = "/index.html"
                        mimetype = 'text/html'
                        f = open(curdir + sep + self.path)
                        #self.send_response(200)
                        #self.send_header('Content-type',mimetype)
                        #self.end_headers()
                        self.wfile.write(f.read())
			f.close()
				
			internet_protocol = form["IP"].value
			start_port = form["start"].value
			end_port = form["end"].value
			random1 = False
			try:
				random1 = form["random"].value
				random1 = True
			except:
				random1 = False
			print random1
			port_scan_mode = form["typeofscanning"].value
			today = datetime.datetime.now()
			date_today = datetime.date.today()
			request = Request(type_scan,internet_protocol,0,int(start_port),int(end_port),random1,today,int(port_scan_mode),date_today)
                        length = int(end_port) - int(start_port) + 1
			#request = Request(3,"216.178.46.224",0,79,84,False,today,1)
			#today = datetime.now()
			cursor.execute('''INSERT INTO IPINFO(IP,TYPE,ALIVE,TIME,DATE1,LENGTH)VALUES(?,?,?,?,?,?)''',(form["IP"].value,type_scan,None,today,date_today,length))
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
			self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.path = "/index.html"
                        mimetype = 'text/html'
                        f = open(curdir + sep + self.path)
			
                        #self.send_response(200)
                        #self.send_header('Content-type',mimetype)
                        #self.end_headers()
                        self.wfile.write(f.read())
			f.close()
			today = datetime.datetime.now()
			date_today = datetime.date.today()
			############TRY######
			'''
			self.send_response(200)
			self.send_header('Content-Type','application/json')
			data = {}
			data['test'] = 'OK'
			json_data = json.dumps(data)
			self.request.send(json_data)
			self.end_headers()
			'''
			###########1###########
			if form["Multi-Host"].value == "false":
			#IN UI GIVE THIS FUNCTIONALITY OF MULTI_HOST This value should come from UI by checking IP
				
				type_scan = 1
				subnet = int(form["subnet"].value)
                                length = pow(2,32-subnet)
				internet_protocol = form["IP"].value
				start_port = 0
				end_port = 0 
				request = Request(type_scan, internet_protocol,0,int(start_port),int(end_port), False,today,1,date_today)
				#random = form["random"].value
				cursor.execute('''INSERT INTO IPINFO(IP, TYPE, ALIVE, TIME, DATE1,LENGTH)VALUES(?,?,?,?,?,?)''',(form["IP"].value,type_scan,None,today,date_today,length))
				db.commit()
				Producer(request)
				print "Perfectly Received Request"
				return
			if form["Multi-Host"].value == "true":
				type_scan = 2
				internet_protocol = form["IP"].value
				subnet = int(form["subnet"].value)
				length = pow(2,32-subnet)
				start_port = 0
				end_port = 0
				random1 = False
				try:
					random1 = form["random"].value
					random1 = True
				except:
					random1 = False
				#random = form["random"].value	#We have still not sending this field value as a parameter in request object
				request = Request(type_scan, internet_protocol, subnet, int(start_port),int( end_port),random1,today,1,date_today)
				cursor.execute('''INSERT INTO IPINFO(IP, TYPE, ALIVE, TIME, DATE1,LENGTH)VALUES(?,?,?,?,?,?)''',(form["IP"].value,type_scan,None,today,date_today,length))
				#db.commit()
				Producer(request)
				print "Perfectly Received Request with length = " + str(length)
				return
		
		if self.path == "/results":
			form = cgi.FieldStorage(
				fp = self.rfile,
				headers = self.headers,
				environ={'REQUEST_METHOD':'POST',
				 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			self.send_response(200)
			self.send_header('Content-Type','application/json')
			con = cursor.execute("SELECT * FROM IPINFO ORDER BY TIME DESC")
			rows = con.fetchall()
			results_host = []
			valid = False
		        try:	
     				date = str(form["name"])
	               		date = date.split(",")
		        	date = date[1].strip("'")
                                date = date.strip(")")
				date = date[2:]
                                date = date.strip("'")
				valid = True
		        except:
                                valid = False
			if valid:
				con = cursor.execute('SELECT * FROM IPINFO WHERE DATE1=? ORDER BY TIME DESC',[date])
				rows = con.fetchall()
			#print form["name"]
			#result_host = {}	
			for row in rows:
				print str(row)
				result_host = {}
				result_host["IP"] = row[0]
				result_host["TYPE"] = row[1]
				result_host["ALIVE"] = row[2]
				result_host["TIME"] = row[3]
				result_host["DATE1"] = row[4]
				result_host["TYPE"] = row[1]
				result_host["LENGTH"] = row[5]
				#print result_host["IP"]
				results_host.append(result_host)
			json_data = json.dumps(results_host)
			self.end_headers()
			self.wfile.write(json_data)
			return 
		##################HERE WE ARE REDIRECTED WHEN USER SELECTS A RADIO BUTTON AND CLICK ON TO SEND TO SEE RESULT OF A SPECIFIC EXPERIMENT########3                
		if self.path == "/result2":
                        form = cgi.FieldStorage(
                                fp = self.rfile,
                                headers = self.headers,
                                environ={'REQUEST_METHOD':'POST',
                                 'CONTENT_TYPE':self.headers['Content-Type'],
                        })
                        self.send_response(200)
                        self.send_header('Content-Type','application/json')
			sup = str(form["name"])
			string = sup.split(",")
                 
			IP = string[1].split("'")
			IP = IP[1]
		        if (IP == "Empty"):
                          print "Empty table"
                          return 
			DATEQ = string[3]+" "+string[4]
			#DATE_Q = DATE_Q[0]
			TYPE = int(string[2])
			LENGTH = string[6].split("'")
			LENGTH = LENGTH[0]
			#############QUERY FOR SPECIFIC DATA RESULT##########
			if TYPE==3:
				'''
				con = cursor.execute('SELECT * FROM IPINFO WHERE IP=? AND TYPE=? AND DATE1=?',(IP,TYPE,DATE_Q))
        	                rows = con.fetchall()
                	        results_host = []
                        #result_host = {}       
				print "QUERY EXECEUTION PHASE"
                        	for row in rows:
                                	print str(row)
	                                result_host = {}
        	                        result_host["IP"] = row[0]
                	                result_host["TYPE"] = row[1]
                        	        result_host["ALIVE"] = row[2]
	                                result_host["TIME"] = row[3]
        	                        result_host["DATE1"] = row[4]
                	                result_host["TYPE"] = row[1]
                        	        print result_host["IP"]
                                	results_host.append(result_host["TIME"])
				'''
				port_results = []
				for data in range(0,1):
					con = cursor.execute('SELECT * FROM PORTDATA WHERE IP=? AND TIME=?',(IP,DATEQ))
					rows = con.fetchall()
                                        scan = 1
					if len(rows) == int(LENGTH):
                                                scan = 1
					else:
                                                scan = 0
					if len(rows) == 0:
						port_result = {}
						port_result["SCAN"] = 0
						port_results.append(port_result)
					for row in rows:
						port_result = {}
                                                port_result["TYPE"] = 3
						port_result["PORT"] = row[0]
						port_result["IP"] = row[1]
						port_result["OPEN"] = row[3]
                                                port_result["SCAN"] = scan
						port_results.append(port_result)

				print " Sending Back to Client " + str(port_results)		
        	                json_data = json.dumps(port_results)
                	        self.end_headers()
                        	self.wfile.write(json_data)
			if TYPE == 2:
				'''
                                con = cursor.execute('SELECT * FROM IPINFO WHERE IP=? AND TYPE=? AND DATE1=?',(IP,TYPE,DATE_Q))
                                rows = con.fetchall()
                                results_host = []
                        #result_host = {}       
                                print "QUERY EXECEUTION PHASE"+str(TYPE)
                                for row in rows:
                                        print str(row)
                                        result_host = {}
                                        result_host["IP"] = row[0]
                                        result_host["TYPE"] = row[1]
                                        result_host["ALIVE"] = row[2]
                                        result_host["TIME"] = row[3]
                                        result_host["DATE1"] = row[4]
                                        result_host["TYPE"] = row[1]
                                        print result_host["IP"]
                                        results_host.append(result_host["TIME"])
				'''
                                ip_results = []
                                for data in range(0,1):
                                        con = cursor.execute('SELECT * FROM IPDATA WHERE TIME=?',[DATEQ])
                                        rows = con.fetchall()
                                        scan = 1
                                        if len(rows) == int(LENGTH):
                                                print "TRUi"
                                                scan = 1
                                        else:
                                                print "FALSE"
                                                scan = 0
                                        if len(rows) == 0:
						ip_result = {}
                                                ip_result["SCAN"] = 0
                                                ip_results.append(ip_result)

                                        for row in rows:
                                                ip_result = {}
                                                ip_result["TYPE"] = 2
                                                ip_result["IP"] = row[0]
                                                ip_result["ALIVE"] = row[1]
                                                ip_result["SCAN"]  = scan                                             
                                                print ip_result["ALIVE"]
                                                print ip_result["IP"]
                                                #print ip_result["OPEN"]
                                                ip_results.append(ip_result)
                                print "Sending back to client " + str(ip_results)
                                json_data = json.dumps(ip_results)
                                self.end_headers()
                                self.wfile.write(json_data)
			'''
				
			###################QUERY FOR PORT DATA END#############	
			##################TRY TO DIRECTLY SEND A WRITTEN HTML####################
                if self.path == "/result2":
                        form = cgi.FieldStorage(
                                fp = self.rfile,
                                headers = self.headers,
                                environ={'REQUEST_METHOD':'POST',
                                 'CONTENT_TYPE':self.headers['Content-Type'],
                        })
                        self.send_response(200)
                        self.send_header('Content-Type','application/json')
                        print form["val"]
                        sup = str(form["val"])
                        string = sup.split(",")
                        #print form["val"][1]
                        for stri in string:
                                print stri
                        IP = string[1].split("'")
                        IP = IP[1]
                        print IP
                        DATE_Q = string[3].split("'")
                        DATE_Q = DATE_Q[0]
                        print DATE_Q
                        TYPE = int(string[2])
                        print TYPE
			string = "<HTML>
                        #############QUERY FOR SPECIFIC DATA RESULT##########
                        if TYPE==3:
                                con = cursor.execute('SELECT * FROM IPINFO WHERE IP=? AND TYPE=? AND DATE1=?',(IP,TYPE,DATE_Q))
                                rows = con.fetchall()
                                results_host = []
                        #result_host = {}       
                                print "QUERY EXECEUTION PHASE"
                                for row in rows:
                                        print str(row)
                                        result_host = {}
                                        result_host["IP"] = row[0]
                                        result_host["TYPE"] = row[1]
                                        result_host["ALIVE"] = row[2]
                                        result_host["TIME"] = row[3]
                                        result_host["DATE1"] = row[4]
					result_host["DATE1"] = row[4]
                                        print result_host["IP"]
                                        results_host.append(result_host["TIME"])
                                port_results = []
                                for data in results_host:
                                        print "DATA IN OBJECT"
                                        con = cursor.execute('SELECT * FROM PORTDATA WHERE IP=? AND TIME=?',(IP,data))
                                        rows = con.fetchall()
                                        for row in rows:
                                                port_result = {}
                                                port_result["TYPE"] = 3
                                                port_result["PORT"] = row[0]
                                                port_result["IP"] = row[1]
                                                port_result["OPEN"] = row[3]
                                                print port_result["PORT"]
                                                print port_result["IP"]
                                                print port_result["OPEN"]
                                                port_results.append(port_result)

                                json_data = json.dumps(port_results)
                                self.end_headers()
                                self.wfile.write(json_data)
                        if TYPE == 2:
                                con = cursor.execute('SELECT * FROM IPINFO WHERE IP=? AND TYPE=? AND DATE1=?',(IP,TYPE,DATE_Q))
                                rows = con.fetchall()
                                results_host = []
                        #result_host = {}       
                                print "QUERY EXECEUTION PHASE"+str(TYPE)
                                for row in rows:
                                        print str(row)
                                        result_host = {}
                                        result_host["IP"] = row[0]
                                        result_host["TYPE"] = row[1]
                                        result_host["ALIVE"] = row[2]
                                        result_host["TIME"] = row[3]
                                        result_host["DATE1"] = row[4]
                                        result_host["TYPE"] = row[1]
                                        print result_host["IP"]
                                ip_results = []
                                for data in results_host:
                                        print "DATA IN OBJECT" + str(data)
                                        con = cursor.execute('SELECT * FROM IPDATA WHERE TIME=?',[data])
                                        rows = con.fetchall()
                                        for row in rows:
                                                ip_result = {}
                                                ip_result["TYPE"] = 2
                                                ip_result["IP"] = row[0]
                                                ip_result["ALIVE"] = row[1]

                                                print ip_result["ALIVE"]
                                                print ip_result["IP"]
                                                #print ip_result["OPEN"]
                                                ip_results.append(ip_result)

                                json_data = json.dumps(ip_results)
                                self.end_headers()
                                self.wfile.write(json_data)
		'''	
		'''
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


try:
        #Create a web server and define the handler to manage the
        #incoming request
	InitializeLogger(str(os.getpid()))

        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER
	thread.start_new_thread(add_client, () )
 #   thread.start_new_thread(broadcast_message,( ))
    	thread.start_new_thread(client_listen,( ))
	ConsumerThread().start()
        ConsumerResponseThread().start()

        #Wait forever for incoming htto requests
        server.serve_forever()

except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()




