from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
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
spark = SparkSession.builder.appName("KMeansExample").getOrCreate()

# Parralel k-means clustering
def clustering(poses):
    print(len(poses))
    dff = map(lambda x: (0,(Vectors.dense(x[0:2]))), poses)
    mydf = spark.createDataFrame(dff,schema=["None","features"])
    k = 2
    cost = 99999999999
    while(cost >= 20):
        kmeans = KMeans().setK(k).setSeed(1)
        model = kmeans.fit(mydf)
        cost = model.computeCost(mydf)/len(poses)
        k+=1
        print("K: ", k, " Cost: ", cost)
    centers = model.clusterCenters()
    centroids = []
    for center in centers:
        centroids.append(center)
    prediction = model.transform(mydf).select('prediction').collect()
    labels = [p.prediction for p in prediction ]
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
        clusters, labels = clustering(people_found)
        print("Time to Cluster: ", time.time()-t0, " Clusters Found: ", len(clusters))
        publish_to_mq(clusters, labels, num_people, time.strftime('%Y-%m-%d %H:%M:%S'))
    mydb.commit()

