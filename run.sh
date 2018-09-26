#!/bin/bash

xterm -e sudo docker run --name auctioning auctioning &
xterm -e sudo docker run --name clustering clustering &
xterm -e sudo docker run --name metaclustering metaclustering & 
xterm -e sudo docker run --name tsp tsp &
sleep 3
xterm -e sudo docker run --name uav_client uav_client &
xterm -e sudo docker run --name asv_client asv_client 
