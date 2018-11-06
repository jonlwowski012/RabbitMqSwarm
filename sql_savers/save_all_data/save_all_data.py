print('Writing database to csv file')

import csv
import time
import datetime
import os
import mysql.connector
import yaml
import uuid

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

cursor = mydb.cursor()


currentDate=datetime.datetime.now().date()
save_loc = str(currentDate)+'_'+str(uuid.uuid4())
os.mkdir(save_loc)

tables = ['people_found','clusters_found', 'speed_clusters_found','metaclusters_found', 'auction_info', 'boat_info', 'tsp_info']

for table in  tables:
	query = "SELECT * FROM %s;" % table
	cursor.execute(query)

	with open(save_loc+'/'+table+'.csv','w') as f:
	    writer = csv.writer(f)
	    for row in cursor.fetchall():
	        writer.writerow(row)

	print('Done')