#!/usr/bin/env python

# Title: Map builder service
# Description: Recieves people locations from the UAV
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import sys
import math
import numpy as np
import random
import pika
from sklearn import cluster
import time

hostname = '129.114.111.193'
username = "yellow"
password = "test5243"
port="31111"
credentials = pika.PlainCredentials(username, password)
poses = []
prev_poses_len = 0
connection = None
connection_in = None

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
		connection.process_data_events()
		connection_in.process_data_events()
		### Calculate Clusters
		kmeans = cluster.MiniBatchKMeans(init='k-means++', n_init=10, n_clusters=k, random_state=1, tol=1.0, max_no_improvement=5, reassignment_ratio=0.001, max_iter=100)
		kmeans.fit(location_array)
		min_inertia = kmeans.inertia_
		print(k, min_inertia/len(location_array))
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
	print("Time to Cluster: ", time.time()-t0) 
	#print(centroids)
	return centroids

# Sends locations of clusters found to Rabbit
def publish_to_mq(datas):
	entries = ""
	channel.basic_publish(exchange='speed_clusters_found',
							routing_key='key_speed_clusters_found',
							body="START") 
	for data in datas:
		entry = str((str(data[0]),str(data[1])))
		#entries = entry + ">" + entries
		# Publish message to outgoing exchange
		channel.basic_publish(exchange='speed_clusters_found',
							routing_key='key_speed_clusters_found',
							body=entry) 
		time.sleep(0.01)
	channel.basic_publish(exchange='speed_clusters_found',
							routing_key='key_speed_clusters_found',
							body="END")
	# Indicate delivery of message
	#print(" [ >> ] Sent %r" % entries)


# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global poses, prev_poses_len
	if "START" in str(body):
		poses = []
	elif "END" in str(body):
		#print("Len Poses: ", len(poses))
		print("Clustering with len: ", len(poses))
		centroids = clustering(poses)
		publish_to_mq(centroids)
		prev_poses_len = len(poses)
	else:
		body_temp = str(body).replace("(","").replace(")","").replace("b","")
		body_temp = body_temp.replace("'","")
		x = float(body_temp.split(',')[0])
		y = float(body_temp.split(',')[1])
		#print(" [x] Received ", x, " " , y)
		if [x,y] not in poses:
			poses.append([x,y])


if __name__ == '__main__':
	# Establish outgoing connection to Clustering
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
	channel = connection.channel()
	channel.exchange_declare(exchange='speed_clusters_found', exchange_type='direct')

	# Establish incoming connection from UAVs
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port,heartbeat_interval=65000,blocked_connection_timeout=600000))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='people_found', exchange_type='direct')
	result_in = channel_in.queue_declare(exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='people_found',queue=queue_in_name,routing_key='key_people_found')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(callback,queue=queue_in_name,no_ack=False)

	# Begin consuming from UAVs
	channel_in.start_consuming()


