class Request():
    
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end ,random, date_today,port_scanning_mode,date_only):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.random = random
        self.date_today = date_today
	self.date_only = date_only
	#self.port_list = port_list
        self.port_scanning_mode = port_scanning_mode
        
class ClientRequest():

    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end ,port_list, date_today,port_scanning_mode,date_only):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.port_list = port_list
        self.date_today = date_today
        #self.port_list = port_list
        self.port_scanning_mode = port_scanning_mode
        self.date_only = date_only
class Response():
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end, port_list, date_today, result_dict,date_only):
        self.type = type
        self.date_today = date_today
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.port_list = port_list
	self.result_dict = result_dict
	self.date_only = date_only
