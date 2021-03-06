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
poses = []

# Receive messages from UAVs and publish to Clustering
def callback(ch, method, properties, body):
	global poses
	if "START" in str(body):
		poses = []
	elif "END" in str(body):
		for pose in poses:
			plt.scatter(pose[0],pose[1],c='b',s=30)
		plt.ylim([-300,300])
		plt.xlim([-300,300])
		plt.draw()
		plt.pause(0.001)
	else:
		body_temp = str(body).replace("(","").replace(")","").replace("b","")
		body_temp = body_temp.replace("'","")
		x = float(body_temp.split(',')[0])
		y = float(body_temp.split(',')[1])
		poses.append([x,y])
	#print("Len Poses: ", len(poses))


if __name__ == '__main__':
	# Establish incoming connection from UAVs
	plt.draw()
	plt.pause(0.01)
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
	


