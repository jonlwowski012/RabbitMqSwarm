#!/bin/bash
sudo sh killall.sh 
sudo sh build.sh 
sudo sh run.sh &
sleep 5
sudo sh run_asv.sh &
sleep 5
sudo sh run_uav.sh &
