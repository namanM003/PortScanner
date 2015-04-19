#!/usr/bin/env python

import sys
import socket
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Disable the annoying No Route found warning !  
from scapy.all import *
#ip = "216.178.46.224"
ip = "74.125.141.106"
def is_up(ip):
    """ Tests if host is up """
    icmp = IP(dst=ip)/ICMP()
    resp = sr1(icmp, timeout=10)
    if resp == None:
        return False
    else:
        return True

def scan_port_connect(port_list,ip):
       	 open_close_dict = dict()
         if is_up(ip):
	    print "Host %s is up, start scanning" % ip
            
	    try: 
	 	    for port in port_list:
		
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(2)
			result = sock.connect_ex((ip, port))

			if result == 0:
			    print "Port " + str(port) +" is Open"
		            open_close_dict[port] = "yes"
			else :
			    print "Port " + str(port) +" is Closed"
		            open_close_dict[port] = "no"
		 	sock.close()
            except:
	          print "Error"

            print "Scan Complete : for the ports with results" + str(open_close_dict)
         else:
              for port in ports:
                open_close_dict[port] = "HostDown"
              print "Host %s is down " % ip
         return open_close_dict

#resp = scan_port_connect([1,2,3],ip)
#print "Ports :  " + str(resp)

	
	







