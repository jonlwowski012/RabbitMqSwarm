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
import copy

hostname = '129.114.111.193'
username = "yellow"
password = "test5243"
credentials = pika.PlainCredentials(username, password)

num_boats = 5
clusters = []
clusters_threads = []
final_paths_threads = []
boat_paths = [None]*num_boats

class FinalPathsThread(threading.Thread):
	def __init__(self, host, topic, boat_id, *args, **kwargs):
		super(FinalPathsThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
		self.boat_id = boat_id
		self.start_time = time.time()
		self.end_time = 0.0
		
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_clustering(self, ch, method, properties, body):
		poses_list = []
		poses_temp = body.decode("utf-8")
		for pose in poses_temp.split("\n")[0].split(">"):
			if len(pose.replace("(","").replace(")","").replace("'","").split(",")) == 2:
				x = pose.replace("(","").replace(")","").replace("'","").split(",")[0]
				y = pose.replace("(","").replace(")","").replace("'","").split(",")[1]
				#print(clusters[self.boat_id-1])
				#if [float(x),float(y)] not in poses_list:
				#	#print(" [x] Received ", x, " " , y)
				poses_list.append([float(x),float(y)])

		#print(poses_list)
		if self.end_time == 0.0:
			self.end_time = time.time()
		if len(poses_list) > 2:
			boat_paths[self.boat_id-1]= copy.deepcopy(poses_list)
			print("Time to get paths: ", self.end_time-self.start_time, " Boat ID: ", self.boat_id, "Final Path: ", len(poses_list))
		
	def run(self):
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
		channel = connection.channel()
		channel.exchange_declare(exchange='final_path'+'_'+str(self.boat_id), exchange_type='direct')
		result = channel.queue_declare(exclusive=True)
		queue = result.method.queue
		channel.queue_bind(exchange='final_path'+'_'+str(self.boat_id),queue=queue,routing_key='key_final_path'+'_'+str(self.boat_id))
		#Indicate queue readiness
		print(' [*] Waiting for messages. To exit, press CTRL+C')

		channel.basic_consume(self.callback_clustering,
							  queue=queue,
							  no_ack=False)

		channel.start_consuming()  
		

### Main Service Client for ASV
def viz():
	for i in range(num_boats):
		boat_id = i+1
		final_paths_threads.append(FinalPathsThread(hostname, 'final_path'+"_"+str(boat_id), boat_id))
		final_paths_threads[len(final_paths_threads)-1].start()
	

if __name__ == '__main__':
	colors = ['r','b','g','y','k']
	viz()
	while(1):
		boat_paths_temp = copy.deepcopy(boat_paths)
		print("len boat_paths: ", len(boat_paths_temp))
		for i,boat in enumerate(boat_paths_temp):
			if boat is not None:
				print("len boat ", i, " ", len(boat))
				for j,pose in enumerate(boat):
					if j == 0:
						plt.scatter(pose[0],pose[1], c=colors[i], marker="*", s=50)
					else:
						plt.scatter(pose[0],pose[1], c=colors[i])
					if j < len(boat)-2:
						plt.arrow(boat[j][0],boat[j][1],boat[j+1][0]-boat[j][0],boat[j+1][1]-boat[j][1], fc=colors[i], ec=colors[i])
				
		plt.draw()
		plt.pause(0.01)
		plt.gcf().clear()
		
	


