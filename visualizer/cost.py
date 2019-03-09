#!/usr/bin/env python

# Title: Cost Calculation for Rescue Problem
# Description: Calculates the time to run various components of the rescue problem.
# Engineer: Sean Ackels
# Email: s.ackels@yahoo.com
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

### Calculator ###
def findHz(times):
	totals = []
	allTimes = []
	Hz = []
	count = 1
	for i in range(0,len(times)-1):
		time = times[i][0].seconds
		nextTime = times[i+1][0].seconds
		if(time == nextTime):
			count = count + 1
		else:
			allTimes.append(times[i][0].seconds)
			totals.append(count)
			count = 1
	for j in range(1,len(totals)):
		Hz.append(float(totals[j])/float((allTimes[j]-allTimes[j-1])))
#	print(totals)
#	print(allTimes)
#	print(Hz)
	return Hz
if __name__ == '__main__':
	print("Starting")
	# Establish incoming connection from Speed Clusters
#	while(1):

	mycursor.execute("SELECT time_stamp FROM tsp_info")
	tspTimes = mycursor.fetchall()
	print("Avg Hz tsp: ", sum(findHz(tspTimes))/len(findHz(tspTimes)))

	mycursor.execute("SELECT time_stamp FROM clusters_found")
	clusteringTimes = mycursor.fetchall()
	print("Avg Hz clustering: ", sum(findHz(clusteringTimes))/len(findHz(clusteringTimes)))

	mycursor.execute("SELECT time_stamp FROM speed_clusters_found")
	speedClusteringTimes = mycursor.fetchall()
	print("Avg Hz speed clustering: ", sum(findHz(speedClusteringTimes))/len(findHz(speedClusteringTimes)))

	mycursor.execute("SELECT time_stamp FROM auction_info")
	auctioningTimes = mycursor.fetchall()
	print("Avg Hz auction: ", sum(findHz(auctioningTimes))/len(findHz(auctioningTimes)))

	mycursor.execute("SELECT time_stamp FROM people_found")
	peopleTimes = mycursor.fetchall()
	print("Avg Hz people: ", sum(findHz(peopleTimes))/len(findHz(peopleTimes)))
