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
colors = ['b','g','y','k','c','r','m']
tsp_count = 0
curr_num_tsp = 0
boat_ids = []
curr_time = None
count = 0
prev_x = 0
prev_y = 0
fig,p = plt.subplots()
boatid = 0
### Plotter ###
def plot(prev_x,prev_y,boatid,uav,auction_info):
	for value in auction_info:
		#print("prev_x: "+str(prev_x))
		#print("prev_y: "+str(prev_y))
		#print("current_x: "+str(value[0]))
		#print("current_y: "+str(value[1]))
		if prev_x == 0 and prev_y == 0:
			p.scatter(value[0],value[1],c=colors[uav%len(colors)],s=5, label ="Boat ID: "+ str(boatid))
		else:
			p.arrow(prev_x,prev_y,value[0]-prev_x,value[1]-prev_y,fc=colors[uav%len(colors)], ec=colors[uav%len(colors)])
			p.scatter(value[0],value[1],c=colors[uav%len(colors)],s=5)
		prev_x = value[0]
		prev_y = value[1]
	
if __name__ == '__main__':
	print("Starting")
	# Establish incoming connection from Speed Clusters
	while(1):
		mycursor.execute("SELECT boat_id FROM boat_info")
		boat_ids = mycursor.fetchall()
		for boat_id in enumerate(boat_ids):
			print("Boat id:"+str(boat_id[1][0]))
			boatid = boat_id[1][0]
			mycursor.execute("SELECT x_position, y_position, seq_id FROM tsp_info WHERE boat_id=" + str(boat_id[1][0]) + " AND time_stamp = (SELECT MAX(time_stamp) FROM tsp_info WHERE boat_id=" + str(boat_id[1][0])+");")
			auction_info = mycursor.fetchall()
			plot(prev_x,prev_y,boatid,count,auction_info)
			prev_x = 0
			prev_y = 0
			count = count+1
		count = 0
		plt.ylim([-300,300])
		plt.xlim([-300,300])
		p.legend()
		plt.draw()
		plt.pause(.1)
		p.cla()
