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
from mpi4py import MPI
from sklearn import cluster
import time

### MPI Functions   ####
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

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
	global connection, connection_in
	location_array = poses
	location_array = comm.bcast(location_array, root=0)
	flag = False
	min_inertia = 100000
	ks = list(range(1,size+1))
	### while the average cluster radius is greater than 10m
	while((min_inertia/len(location_array))>= 20 or flag == False):
		connection.process_data_events()
		connection_in.process_data_events()
		ks_copy = list(ks)
		data = comm.scatter(ks_copy, root=0)
		### Calculate Clusters
		kmeans = cluster.KMeans(init='k-means++', n_init=10, n_clusters=int(data), random_state=1)
		kmeans.fit(location_array)
		inertia = kmeans.inertia_
		min_inertia = comm.allreduce(inertia, op=MPI.MIN)
		inertia = min_inertia
		flag = True
		for index_k in range(len(ks)):
			ks[index_k] += 1
		#ks = [x+1 for x in ks]

	if rank == 0:
		### Calculate Clusters
		kmeans = cluster.KMeans(init='k-means++', n_init=10, n_clusters=int(data), random_state=1)
		kmeans.fit(location_array)
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
def publish_to_mq(datas):
	entries = ""
	channel.basic_publish(exchange='clusters_found',
							routing_key='key_clusters_found',
							body="START") 
	for data in datas:
		entry = str((str(data[0]),str(data[1])))
		#entries = entry + ">" + entries
		# Publish message to outgoing exchange
		channel.basic_publish(exchange='clusters_found',
							routing_key='key_clusters_found',
							body=entry) 
		time.sleep(0.01)
	channel.basic_publish(exchange='clusters_found',
							routing_key='key_clusters_found',
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
	if rank == 0:
		# Establish outgoing connection to Clustering
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
		channel = connection.channel()
		channel.exchange_declare(exchange='clusters_found', exchange_type='direct')

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
	else:
		while(1):
			flag = False
			min_inertia = 100000
			location_array = [0]
			ks = range(1,size+1)
			data = [1]
			location_array = comm.bcast(location_array, root=0)

		        ### while the average cluster radius is greater than 10m
			while((min_inertia/len(location_array))>= 20 or flag == False):
				ks_copy = list(ks)
				data = comm.scatter(ks_copy, root=0)
				### Calculate Clusters
				kmeans = cluster.KMeans(init='k-means++', n_init=10, n_clusters=int(data), random_state=1)
				kmeans.fit(location_array)
				inertia = kmeans.inertia_
				min_inertia = comm.allreduce(inertia, op=MPI.MIN)
				flag = True
				ks = [x+1 for x in ks]


