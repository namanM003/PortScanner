class Request():
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
    
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end, random, date_today):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.random = random
        self.date = date
        
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end, date):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.date = date
        
        
class Response():
    def __init__(self, type, date, ip_addr, ip_subnet, port_start, port_end, port_map):
        self.type = type
        self.date = date
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end
        self.port_map = port_map
