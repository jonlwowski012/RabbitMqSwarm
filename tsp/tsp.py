#!/usr/bin/env python

# Title: TSP service
# Description: Recieves cluster locations and TSPs them
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import numpy as np
import random
import time
import pika
import yaml
import json
import mysql.connector
import copy
import math
from collections import defaultdict
from tsp_solver.greedy import solve_tsp
import signal
import sys

### Read config parameters for mysql
with open('config.yaml') as f:
	config = yaml.safe_load(f)
	host = config['mysql_hostname']
	username = config['mysql_username']
	password = config['mysql_password']
	database = config['mysql_database']
	port = config['mysql_port']

### Connect to mysql database and get cursor
mydb = mysql.connector.connect(
  host=host,
  user=username,
  passwd=password,
  database=database,
  port = port
)
mycursor = mydb.cursor()

### Read config parameters for RabbitMQ
with open('config.yaml') as f:
	config = yaml.safe_load(f)
	hostname = config['hostname']
	username = config['username']
	password = config['password']
	port = config['port']
credentials = pika.PlainCredentials(username, password) 
		   
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
		print(people_location_array_current)
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
	
# Sends tsp info to Rabbit
def publish_to_mq(tsp_info, boat_id):
	time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
	for pose_index,pose in enumerate(tsp_info):
		entry = {}
		entry['seq_id'] = pose_index
		entry['x_position'] = pose[0]
		entry['y_position'] = pose[1]
		entry['boat_id'] = boat_id
		entry['time_stamp'] = time_stamp
		assignment_to_send = json.dumps(entry)
		channel.basic_publish(exchange='tsp_info',
						routing_key='key_tsp_info',
						body=assignment_to_send)
		#print(entry)
		time.sleep(0.01)


def close_pika(signal, frame):
    print('Closing Pika Connection')
    connection.close()
    sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, close_pika)

	# Establish outgoing connection to Auctioning
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat=600, blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='tsp_info', exchange_type='direct')
	len_auction = {}
	while(1):
		mycursor.execute("SELECT * FROM boat_info")
		boat_info = mycursor.fetchall()
		for boat_idx, boat in enumerate(boat_info):
			boat_id = boat[5]
			mycursor.execute("SELECT x_position, y_position, boat_id FROM auction_info WHERE boat_id=" + str(boat_id) + " AND time_stamp = (SELECT MAX(time_stamp) FROM auction_info);")
			auction_info = mycursor.fetchall()
			boat_pose =  [boat[1],boat[2]]
			if str(boat_id) not in len_auction:
				len_auction[str(boat_id)] = 0
			if auction_info != [] and len(auction_info) > len_auction[str(boat_id)]:
				len_auction[str(boat_id)] = len(auction_info)
				tsp_paths = np.array(auction_info)[:,0:2]
				tsp_paths = np.insert(tsp_paths, 0, boat_pose, axis=0)
				final_path = tsp_solver(np.array(auction_info)[:,0:2])
				publish_to_mq(final_path, boat_id)
			mydb.commit()
		mydb.commit()

