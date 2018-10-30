#!/bin/bash

# Launch SQL Savers
cd sql_savers && xterm -e python3 save_people.py &
cd sql_savers && xterm -e python3 save_speed_clusters.py &
cd sql_savers && xterm -e python3 save_metaclusters.py &
cd sql_savers && xterm -e python3 save_boat_info.py &
cd sql_savers && xterm -e python3 save_auctioning.py &
cd sql_savers && xterm -e python3 save_tsp.py &
sleep 5

# Launch Nodes
cd speed_clustering && xterm -e python3 speed_clustering.py &
cd metaclustering && xterm -e python3 metaclustering.py &
cd auctioning && xterm -e python3 auctioning.py &
cd tsp && xterm -e python3 tsp.py &
sleep 5

# Launch Visualizers
cd visualizer && xterm -e python3 viz_metaclustering.py &
cd visualizer && xterm -e python3 viz_speed_clustering_new.py &
cd visualizer && xterm -e python3 viz_people_new.py &
cd visualizer && xterm -e python3 viz_boats.py &
cd visualizer && xterm -e python3 viz_auctioning.py &
cd visualizer && xterm -e python3 viz_tsp.py &
sleep 5

# Launch ASVs
cd asv_client && xterm -e python3 asv_client.py &
cd asv_client && xterm -e python3 asv_client.py &
cd asv_client && xterm -e python3 asv_client.py &
cd asv_client && xterm -e python3 asv_client.py &
cd asv_client && xterm -e python3 asv_client.py &

# Launch UAV
cd uav_client && xterm -e python3 uav_client_new.py  &
 
