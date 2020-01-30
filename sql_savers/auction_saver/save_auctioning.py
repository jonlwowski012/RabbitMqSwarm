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
import yaml
import json
import mysql.connector


### Read config parameters for mysql
with open('config.yaml') as f:
	config = yaml.safe_load(f)
	host = config['mysql_hostname']
	username = config['mysql_username']
	password = config['mysql_password']
	database = config['mysql_database']
	port = config['mysql_port']

### Connect to mysql database and get cursor
mydb = mysql.connector.connect(
  host=host,
  user=username,
  passwd=password,
  database=database,
  port = port
)
mycursor = mydb.cursor()

### Clear table for restart
sql = "TRUNCATE TABLE auction_info"
mycursor.execute(sql)
mydb.commit()


### Read config parameters for RabbitMQ
with open('config.yaml') as f:
	config = yaml.safe_load(f)
	hostname = config['hostname']
	username = config['username']
	password = config['password']
	port = config['port']
credentials = pika.PlainCredentials(username, password)


### Global variable to store people count
auctions_count = 0

# Receive messages from UAVs and plot
def callback(ch, method, properties, body):
	global auctions_count
	#Receive person found
	auctions_count += 1
	auction_info = json.loads(body.decode('utf-8'))

	# Save person into mysql
	sql = "INSERT INTO auction_info (x_position, y_position, boat_id, time_stamp) VALUES (%s, %s, %s, %s)"
	val = (auction_info['x_position'], auction_info['y_position'],auction_info['boat_id'],auction_info['time_stamp'])
	mycursor.execute(sql, val)
	mydb.commit()

if __name__ == '__main__':
	# Establish incoming connection from Speed Clusters
	connection_in = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port))
	channel_in = connection_in.channel()
	channel_in.exchange_declare(exchange='auctioning_info', exchange_type='direct')
	result_in = channel_in.queue_declare(queue="",exclusive=True)
	queue_in_name = result_in.method.queue
	channel_in.queue_bind(exchange='auctioning_info',queue=queue_in_name,routing_key='key_auctioning_info')

	# Indicate queue readiness
	print(' [*] Waiting for messages. To exit, press CTRL+C')

	# Consumption configuration
	channel_in.basic_consume(on_message_callback=callback,queue=queue_in_name)

	# Begin consuming from speed clusters
	channel_in.start_consuming()
	


