#!/usr/bin/env python

# Title: Clustering service
# Description: Recieves cluster locations and metaclusters them
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import sys
import math
import numpy as np
import random
from sklearn import cluster
import skfuzzy as fuzz
import time
import pika

hostname = '129.114.111.193'
username = "yellow"
password = "test5243"
credentials = pika.PlainCredentials(username, password)

num_boats = 5
poses = []

# Sends locations of metaclusters found to Rabbit
def publish_to_mq(datas):
	entries = ""
	for data in datas:
		entry = str((str(data[0]),str(data[1])))
		entries = entry + ">" + entries
	print(entries)
	# Publish message to outgoing exchange
	channel.basic_publish(exchange='metaclusters_found',
							routing_key='key_metaclusters_found',
							body=entries) 
	# Indicate delivery of message
	print(" [ >> ] Sent %r" % entry)


### Metaclustering function
def cmeans_clustering(data):
		global num_boats
		clusters = poses
		location_array = []
		if(data != []):
				### K-means clustering on Clusters
				k = num_boats
				cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(np.asarray(data).T, k, 2, error=0.005, maxiter=5000, init=None)
				centroids = []
				for pt in cntr:
						centroids.append((pt[0],pt[1])) 

				cluster_membership = np.argmax(u, axis=0)
				labels = u

		return centroids,labels,location_array



# Receive messages from Clustering and publish to Metaclustering
def callback(ch, method, properties, body):
	global poses
	poses_list = []
	poses_temp = body.decode("utf-8")
	for pose in poses_temp.split("\n")[0].split(">"):
		if len(pose.replace("(","").replace(")","").replace("'","").split(",")) == 2:
			x = pose.replace("(","").replace(")","").replace("'","").split(",")[0]
			y = pose.replace("(","").replace(")","").replace("'","").split(",")[1]
			#print(" [x] Received ", x, " " , y)
			if [float(x),float(y)] not in poses:
				poses_list.append([float(x),float(y)])
	poses = poses_list
	centroids,labels,location_array = cmeans_clustering(poses)
	print(centroids)
	publish_to_mq(centroids)

if __name__ == '__main__':
	# Establish outgoing connection to Clustering
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials))
	channel = connection.channel()
	channel.exchange_declare(exchange='metaclusters_found', exchange_type='direct')

	# Establish incoming connection from UAVs
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='clusters_found', exchange_type='direct')
	result_in = channel_in.queue_declare(exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='clusters_found',queue=queue_in_name,routing_key='key_clusters_found')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(callback,queue=queue_in_name,no_ack=False)

	# Begin consuming from UAVs
	channel_in.start_consuming()

