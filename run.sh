#!/bin/bash

docker run -d --hostname my-rabbit --name rabbit_daemon rabbitmq:3
docker run -d --hostname my-rabbit --name rabbit_manager -p 8080:5672 rabbitmq:3-management

xterm -T auction_saver -hold -e sudo docker run -it --name auction_saver auction_saver &
xterm -T boat_info_saver -hold -e sudo docker run -it --name boat_info_saver boat_info_saver &
xterm -T metaclustering_saver -hold -e sudo docker run -it --name metaclusters_saver metaclusters_saver &
xterm -T people_saver -hold -e sudo docker run -it --name people_saver people_saver &
xterm -T speed_clustering_saver -hold -e sudo docker run -it --name speed_clusters_saver speed_clusters_saver &
xterm -T clustering_saver -hold -e sudo docker run -it --name clusters_saver clusters_saver &
xterm -T tsp_saver -hold -e sudo docker run -it --name tsp_saver tsp_saver &


xterm -T auctioning -hold -e sudo docker run -it --name auctioning auctioning &
xterm -T clustering -hold -e sudo docker run -it --name clustering clustering &
xterm -T speed_clustering -hold -e sudo docker run -it --name speed_clustering speed_clustering &
xterm -T metaclustering -hold -e sudo docker run -it --name metaclustering metaclustering & 
xterm -T tsp -hold -e sudo docker run -it --name tsp tsp &

#xterm -e sudo docker run -it --name uav_client uav_client &
#xterm -e sudo docker run -it --name asv_client1 asv_client &
#xterm -e sudo docker run -it --name asv_client2 asv_client &
#xterm -e sudo docker run -it --name asv_client3 asv_client &
#xterm -e sudo docker run -it --name asv_client4 asv_client &
#xterm -e sudo docker run -it --name asv_client5 asv_client 
