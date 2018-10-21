#!/usr/bin/env python

# Title: Metaclustering service
# Description: Recieves cluster locations and metaclusters them
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import numpy as np
import random
from sklearn import cluster
import skfuzzy as fuzz
import time
import pika
import yaml
import json
import mysql.connector

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

# Sends locations of metaclusters found to Rabbit
def publish_to_mq(metaclusters,num_clusters,time_stamp):
	for metacluster in metaclusters:
		entry = {}
		entry['x_position'] = metacluster[0]
		entry['y_position'] = metacluster[1]
		entry['num_clusters'] = num_clusters
		entry['time_stamp'] = time_stamp
		metacluster_to_send = json.dumps(entry)
		# Publish message to outgoing exchange
		channel.basic_publish(exchange='metaclusters_found',
							routing_key='key_metaclusters_found',
							body=metacluster_to_send) 
		time.sleep(0.01)


### Metaclustering function
def cmeans_clustering(data, num_boats):
		location_array = []
		if(data != []):
				### K-means clustering on Clusters
				k = num_boats
				t0 = time.time()
				cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(np.asarray(data).T, k, 2, error=1.0, maxiter=500, init=None, seed=1)
				print("time to run: ", time.time()-t0)
				centroids = []
				for pt in cntr:
						centroids.append((pt[0],pt[1])) 

				cluster_membership = np.argmax(u, axis=0)
				labels = u

		return centroids,labels,location_array

if __name__ == '__main__':
	# Establish outgoing connection to Clustering
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='metaclusters_found', exchange_type='direct')

	while(1):
		mycursor.execute("SELECT x_position, y_position FROM speed_clusters_found")
		clusters_found = mycursor.fetchall()
		mycursor.execute("SELECT * FROM boat_info")
		num_boats = len(mycursor.fetchall())
		if len(clusters_found) > 0:
			num_clusters = len(clusters_found)
			t0 = time.time()
			metaclusters,labels,location_array = cmeans_clustering(clusters_found, num_boats)
			print("Time to Metacluster: ", time.time()-t0, " Metaclusters Found: ", len(metaclusters))
			publish_to_mq(metaclusters, num_clusters, time.strftime('%Y-%m-%d %H:%M:%S'))
		mydb.commit()

