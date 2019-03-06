#!/bin/bash

xterm -T auction_saver -e sudo docker run -it --name auction_saver auction_saver &
xterm -T boat_info_saver -e sudo docker run -it --name boat_info_saver boat_info_saver &
xterm -T metaclustering_saver -e sudo docker run -it --name metaclusters_saver metaclusters_saver &
xterm -T people_saver -e sudo docker run -it --name people_saver people_saver &
xterm -T speed_clustering_saver -e sudo docker run -it --name speed_clusters_saver speed_clusters_saver &
xterm -T tsp_saver -e sudo docker run -it --name tsp_saver tsp_saver &
sleep 5

xterm -T auctioning -e sudo docker run -it --name auctioning auctioning &
xterm -T clustering -e sudo docker run -it --name clustering clustering &
xterm -T speed_clustering -e sudo docker run -it --name speed_clustering speed_clustering &
xterm -T metaclustering -e sudo docker run -it --name metaclustering metaclustering & 
xterm -T tsp -e sudo docker run -it --name tsp tsp &
sleep 5

#xterm -e sudo docker run -it --name uav_client uav_client &
#xterm -e sudo docker run -it --name asv_client1 asv_client &
#xterm -e sudo docker run -it --name asv_client2 asv_client &
#xterm -e sudo docker run -it --name asv_client3 asv_client &
#xterm -e sudo docker run -it --name asv_client4 asv_client &
#xterm -e sudo docker run -it --name asv_client5 asv_client 
