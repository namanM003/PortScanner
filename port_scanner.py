#!/usr/bin/python
import time
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Disable the annoying No Route found warning !
from scapy.all import *
 
ip = "216.178.46.224"
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
 
if __name__ == '__main__':
    conf.verb = 0 # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    ports = range(78, 1024)
    closed = 0
    openp = []
    if is_up(ip):
        print "Host %s is up, start scanning" % ip
        for port in ports:
            src_port = RandShort() # Getting a random port as source port
            p = IP(dst=ip)/TCP(sport=src_port, dport=port, flags='S') # Forging SYN packet
            resp = sr1(p, timeout=2) # Sending packet
            if str(type(resp)) == "<type 'NoneType'>":
                closed += 1
                print " Port is closed " + str(port)
            elif resp.haslayer(TCP):
                if resp.getlayer(TCP).flags == 0x12:
                    send_rst = sr(IP(dst=ip)/TCP(sport=src_port, dport=port, flags='AR'), timeout=1)
                    print " Port is open " + str(port) 
                    openp.append(port)
                elif resp.getlayer(TCP).flags == 0x14:
                    closed += 1
        duration = time.time()-start_time
        print "%s Scan Completed in %fs" % (ip, duration)
        if len(openp) != 0:
            for opp in openp:
                print "%d open" % pop
        print "%d closed ports in %d total port scanned" % (closed, len(ports))
    else:
        print "Host %s is Down" % ip
