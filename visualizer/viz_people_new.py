#!/usr/bin/env python

# Title: Viz People
# Description: Reads people from RabbbitMQ and visualizes it
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

### Global variable to store people count
people_count = 0

# Receive messages from UAVs and plot
def callback(ch, method, properties, body):
	global people_count
	#Plot person found
	people_count += 1
	person = json.loads(body.decode('utf-8'))
	plt.scatter(float(person['x_position']),float(person['y_position']))
	
	# Update plot
	if people_count % 10 == 0:
		plt.draw()
		plt.pause(0.01)

if __name__ == '__main__':
	# Draw inital plot
	plt.draw()
	plt.pause(0.01)
	plt.xlim([-300, 300])
	plt.ylim([-300, 300])
	
	# Establish incoming connection from UAVs
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
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
	


