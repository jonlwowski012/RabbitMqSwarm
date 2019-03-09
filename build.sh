#!/bin/bash

sudo docker build -t asv_client asv_client
sudo docker build -t auctioning auctioning
sudo docker build -t clustering clustering
sudo docker build -t speed_clustering speed_clustering
sudo docker build -t metaclustering metaclustering
sudo docker build -t tsp tsp
sudo docker build -t uav_client uav_client

sudo docker build -t auction_saver sql_savers/auction_saver
sudo docker build -t boat_info_saver sql_savers/boat_info_saver
sudo docker build -t metaclusters_saver sql_savers/metaclusters_saver
sudo docker build -t people_saver sql_savers/people_saver
sudo docker build -t clusters_saver sql_savers/clusters_saver
sudo docker build -t speed_clusters_saver sql_savers/speed_clusters_saver
sudo docker build -t tsp_saver sql_savers/tsp_saver



