import numpy as np
import random
import matplotlib.pyplot as plt
import pika
import time
import yaml
import json
from sklearn import cluster
import mysql.connector
import signal
import sys
import math

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

### Read config parameters for RabbitMQ
with open('config.yaml') as f:
    config = yaml.safe_load(f)
    hostname = config['hostname']
    username = config['username']
    password = config['password']
    port = config['port']
credentials = pika.PlainCredentials(username, password)
connection = None

# Parralel k-means clustering
def clustering(poses):
	t0 = time.time()
	location_array = poses
	flag = False
	min_inertia = 100000
	k = 1
	### while the average cluster radius is greater than 10m
	while((min_inertia/len(location_array))>= 20 or flag == False):
		### Calculate Clusters
		kmeans = cluster.KMeans(init='k-means++', n_init=8, n_clusters=k, random_state=1, n_jobs=-1)
		kmeans.fit(location_array)
		min_inertia = kmeans.inertia_
		flag = True
		k+= 1
	### Calculate Clusters
	centroids_temp = kmeans.cluster_centers_
	labels = kmeans.labels_
	inertia = kmeans.inertia_

	### Calculate Radius for Cluster Msg
	radius = inertia/len(location_array)

	### Calculate Centroids of Clusters
	centroids = centroids_temp

	### Get Labels for all people's locations
	labels = kmeans.labels_
	#print(centroids)
	return centroids, labels

# Sends locations of clusters found to Rabbit
def publish_to_mq(clusters, labels, num_people, time_stamp):
    for index, cluster in enumerate(clusters):
        people_count = 0
        # Get number of people in  the cluster
        for  label in labels:
            if label == index:
                people_count += 1
        entry = {}
        entry['x_position'] = cluster[0]
        entry['y_position'] = cluster[1]
        entry['people_in_cluster'] = people_count
        entry['num_people'] = num_people
        entry['time_stamp'] = time_stamp
        cluster_to_send = json.dumps(entry)
        #print(entry)
        # Publish message to outgoing exchange
        channel.basic_publish(exchange='clusters_found',
                            routing_key='key_clusters_found',
                            body=cluster_to_send) 
        time.sleep(0.01)

def close_pika(signal, frame):
    print('Closing Pika Connection')
    connection.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, close_pika)
# Establish outgoing connection to Speed Clustering
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, credentials=credentials, port=port, heartbeat_interval=0, blocked_connection_timeout=600000))
channel = connection.channel()
channel.exchange_declare(exchange='clusters_found', exchange_type='direct')

while(1):
    mycursor.execute("SELECT x_position, y_position FROM people_found")
    people_found = mycursor.fetchall()
    if len(people_found) > 0:
        num_people = len(people_found)
        t0 = time.time()
        print("Clustering ",  num_people, " people")
        clusters, labels = clustering(people_found)
        print("Time to Cluster: ", time.time()-t0, " Clusters Found: ", len(clusters))
        publish_to_mq(clusters, labels, num_people, time.strftime('%Y-%m-%d %H:%M:%S'))
    mydb.commit()

