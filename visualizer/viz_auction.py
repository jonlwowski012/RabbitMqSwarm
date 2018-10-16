#!/usr/bin/env python

# Title: UAV client
# Description: Randomly generates peoples poses and sends them to the RabbitMQ server
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import sys
import math
import numpy as np
import random
import pika
import threading
import time
import matplotlib.pyplot as plt

hostname = '129.114.111.193'
username = "yellow"
password = "test5243"
port="31111"
credentials = pika.PlainCredentials(username, password)

num_boats = 5
poses = []
clusters = []
clusters_temp = []
clusters_threads = []

class ClustersThread(threading.Thread):
	def __init__(self, host, topic, boat_id, *args, **kwargs):
		super(ClustersThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
		self.boat_id = boat_id
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials, port=port))
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange='tsp_info'+'_'+str(self.boat_id), exchange_type='direct')
		
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_clustering(self, ch, method, properties, body):
		global clusters, clusters_temp
		if 'START' in str(body):
			clusters_temp[self.boat_id-1] = []
		elif 'END' in str(body):
			clusters[self.boat_id-1] = clusters_temp[self.boat_id-1]
		else:
			poses_temp = body.decode("utf-8")
			x = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[0])
			y = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[1])
			clusters_temp[self.boat_id-1].append([x,y])
		
	def run(self):
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials, port=port))
		channel = connection.channel()
		channel.exchange_declare(exchange=self.topic, exchange_type='direct')
		result = channel.queue_declare(exclusive=True)
		queue = result.method.queue
		channel.queue_bind(exchange=self.topic,queue=queue,routing_key="key_"+self.topic)
		
		#Indicate queue readiness
		print(' [*] Waiting for messages. To exit, press CTRL+C')

		channel.basic_consume(self.callback_clustering,
							  queue=queue,
							  no_ack=False)

		channel.start_consuming()   
		

### Main Service Client for ASV
def viz():
	# Establish incoming connection from UAVs
	for i in range(num_boats):
		clusters.append([])
		clusters_temp.append([])
		clusters_threads.append(ClustersThread(hostname, 'auctioning'+"_"+str(i+1), i+1))
		clusters_threads[len(clusters_threads)-1].start()
	

if __name__ == '__main__':
	colors = ['r','b','g','y','k']
	viz()
	while(1):
		for j,boat in enumerate(clusters):
			print(j , len(boat))
			for i,pose in enumerate(boat):
				x = pose[0]
				y = pose[1]
				plt.scatter(float(x),float(y),c=colors[j%len(colors)],s=5)
				circle1=plt.Circle((float(x),float(y)),color=colors[j%len(colors)], radius=10,fill=False)
				fig = plt.gcf()
				ax = fig.gca()
				ax.add_artist(circle1)
		plt.ylim([-300,300])
		plt.xlim([-300,300])
		plt.draw()
		plt.pause(1.0)
		plt.gcf().clear()
	


