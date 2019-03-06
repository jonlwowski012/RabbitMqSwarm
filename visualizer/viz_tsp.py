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
import signal
import sys

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
tsp_count = 0
curr_num_tsp = 0
boat_ids = []
curr_time = None
prev_x = None
prev_y = None
prev_id = None
# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global tsp_count, curr_num_tsp, boat_ids, curr_time, prev_x, prev_y, prev_id
	tsp_info = json.loads(body.decode('utf-8'))
	print(tsp_info['boat_id'])
	if tsp_info['boat_id'] not in boat_ids:
		boat_ids.append(tsp_info['boat_id'])

	fig = plt.gcf()
	ax = fig.gca()
	if prev_id == tsp_info['boat_id']:
		plt.arrow(prev_x,prev_y,float(tsp_info['x_position'])-prev_x,float(tsp_info['y_position'])-prev_y,
				 fc=colors[boat_ids.index(tsp_info['boat_id'])%len(colors)], ec=colors[boat_ids.index(tsp_info['boat_id'])%len(colors)], label=str(tsp_info['boat_id']))
	
	plt.scatter(float(tsp_info['x_position']),float(tsp_info['y_position']),c=colors[boat_ids.index(tsp_info['boat_id'])%len(colors)],s=5)
	prev_x = float(tsp_info['x_position'])
	prev_y = float(tsp_info['y_position'])
	prev_id = tsp_info['boat_id']
	plt.ylim([-300,300])
	plt.xlim([-300,300])
	print(curr_time, tsp_info['time_stamp'])
	if curr_time != tsp_info['time_stamp']:
		prev_id = None
		curr_time = tsp_info['time_stamp']
		plt.draw()
		plt.legend()
		plt.pause(0.1)
		fig.clear()

def close_pika(signal, frame):
    print('Closing Pika Connection')
    connection.close()
    sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, close_pika)
	# Establish incoming connection from Speed Clusters
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='tsp_info', exchange_type='direct')
	result_in = channel_in.queue_declare(exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='tsp_info',queue=queue_in_name,routing_key='key_tsp_info')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(callback,queue=queue_in_name,no_ack=False)

	# Begin consuming from UAVs
	plt.draw()
	plt.legend()
	plt.pause(0.01)
	channel_in.start_consuming()
	


