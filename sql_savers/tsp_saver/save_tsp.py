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
sql = "TRUNCATE TABLE tsp_info"
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
tsp_count = 0

# Receive messages from UAVs and plot
def callback(ch, method, properties, body):
	global tsp_count
	#Receive person found
	tsp_count += 1
	tsp_info = json.loads(body.decode('utf-8'))

	# Save person into mysql
	sql = "INSERT INTO tsp_info (x_position, y_position, boat_id, seq_id, time_stamp) VALUES (%s, %s, %s, %s, %s)"
	val = (tsp_info['x_position'], tsp_info['y_position'],tsp_info['boat_id'], tsp_info['seq_id'], tsp_info['time_stamp'])
	mycursor.execute(sql, val)
	mydb.commit()

if __name__ == '__main__':
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

	# Begin consuming from speed clusters
	channel_in.start_consuming()
	