#!/usr/bin/python
import time
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Disable the annoying No Route found warning !
from scapy.all import *
 
#ip = "216.178.46.224"
ip = "8.8.8.8"
#ip ="10.255.42.171"
#ip = "127.0.0.1"
#ip = "123.125.115.164"
closed_ports = 0
open_ports = []
 
def is_up(ip):
    """ Tests if host is up """
    return True
    icmp = IP(dst=ip)/ICMP()
    resp = sr1(icmp, timeout=10)
    if resp == None:
        return False
    else:
        return True
 
def scan_port_fin(ports,ip):
    conf.verb = 0 # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    closed = 0
    open_close_dict = dict()
    closed_list = []
    openp = []
    if is_up(ip):
        print "Host %s is up, start scanning" % ip
        for port in ports:
            src_port = RandShort() # Getting a random port as source port
            p = IP(dst=ip)/TCP(sport=src_port, dport=port, flags='F') # Forging SYN packet
#            print "Sending Packert" + str(p.show())
             
            resp = sr1(p, timeout=10) # Sending packet
            if str(type(resp)) == "<type 'NoneType'>":
                
                openp.append(port)
                print " Port is open " + str(port)
                open_close_dict[port] = True
            elif resp.haslayer(TCP):
                if resp.getlayer(TCP).flags == 0x14:
                    print " Port is closed " + str(port) 
                    closed_list.append(port)
                    open_close_dict[port] = False
                else:
                    print " Came here jhol " + str(port) + " " + str(resp.getlayer(TCP).flags) 
                    closed_list.append(port)
                    open_close_dict[port] = False
        duration = time.time()-start_time
    else:
        for port in ports:
            open_close_dict[port] = "HostDown"
        print "Host %s is Down" % ip

    return open_close_dict

#dict_l = scan_port_fin([70,71,72],ip)
#print str(dict_l)
