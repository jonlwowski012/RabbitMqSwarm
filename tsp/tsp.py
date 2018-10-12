#!/usr/bin/env python

# Title: TSP service
# Description: Recieves cluster locations and TSPs them
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import time
import sys
import math
import numpy as np
import random
import threading
import pika
from collections import defaultdict
from tsp_solver.greedy import solve_tsp

hostname = '129.114.111.193'
username = "yellow"
password = "test5243"
port="31111"
credentials = pika.PlainCredentials(username, password)

boat_info = []
exchanges_made = []
poses_list = []
connection = None

class BoatInfoThread(threading.Thread):
	def __init__(self, host, topic, *args, **kwargs):
		super(BoatInfoThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic

	# Receive messages from Metaclustering and publish to Auctioning
	def callback_boatinfo(self, ch, method, properties, body):
		global boat_info
		if "START" in str(body):
			boat_info = []
		elif "END" in str(body):
			pass
		else:
			self.boat_info_temp = body.decode("utf-8")
			for boat in self.boat_info_temp.split("\n"):
				self.speed = boat.replace("(","").replace(")","").replace("'","").split(",")[0]
				self.capacity = boat.replace("(","").replace(")","").replace("'","").split(",")[1]
				self.x = boat.replace("(","").replace(")","").replace("'","").split(",")[2]
				self.y = boat.replace("(","").replace(")","").replace("'","").split(",")[3]
				self.boat_id = boat.replace("(","").replace(")","").replace("'","").split(",")[4]
				boat_info.append(int(self.boat_id))
            
	def run(self):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials, port=port))
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange=self.topic, exchange_type='direct')
		self.result = self.channel.queue_declare(exclusive=True)
		self.queue = self.result.method.queue
		self.channel.queue_bind(exchange=self.topic,queue=self.queue,routing_key="key_"+self.topic)

		#Indicate queue readiness
		print(' [*] Waiting for messages. To exit, press CTRL+C')

		self.channel.basic_consume(self.callback_boatinfo,
				      queue=self.queue,
				      no_ack=False)

		self.channel.start_consuming()  


class TSPThread(threading.Thread):
    def __init__(self, host, topic, boat_id, *args, **kwargs):
        super(TSPThread, self).__init__(*args, **kwargs)
        self.host = host
        self.topic = topic
        self.boat_id = boat_id
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials, port=port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='final_path'+'_'+str(self.boat_id), exchange_type='direct')
        
    # Receive messages from Metaclustering and publish to Auctioning
    def callback_clustering(self, ch, method, properties, body):
        global poses_list
        global boat_info
        if 'START' in str(body):
            poses_list=[]
        elif 'END' in str(body):
            print("Len: ", len(poses_list), " Id: ", self.boat_id)
            path = tsp_solver(poses_list)
            self.publish_to_mq(path)
        else:
            poses_temp = body.decode("utf-8")
            x = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[0])
            y = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[1])
            poses_list.append([x,y])

            
    # Sends locations of clusters found to Rabbit
    def publish_to_mq(self,datas):
        entries = ""
        self.channel.basic_publish(exchange='final_path'+'_'+str(self.boat_id),
                                routing_key='key_final_path'+'_'+str(self.boat_id),
                                body="START")
        for data in datas:
            entry = str((str(data[0]),str(data[1])))
            self.channel.basic_publish(exchange='final_path'+'_'+str(self.boat_id),
                                routing_key='key_final_path'+'_'+str(self.boat_id),
                                body=entry)
            time.sleep(0.01)
            #entries = entry + ">" + entries
            # Publish message to outgoing exchange
        self.channel.basic_publish(exchange='final_path'+'_'+str(self.boat_id),
                                routing_key='key_final_path'+'_'+str(self.boat_id),
                                body="END") 
        #print('final_path'+'_'+str(self.boat_id))
        # Indicate delivery of message
        #print(" [ >> ] Sent %r" % entries) 
        
    def run(self):
        #print(self.topic+"_"+str(self.boat_id))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials, port=port))
        channel = connection.channel()
        channel.exchange_declare(exchange=self.topic+"_"+str(self.boat_id), exchange_type='direct')
        result = channel.queue_declare(exclusive=True)
        queue = result.method.queue
        channel.queue_bind(exchange=self.topic+"_"+str(self.boat_id),queue=queue,routing_key="key_"+self.topic+"_"+str(self.boat_id))
        
        #Indicate queue readiness
        print(' [*] Waiting for messages. To exit, press CTRL+C')

        channel.basic_consume(self.callback_clustering,
                              queue=queue,
                              no_ack=False)

        channel.start_consuming()    
        
                
### Dijkstra Class 
class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance

def distance(p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

### Setup TSP Solver
def setup_tsp(clusters):
        global connection
        people_location_array = clusters
        graph_people_locations = Graph()
        number = 1
        people_location_array_current = people_location_array
        #print people_location_array_current
        w, h = len(people_location_array_current)+1, len(people_location_array_current)+1
        cost_mat = [[0 for x in range(w)] for y in range(h)] 
        graph_people_locations.add_node(str(0))
        for i in range(len(people_location_array_current)):
                graph_people_locations.add_node(str(number))
                number = number + 1
        for node in graph_people_locations.nodes:
                if connection is not None:
                        connection.process_data_events()
                for node2 in graph_people_locations.nodes:
                        if connection is not None:
                            connection.process_data_events()
                        if(node != '1' and node2 != '1'):
                                cost = distance((people_location_array_current[int(node)-1][0], people_location_array_current[int(node)-1][1]),
                                                (people_location_array_current[int(node2)-1][0],
                                                people_location_array_current[int(node2)-1][1]))
                        elif node == '1':
                                cost = 0
                        elif node2 == '1':
                                cost = 99999999
                        graph_people_locations.add_edge(node,node2,cost)
                        cost_mat[int(node)][int(node2)]=cost
        return cost_mat


### TSP Solver
def tsp_solver(clusters):
    cost_mat = setup_tsp(clusters)
    path = solve_tsp( cost_mat )
    path_array = [] 
    for index in path:
        path_array.append(clusters[index-1])
    #print(path_array)
    return path_array


if __name__ == '__main__':
    # Establish incoming connection from UAVs
    boat_thread = BoatInfoThread(hostname, 'boat_info')
    boat_thread.start()
    
    threads = []
    while(1):
        for boat in boat_info:
            if boat not in exchanges_made:
                exchanges_made.append(boat)
                threads.append(TSPThread(hostname, 'tsp_info', int(boat)))
                threads[-1].start()
                

