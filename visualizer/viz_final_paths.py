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
boat_paths_temp = [None]*num_boats

class FinalPathsThread(threading.Thread):
	def __init__(self, host, topic, boat_id, *args, **kwargs):
		super(FinalPathsThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
		self.boat_id = boat_id
		self.start_time = time.time()
		self.end_time = time.time()
		
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_clustering(self, ch, method, properties, body):
		if "START" in str(body):
			boat_paths_temp[self.boat_id-1]=[]
		elif "END" in str(body):
			boat_paths[self.boat_id-1] = copy.deepcopy(boat_paths_temp[self.boat_id-1])
			print("Time to get paths: ", self.end_time-self.start_time, " Boat ID: ", self.boat_id)
		else:
			poses_temp = body.decode("utf-8")
			x = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[0])
			y = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[1])
			boat_paths_temp[self.boat_id-1].append([x,y])
		
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
		boat_paths_plot = copy.deepcopy(boat_paths)
		print("len boat_paths: ", len(boat_paths_plot))
		for i,boat in enumerate(boat_paths_plot):
			if boat is not None:
				print("len boat ", i, " ", len(boat))
				for j,pose in enumerate(boat):
					if j == 0:
						plt.scatter(pose[0],pose[1], c=colors[i], marker="*", s=100)
					else:
						plt.scatter(pose[0],pose[1], c=colors[i])
					if j < len(boat)-1:
						plt.arrow(boat[j][0],boat[j][1],boat[j+1][0]-boat[j][0],boat[j+1][1]-boat[j][1], fc=colors[i], ec=colors[i])
				
		plt.draw()
		plt.pause(0.01)
		plt.gcf().clear()
		
	


