docker ps | grep -v "rabbitmqswarm_db_1" | awk {' print $1 '} | tail -n+2 > tmp.txt; for line in $(cat tmp.txt); do docker kill $line; done; rm tmp.txt
#docker rm $(docker ps -a | awk 'NR>1 {print $1}')
docker rm $(docker ps -a | grep -v "rabbitmqswarm_db_1" | awk 'NR>1 {print $1}')
