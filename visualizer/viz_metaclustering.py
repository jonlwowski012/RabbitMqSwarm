#!/usr/bin/env python

# Title: UAV client
# Description: Randomly generates peoples poses and sends them to the RabbitMQ server
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import numpy as np
import random
import pika
import time
import matplotlib.pyplot as plt
import yaml
import json

### Read config parameters for RabbitMQ
with open('config.yaml') as f:
	config = yaml.safe_load(f)
	hostname = config['hostname']
	username = config['username']
	password = config['password']
	port = config['port']
credentials = pika.PlainCredentials(username, password)

connection = None

colors = ['b','g','y','k','c','r']
metaclusters_count = 0
curr_num_clusters = 0

# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global metaclusters_count, curr_num_clusters
	fig = plt.gcf()
	ax = fig.gca()
	#Plot clusters found
	metaclusters_count += 1
	metacluster = json.loads(body.decode('utf-8'))
	print(metacluster['num_clusters'],curr_num_clusters)
	if curr_num_clusters + 10 < metacluster['num_clusters']:
		plt.scatter(float(metacluster['x_position']),float(metacluster['y_position']),c=colors[metaclusters_count%len(colors)],s=5)
		circle1=plt.Circle((float(metacluster['x_position']),float(metacluster['y_position'])),color=colors[metaclusters_count%len(colors)], radius=100,fill=False)
		plt.ylim([-300,300])
		plt.xlim([-300,300])
		ax.add_artist(circle1)
		curr_num_clusters = metacluster['num_clusters']
		plt.draw()
		plt.pause(0.1)
		fig.clear()
	elif curr_num_clusters == metacluster['num_clusters']:
		plt.scatter(float(metacluster['x_position']),float(metacluster['y_position']),c=colors[metaclusters_count%len(colors)],s=5)
		circle1=plt.Circle((float(metacluster['x_position']),float(metacluster['y_position'])),color=colors[metaclusters_count%len(colors)], radius=100,fill=False)
		plt.ylim([-300,300])
		plt.xlim([-300,300])
		ax.add_artist(circle1)

if __name__ == '__main__':
	# Establish incoming connection from Speed Clusters
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='metaclusters_found', exchange_type='direct')
	result_in = channel_in.queue_declare(exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='metaclusters_found',queue=queue_in_name,routing_key='key_metaclusters_found')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(callback,queue=queue_in_name,no_ack=False)

	# Begin consuming from UAVs
	plt.draw()
	plt.pause(0.01)
	channel_in.start_consuming()
	


