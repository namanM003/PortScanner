import socket
import sys
import thread
import cPickle as pickle
from datatypes import Request

def client_listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_address = ('localhost', 10006)
    print >>sys.stderr, 'starting up on %s port %s' % client_address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(client_address)
    # Listen for incoming connections
    sock.listen(10)
    while True:
        connection, server_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', server_address  
            # Receive the data in small chunks and retransmit it
            print "here1"
            data = connection.recv(10000)
            print "here2"
            #print data
            request = pickle.loads(data)
            print >>sys.stderr, 'received "%s"' % request
            print str(request.port_start) + ":" + str(request.port_end) + ":" + str(request.date_today) 
                              
        finally:
            # Clean up the connection
            connection.close()

def server_send():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        
        
        print >>sys.stderr, 'starting up on %s port %s' % client_address
        #sock.bind(client_address)
        # Listen for incoming connections
       # 
        sock.connect(server_address)
        try:
            # Send data
            message = 'sending message to server'
            print >>sys.stderr, '"%s"' % message
            sock.sendall(message)
        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_address = ('localhost', 10006)
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
    thread.start_new_thread(client_listen, ())
#    thread.start_new_thread(server_send, ())
except:
   print "unable to start thread"

while 1:
   pass
