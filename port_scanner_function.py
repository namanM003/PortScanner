#!/usr/bin/python
import time
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Disable the annoying No Route found warning !
from scapy.all import *
 
#ip = "216.178.46.224"
#ip = "127.0.0.1"
ip = "173.194.123.83"

closed_ports = 0
open_ports = []
 
def is_up(ip):
    """ Tests if host is up """
    icmp = IP(dst=ip)/ICMP()
    resp = sr1(icmp, timeout=10)
    if resp == None:
        return False
    else:
        return True
 
def scan_port_ack(port_list,ip):
    conf.verb = 0 # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    closed = 0
    dict_response = dict()
    open_dict = []
    if is_up(ip):
      print "Host %s is up, start scanning" % ip
      for port in port_list:
            src_port = RandShort() # Getting a random port as source port
            p = IP(dst=ip)/TCP(sport=src_port, dport=port, flags='S') # Forging SYN packet
            resp = sr1(p, timeout=2) # Sending packet
            if str(type(resp)) == "<type 'NoneType'>":
                closed += 1
                dict_response[port] = False
                print " Port is closed " + str(port)
            elif resp.haslayer(TCP):
                if resp.getlayer(TCP).flags == 0x12:
                    send_rst = sr(IP(dst=ip)/TCP(sport=src_port, dport=port, flags='AR'), timeout=1)
                    dict_response[port] = True
                elif resp.getlayer(TCP).flags == 0x14:
                    print " Here for port " + str(port)
                    closed += 1
                    dict_response[port] = False
                else:
                    print " Came here " + str(port) 
                    dict_response[port] = False
      duration = time.time()-start_time
      print "%s Scan Completed in %fs" % (ip, duration)
      print "Scan Complete : for the ports with results" + str(dict_response)
    else:
        print "Host %s is Down" % ip
       
    return dict_response            
#resp = scan_port_ack([1,2,3,80,82,83,443],ip)
#print "Ports :  " + str(resp)

