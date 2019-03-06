#!/usr/bin/env python

# Title: TSP service
# Description: Recieves cluster locations and TSPs them
# Engineer: Jonathan Lwowski 
# Email: jonathan.lwowski@gmail.com
# Lab: Autonomous Controls Lab, The University of Texas at San Antonio


#########          Libraries         ###################
import numpy as np
import random
import time
import matplotlib.pyplot as plt
import yaml
import json
import signal
import sys
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
### Config ###
colors = ['b','g','y','k','c','r']
tsp_count = 0
curr_num_tsp = 0
boat_ids = []
curr_time = None
prev_x = None
prev_y = None
prev_id = None

if __name__ == '__main__':
	# Establish incoming connection from Speed Clusters
	mycursor.execute("SELECT boat_id FROM boat_info")
	boat_ids = mycursor.fetchall()
	for boat_id in enumerate(boat_ids):
		print(boat_id[1][0])
