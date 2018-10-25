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
auction_count = 0
curr_num_auction = 0
boat_ids = []
curr_time = None

# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global auction_count, curr_num_auction, boat_ids, curr_time

	auction_info = json.loads(body.decode('utf-8'))
	if auction_info['boat_id'] not in boat_ids:
		boat_ids.append(auction_info['boat_id'])

	fig = plt.gcf()
	ax = fig.gca()
	plt.scatter(float(auction_info['x_position']),float(auction_info['y_position']),c=colors[boat_ids.index(auction_info['boat_id'])%len(colors)],s=5)
	circle1=plt.Circle((float(auction_info['x_position']),float(auction_info['y_position'])),color=colors[boat_ids.index(auction_info['boat_id'])%len(colors)], radius=20,fill=False)
	plt.ylim([-300,300])
	plt.xlim([-300,300])
	ax.add_artist(circle1)
	print(curr_time, auction_info['time_stamp'])
	if curr_time != auction_info['time_stamp']:
		curr_time = auction_info['time_stamp']
		plt.draw()
		plt.pause(0.1)
		fig.clear()

if __name__ == '__main__':
	# Establish incoming connection from Speed Clusters
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='auctioning_info', exchange_type='direct')
	result_in = channel_in.queue_declare(exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='auctioning_info',queue=queue_in_name,routing_key='key_auctioning_info')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(callback,queue=queue_in_name,no_ack=False)

	# Begin consuming from UAVs
	plt.draw()
	plt.pause(0.01)
	channel_in.start_consuming()
	


