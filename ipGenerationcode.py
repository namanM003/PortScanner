from netaddr import IPNetwork
total_list = list()
for ip in IPNetwork('192.0.222.0/23'):
   total_list.append(str(ip))

print str(total_list)                       
