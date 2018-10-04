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
credentials = pika.PlainCredentials(username, password)
poses = []
colors = ['b','g','y','k','c','r']
i = 0

# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global poses, i
	if 'START' in str(body):
		poses = []
	elif 'END' in str(body):
		plt.gcf().clear()
	else:
		poses_temp = body.decode("utf-8")
		x = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[0])
		y = float(poses_temp.replace("(","").replace(")","").replace("'","").split(",")[1])
		plt.scatter(float(x),float(y),c=colors[i%len(colors)],s=5)
		circle1=plt.Circle((float(x),float(y)),color=colors[i%len(colors)], radius=20,fill=False)
		fig = plt.gcf()
		ax = fig.gca()
		ax.add_artist(circle1)
		plt.draw()
		plt.pause(0.01)
		i += 1

if __name__ == '__main__':
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
	plt.draw()
	plt.pause(0.01)
	channel_in.start_consuming()
	


