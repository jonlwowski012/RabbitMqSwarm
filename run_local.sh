#!/bin/bash

cd sql_savers && xterm -e python3 save_people.py &
cd sql_savers && xterm -e python3 save_speed_clusters.py &
cd speed_clustering && xterm -e python3 speed_clustering.py &
cd visualizer && xterm -e python3 viz_speed_clustering_new.py &
cd visualizer && xterm -e python3 viz_people_new.py &
cd uav_client && xterm -e python3 uav_client_new.py 
