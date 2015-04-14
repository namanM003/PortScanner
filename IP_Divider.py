#! /bin/bash/python/

IP_Net = "192.24.56.78/23"
strings=IP_Net.split('/')
print strings[0]
print strings[1]
strings[1]=int(strings[1])
IP_parts = strings[0].split('.')
for i in range(0, 4):
	IP_parts[i] = int(IP_parts[i])
current_octet = 0
for i in range(0,4):
	if(strings[1]>=8):
		strings[1]=strings[1]-8
#		current_octet = current_octet+1
		continue
	if strings[1] == 0:
		and_op = 0
		print and_op	
		strings[1] = 0
	else:
		z = 8
		and_op = 0
		while(strings[1] != 0):
			and_op = and_op + 2**z
			z = z-1
			strings[1] = strings[1] - 1
		#strings[1]=0		
	IP_parts[i] = IP_parts[i] & and_op
	#print IP_parts[i]
	print  i
	current_octet = current_octet + 1
for i in range(0,4):
	print IP_parts[i]
	
	
