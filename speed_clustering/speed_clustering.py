#!/usr/bin/env python

# Title: Speed Clustering
# Description: Clusters the people found by the UAVs quickly
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio

#########          Libraries         ###################
import random
import pika
import time
import yaml
import json
import numpy as np
from sklearn import cluster
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

connection = None

# Parralel k-means clustering
def clustering(poses):
	t0 = time.time()
	global connection, connection_in
	location_array = poses
	flag = False
	min_inertia = 100000
	k = 1
	### while the average cluster radius is greater than 10m
	while((min_inertia/len(location_array))>= 20 or flag == False):
		### Calculate Clusters
		kmeans = cluster.MiniBatchKMeans(init='k-means++', n_init=10, n_clusters=k, random_state=1, tol=1.0, max_no_improvement=5, reassignment_ratio=0.001, max_iter=100)
		kmeans.fit(location_array)
		min_inertia = kmeans.inertia_
		flag = True
		k+= max(int(k/5),1)
	### Calculate Clusters
	centroids_temp = kmeans.cluster_centers_
	labels = kmeans.labels_
	inertia = kmeans.inertia_

	### Calculate Radius for Cluster Msg
	radius = inertia/len(location_array)

	### Calculate Centroids of Clusters
	centroids = centroids_temp

	### Get Labels for all people's locations
	labels = kmeans.labels_
	#print(centroids)
	return centroids

# Sends locations of clusters found to Rabbit
def publish_to_mq(clusters, num_people, time_stamp):
	for cluster in clusters:
		entry = {}
		entry['x_position'] = cluster[0]
		entry['y_position'] = cluster[1]
		entry['num_people'] = num_people
		entry['time_stamp'] = time_stamp
		cluster_to_send = json.dumps(entry)
		# Publish message to outgoing exchange
		channel.basic_publish(exchange='speed_clusters_found',
							routing_key='key_speed_clusters_found',
							body=cluster_to_send) 
		time.sleep(0.01)

if __name__ == '__main__':
	# Establish outgoing connection to Speed Clustering
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='speed_clusters_found', exchange_type='direct')

	while(1):
		mycursor.execute("SELECT x_position, y_position FROM people_found")
		people_found = mycursor.fetchall()
		if len(people_found) > 0 and len(people_found)%10 == 0:
			num_people = len(people_found)
			t0 = time.time()
			clusters = clustering(people_found)
			print("Time to Cluster: ", time.time()-t0, " Clusters Found: ", len(clusters))
			publish_to_mq(clusters, num_people, time.strftime('%Y-%m-%d %H:%M:%S'))
		mydb.commit()