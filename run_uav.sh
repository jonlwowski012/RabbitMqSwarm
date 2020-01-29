#!/bin/bash
UAVS=2
for i in `seq 1 $UAVS`;
do
	xterm -T uav_client_$i -hold -e sudo docker run -it --name uav_client_$i uav_client &
	echo uav_client_$i
done
#xterm -e sudo docker run -it --name asv_client2 asv_client &
#xterm -e sudo docker run -it --name asv_client3 asv_client &
#xterm -e sudo docker run -it --name asv_client4 asv_client &
#xterm -e sudo docker run -it --name asv_client5 asv_client 
