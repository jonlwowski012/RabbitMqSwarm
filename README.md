# RabbitMqSwarm
- To start mySQL run ```$ docker-compose -f docker-compose.yml up ```
- Login to mySQL with ```$ mysql -h YOUR_IP -u lambda --password=test5243 ```, switch to lambda database with ```use lambda ```; source dump file with ```source dump.sql ```;
- To build all the docker containers run ```$ sudo sh build.sh ```
- To run the docker containers run ```$ sudo sh run.sh ```
- To run ASV and USVs, wait for docker containters to start then run ```$ sudo sh run_asv.sh ``` and ```$ sudo sh run_uav.sh ``` 
- To stop the docker containers run ```$ sudo sh killall.sh ```
- To stop mySQL run ```$ docker-compose down ```
