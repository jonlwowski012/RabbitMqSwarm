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

class AuctionThread(threading.Thread):
	def __init__(self, host, topic, *args, **kwargs):
		super(AuctionThread, self).__init__(*args, **kwargs)
		self.host = host
		self.topic = topic
		
	# Receive messages from Metaclustering and publish to Auctioning
	def callback_clustering(self, ch, method, properties, body):
		global poses
		if 'START' in str(body):
			poses = []
		elif 'END' in str(body):
			pass
		else:
			poses_temp = body.decode("utf-8")
			x = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[0])
			y = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[1])
			poses.append([x,y])
			
	def run(self):
		global credentials
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
		channel.start_consuming()  
		

### Main Service Client for ASV
def viz():
	# Establish incoming connection from UAVs
	auction_thread = AuctionThread(hostname, 'metaclusters_found')
	auction_thread.start()
	

if __name__ == '__main__':
	colors = ['r','b','g','y','k']
	viz()
	while(1):
		for i,pose in enumerate(poses):
			x = pose[0]
			y = pose[1]
			plt.scatter(float(x),float(y),c=colors[i%len(colors)],s=5)
			circle1=plt.Circle((float(x),float(y)),color=colors[i%len(colors)], radius=60,fill=False)
			fig = plt.gcf()
			ax = fig.gca()
			ax.add_artist(circle1)
			plt.draw()
		plt.pause(1.0)
		plt.gcf().clear()
	


