#!/usr/bin/env python
import socket  
import sys  
import os  
#grab the banner  
def grab_banner(ip_address,port):  
	 
	   s=socket.socket()  
           s.settimeout(2)
 	   s.connect_ex((ip_address,port))  
	   banner = s.recv(1024)  
	   print ip_address + ':' + banner  
  
	   return  
def checkVulns(banner):  
	if len(sys.argv) >=2:  
	   filename = sys.argv[1]  
	   for line in filename.readlines():  
		line = line.strip('\n')  
		if banner in line:  
		     print "%s is vulnerable" %banner  
		else:  
		     print "%s is not vulnerable"  
def main():  
	portList = [80,110,443]  

	for port in portList:  
		ip_address = '216.178.46.224' 
		grab_banner(ip_address,port)  
if __name__ == '__main__':  
 main() 
