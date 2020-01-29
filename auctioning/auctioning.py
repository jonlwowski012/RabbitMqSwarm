#!/usr/bin/env python

# Title: Auction service
# Description: Recieves metacluster locations and auctions them to the ASVs
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import numpy as np
import random
import time
from datetime import datetime
import pika
import yaml
import json
import mysql.connector
import copy
import math
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
		
### Euclidean Distance
def distance(p0, p1):
	return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

### Call Clustering Service
def auctioning(auction_info, boat_info, num_boats, clusters_info):
		clusters_auc_pub = []
		boats = range(num_boats)     
		assignments = [0]*num_boats
		boat_info_temp = copy.deepcopy(np.asarray(boat_info))

		### Perform Auction Algorithm
		for metacluster in auction_info:
				if connection is not None:
					connection.process_data_events()
				min_value = 999999
				min_index = 0
				for index in boats:
						meta_pose = (metacluster[0], metacluster[1])
						#print(boat_info,index)
						boat_pose = (boat_info_temp[index][1],boat_info_temp[index][2])
						if abs(distance(meta_pose,boat_pose)) < min_value:
								min_value = abs(distance(meta_pose,boat_pose))
								min_index = index
				assignments[min_index] = meta_pose
				boat_info_temp[min_index][2] = 9999999999

		### Calculate which clusters are in the asv assigned metacluster
		for boat in boats:
				clusters_auc = []
				metacluster = assignments[boat]
				for cluster in clusters_info:
						min_dist = 999999
						min_index = 0
						for index,metacluster in enumerate(auction_info):
								meta_pose = (metacluster[0], metacluster[1])
								cluster_pose = (cluster[0], cluster[1])
								if abs(distance(meta_pose,cluster_pose)) < min_dist:
										min_dist = abs(distance(meta_pose,cluster_pose))
										min_index = index
						if auction_info[min_index][0] == assignments[boat][0] and auction_info[min_index][1] == assignments[boat][1]:
								clusters_auc.append(cluster)
				#print("Boat: ", boat, "Clusters: ", clusters_auc)
				colors = ['r','b','g','y','k']
				if len(clusters_auc) > 0:
					clusters_auc_pub.append(clusters_auc)
		return clusters_auc_pub

# Sends auction info to Rabbit
def publish_to_mq(auction_info, boat_info):
	time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
	for assign_index,assignment in enumerate(auction_info):
		for pose_index, pose in enumerate(assignment):
			entry = {}
			entry['x_position'] = pose[0]
			entry['y_position'] = pose[1]
			entry['boat_id'] = boat_info[assign_index][5]
			entry['time_stamp'] = time_stamp
			assignment_to_send = json.dumps(entry)
			channel.basic_publish(exchange='auctioning_info',
							routing_key='key_auctioning_info',
							body=assignment_to_send)
			print(entry)
			time.sleep(0.01)

def close_pika(signal, frame):
    print('Closing Pika Connection')
    connection.close()
    sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, close_pika)
	# Establish outgoing connection to Auctioning
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port,  blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='auctioning_info', exchange_type='direct')
	curr_time = None
	while(1):
		mycursor.execute("SELECT x_position, y_position, people_in_metacluster, time_stamp FROM metaclusters_found WHERE time_stamp = (SELECT MAX(time_stamp) FROM metaclusters_found)")
		metaclusters_found = mycursor.fetchall()
		mycursor.execute("SELECT * FROM boat_info")
		boat_info = mycursor.fetchall()
		num_boats = len(boat_info)
		mycursor.execute("SELECT x_position, y_position, people_in_cluster FROM speed_clusters_found WHERE time_stamp = (SELECT MAX(time_stamp) FROM speed_clusters_found)")
		clusters_found = mycursor.fetchall()
		if len(metaclusters_found) >= num_boats and num_boats > 0:
			print(metaclusters_found[0][3] != curr_time)
			if metaclusters_found[0][3] != curr_time:
				curr_time = metaclusters_found[0][3]
				auction_info = auctioning(metaclusters_found, boat_info, num_boats, clusters_found)
				publish_to_mq(auction_info,boat_info)
		mydb.commit()
	


