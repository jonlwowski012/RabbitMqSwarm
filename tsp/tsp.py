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
credentials = pika.PlainCredentials(username, password)

boat_info = []
exchanges_made = []

class BoatInfoThread(threading.Thread):
	def __init__(self, host, topic, *args, **kwargs):
		super(BoatInfoThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
				
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_boatinfo(self, ch, method, properties, body):
		global boat_info
		boat_info_temp = body.decode("utf-8")
		for boat in boat_info_temp.split("\n"):
			boat_id = boat.replace("(","").replace(")","").replace("'","").split(",")[4]
			if int(boat_id) not in boat_info:
				boat_info.append(int(boat_id))
			
	def run(self):
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
		channel = connection.channel()
		channel.exchange_declare(exchange=self.topic, exchange_type='direct')
		result = channel.queue_declare(exclusive=True)
		queue = result.method.queue
		channel.queue_bind(exchange=self.topic,queue=queue,routing_key="key_"+self.topic)
		
		#Indicate queue readiness
		print(' [*] Waiting for messages. To exit, press CTRL+C')

		channel.basic_consume(self.callback_boatinfo,
							  queue=queue,
							  no_ack=False)

		channel.start_consuming()  


class TSPThread(threading.Thread):
	def __init__(self, host, topic, boat_id, *args, **kwargs):
		super(TSPThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
		self.boat_id = boat_id
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange='final_path'+'_'+str(self.boat_id), exchange_type='direct')
		
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_clustering(self, ch, method, properties, body):
		poses_list = []
		poses_temp = body.decode("utf-8")
		for pose in poses_temp.split("\n")[0].split(">"):
			if len(pose.replace("(","").replace(")","").replace("'","").split(",")) == 2:
				x = pose.replace("(","").replace(")","").replace("'","").split(",")[0]
				y = pose.replace("(","").replace(")","").replace("'","").split(",")[1]
				#print(" [x] Received ", x, " " , y)
				if [float(x),float(y)] not in poses_list:
					poses_list.append([float(x),float(y)])
		if len(poses_list) > 0:
			path = tsp_solver(poses_list)
			self.publish_to_mq(path)
			
	# Sends locations of clusters found to Rabbit
	def publish_to_mq(self,datas):
		entries = ""
		for data in datas:
			entry = str((str(data[0]),str(data[1])))
			entries = entry + ">" + entries
			# Publish message to outgoing exchange
		self.channel.basic_publish(exchange='final_path'+'_'+str(self.boat_id),
								routing_key='key_final_path'+'_'+str(self.boat_id),
								body=entries) 
		print('final_path'+'_'+str(self.boat_id))
		# Indicate delivery of message
		#print(" [ >> ] Sent %r" % entries)	
		
	def run(self):
		print(self.topic+"_"+str(self.boat_id))
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
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
                for node2 in graph_people_locations.nodes:
                        if(node != '0' and node2 != '0'):
                                cost = distance((people_location_array_current[int(node)-1][0], people_location_array_current[int(node)-1][1]),
												(people_location_array_current[int(node2)-1][0],
												people_location_array_current[int(node2)-1][1]))
                        else:
                                cost = 9999999
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
	print(path_array)
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
				

