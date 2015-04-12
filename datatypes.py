
class Request():
    def __init__(self, type, ip_addr, ip_subnet, port_start, port_end):
        self.type = type
        self.ip_addr = ip_addr
        self.ip_subnet = ip_subnet
        self.port_start = port_start
        self.port_end = port_end