#!/bin/bash

xterm -e sudo docker run -it --name auction_saver auction_saver &
xterm -e sudo docker run -it --name boat_info_saver boat_info_saver &
xterm -e sudo docker run -it --name metaclusters_saver metaclusters_saver &
xterm -e sudo docker run -it --name people_saver people_saver &
xterm -e sudo docker run -it --name speed_clusters_saver speed_clusters_saver &
xterm -e sudo docker run -it --name tsp_saver tsp_saver &
sleep 5

xterm -e sudo docker run -it --name auctioning auctioning &
#xterm -e sudo docker run -it --name clustering clustering &
xterm -e sudo docker run -it --name speed_clustering speed_clustering &
xterm -e sudo docker run -it --name metaclustering metaclustering & 
xterm -e sudo docker run -it --name tsp tsp &
sleep 5

xterm -e sudo docker run -it --name uav_client uav_client &
xterm -e sudo docker run -it --name asv_client asv_client 
