docker-compose -f docker-compose.yml up -d --build
sleep 15
sudo mysql --host=192.168.1.102 -u lambda lambda --password=test5243 -e "source dump.sql"

