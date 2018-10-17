#!/usr/bin/env python

# Title: UAV client
# Description: Randomly generates peoples poses and sends them to the RabbitMQ server
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import random
import pika
import time
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
uav_id = random.randint(0,100000)

# Sends locations of people found to Rabbit
def publish_to_mq(person):
	print("Found Person: ", person)
	person_to_send = json.dumps(person)
	# Publish message to outgoing exchange
	channel.basic_publish(exchange='people_found',
						routing_key='key_people_found',
						body=person_to_send) 
 
	time.sleep(0.01)

### Randomly generate peoples poses
def gen_poses():
	person = {}
	
	min_x = -200
	while(min_x<200):
		num_people = int(random.uniform(100,200))
		while num_people > 0:
			x = random.uniform(min_x,min_x+10)
			y = random.uniform(-200,200)
			person['x_position'] = x
			person['y_position'] = y
			person['uav_id'] = uav_id
			person['timestamp'] = time.time()
			num_people -= 1
			publish_to_mq(person)
		min_x += 25
		time.sleep(1)

if __name__ == '__main__':
	# Establish outgoing connection to RabbitMQ
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,port=port, credentials=credentials))
	channel = connection.channel()
	channel.exchange_declare(exchange='people_found', exchange_type='direct')
	gen_poses()


