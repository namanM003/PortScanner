#!/usr/bin/python
from threading import Thread, Lock
from threading import Condition
import time
import random

queue = []
lock = Lock()

condition = Condition()

class Struct1():
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

class Struct2():
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

class Struct3():
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        
class Request():
    def __init__(self, type, time_stamp, ip_addr, ip_subnet, port_start, port_end):
        self.type = type
        self.ip_addr = ip_addr
        self.no_of_ip = ip_subnet
        self.port_start = port_start
        self.port_end = port_end

class ConsumerThread(Thread):
    def run(self):
        global queue
        while True:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
                condition.wait()
                print "Producer added something to queue and notified the consumer"
            request = queue.pop(0)
            print "Consumed", request.ip_addr 
            condition.release()
            time.sleep(1)

class ProducerThread(Thread):
    def run(self):
        nums = range(3)
        global queue
        while True:
            condition.acquire()
            request = Request(1,"120.120.120.120",200,10,20)
            length = len(queue)
            queue.append(request)
            print "Produced", request 
            if length == 0:
              print "Notifying"
              condition.notify()
            condition.release()
            time.sleep(1)
     

ProducerThread().start()
ConsumerThread().start()
