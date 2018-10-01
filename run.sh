#!/bin/bash

xterm -e sudo docker run -it --name auctioning auctioning &
xterm -e sudo docker run -it --name clustering clustering &
xterm -e sudo docker run -it --name metaclustering metaclustering & 
xterm -e sudo docker run -it --name tsp tsp &
sleep 3
xterm -e sudo docker run -it --name uav_client uav_client &
xterm -e sudo docker run -it --name asv_client asv_client 
