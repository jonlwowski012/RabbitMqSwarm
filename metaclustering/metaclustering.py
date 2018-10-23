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
def publish_to_mq(metaclusters, labels, clusters_found, num_clusters,time_stamp):
	for index,metacluster in enumerate(metaclusters):
		people_in_metacluster = 0
		for index2,label in enumerate(labels):
			if label == index:
				people_in_metacluster += clusters_found[index2][2]
		entry = {}
		entry['x_position'] = metacluster[0]
		entry['y_position'] = metacluster[1]
		entry['people_in_metacluster'] = people_in_metacluster
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
				kmeans = cluster.KMeans(init='k-means++', n_init=10, n_clusters=k, random_state=1)
				print(np.asarray(data).shape)
				kmeans.fit(np.asarray(data))
				centroids_temp = kmeans.cluster_centers_
				labels = kmeans.labels_
				inertia = kmeans.inertia_

				### Calculate Radius for Cluster Msg
				radius = inertia/len(data)

				### Calculate Centroids of Clusters
				centroids = centroids_temp

				### Get Labels for all people's locations
				labels = kmeans.labels_ 

		return centroids,labels,location_array

if __name__ == '__main__':
	# Establish outgoing connection to Clustering
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='metaclusters_found', exchange_type='direct')

	while(1):
		mycursor.execute("SELECT x_position, y_position, people_in_cluster FROM speed_clusters_found WHERE time_stamp = (SELECT MAX(time_stamp) FROM speed_clusters_found)")
		clusters_found = mycursor.fetchall()
		mycursor.execute("SELECT * FROM boat_info")
		num_boats = len(mycursor.fetchall())
		print(num_boats)
		if len(clusters_found) > num_boats and num_boats > 0:
			num_clusters = len(clusters_found)
			t0 = time.time()
			metaclusters,labels,location_array = cmeans_clustering(np.array(clusters_found)[:,0:2], num_boats)
			print("Time to Metacluster: ", time.time()-t0, " Metaclusters Found: ", len(metaclusters))
			publish_to_mq(metaclusters, labels, clusters_found, num_clusters, time.strftime('%Y-%m-%d %H:%M:%S'))
		mydb.commit()

