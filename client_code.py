import socket
import sys
import thread
import cPickle as pickle
from datatypes import ClientRequest
from datatypes import Response
from port_scanner_function import scan_port_ack
from port_scanner_function import is_up
from port_scanner_connect_call import scan_port_connect
from port_scanner_fin import scan_port_fin
from threading import Thread, Lock
from threading import Condition
import time
import random

queue = []
lock = Lock()

condition = Condition()

def scan_ip(port_list):
 response = dict()
 for i in range(0,len(port_list)):
      if(True == is_up(port_list[i])):
          response[port_list[i]] = True
      else:
          response[port_list[i]]  = False
 return response

class ConsumerThread(Thread):
    def run(self):
        dict_response = dict()
        global queue
        while True:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
                condition.wait()
                print "Producer added something to queue and notified the consumer"
            request = queue.pop(0)
            print "Consumed" + str (request.ip_addr)
            condition.release()
            print >>sys.stderr, 'received "%s"' % request.ip_addr
            if  request.type == 1:                                   
                print " In request type 1"
                print " For scanning IP " + str(request.ip_addr)
                if(True == is_up(request.ip_addr)):
                   dict_response[request.ip_addr] = True
                else:
                  dict_response[request.ip_addr]  = False
            elif request.type == 2:
                print "In request type 2 "
                dict_response = scan_ip(request.port_list)

            elif request.type == 3:                                          ### For port scanning 
                 print " In request type 3 "
                 if request.port_scanning_mode == 1:
                    print "Requested SYN mode"
                    dict_response=scan_port_ack(request.port_list,request.ip_addr)  ### Add modes
                    print "got response " + str(dict_response)
                 elif request.port_scanning_mode == 2:
                    print "Requested Full connect "
                    dict_response=scan_port_connect(request.port_list,request.ip_addr)
                 elif request.port_scanning_mode == 3:
                    print " Requested Fin mode "
                    dict_response=scan_port_fin(request.port_list,request.ip_addr)    ##change this to Fin
                 else :
                     print "Scanning mode invalid"
                 
            else:
                 print "GOT WRONG PACKET"                 
            resp = Response(request.type,request.ip_addr,request.ip_subnet,request.port_start,request.port_end,request.port_list,request.date_today,dict_response,request.date_only)
            print "Sending to the server"
            server_send(resp)            
            


def server_send(response):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        
        print >>sys.stderr, 'starting up on %s port %s' % client_address
        
        sock.connect(server_address)  
        data_string = pickle.dumps(response, -1)
        print "Final send to the server "
        sock.sendall(data_string)
    finally:
            print >>sys.stderr, 'closing socket'
            sock.close()

def client_listen():                                         ### As well as producer code here
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_address = ('localhost', 10005)
    print >>sys.stderr, 'starting up on %s port %s' % client_address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(client_address)
    # Listen for incoming connections
    sock.listen(10)
    dict_response = dict()
    while True:
        connection, server_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', server_address  
            # Receive the data in small chunks and retransmit it
          
            data = connection.recv(10000)
           
            request = pickle.loads(data)
            condition.acquire()
            
            length = len(queue)
            queue.append(request)
            print "Produced", request
            
            if length == 0:                                   ### Taking the length just before adding the elements 
              print "Notifying"
              condition.notify()
            
            condition.release()
            
 
        finally:
            # Clean up the connection
            connection.close()
        

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_address = ('localhost', 10005)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(client_address)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    
    # Send data
    message = 'This is the message.  It will be repeated.'
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print >>sys.stderr, 'received "%s"' % data

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    
try:
    thread.start_new_thread(client_listen, ())                                ## Producer thread !!
    ConsumerThread().start()

except:
   print "unable to start thread"

while 1:
   pass
