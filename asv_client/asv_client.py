#!/usr/bin/env python

# Title: ASV client
# Description: Randomly generates ASV
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import random
import pika
import time
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
boat_id = random.randint(0,100000)


		
# Sends locations of people found to Rabbit
def publish_to_mq(x,y,speed,capacity, boat_id):
	boat = {}
	boat['x_position'] = x
	boat['y_position'] = y
	boat['speed'] = speed
	boat['capacity'] = capacity
	boat['boat_id'] = boat_id
	boat['time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
	boat_to_send = json.dumps(boat)
	# Publish message to outgoing exchange
	channel.basic_publish(exchange='boat_info',
			            routing_key='key_boat_info',
			            body=boat_to_send) 

def close_pika(signal, frame):
    print('Closing Pika Connection')
    connection.close()
    sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, close_pika)
	# Establish outgoing connection to RabbitMQ
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
	channel = connection.channel()
	channel.exchange_declare(exchange='boat_info', exchange_type='direct')
	
	boat_speed = random.uniform(.2,1.0)
	boat_capacity = random.uniform(10,150)
	boat_location_x = random.uniform(-300,-250)
	boat_location_y = random.uniform(-200,200)
	
	publish_to_mq(boat_location_x, boat_location_y, boat_speed, boat_capacity, boat_id)


