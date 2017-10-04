#!/bin/bash
set -x -e

: ${MEMORY:=$((2**31))} # 2**30 + 2**29 to let sort stress mysql
: ${STSIZE:=100000000}
: ${DBSIZE:=10000000}

docker-compose down
sudo cgdelete -g memory:/consolidate || true
sudo cgcreate -g memory:/consolidate
echo 1 | sudo tee $(lssubsys -m memory | cut -d ' ' -f2)/consolidate/memory.use_hierarchy
echo ${MEMORY} | sudo tee $(lssubsys -m memory | cut -d ' ' -f2)/consolidate/memory.limit_in_bytes

docker-compose -f unrestricted.yml up -d --build
# Prepare Starts
docker-compose exec sysbench prepare --dbsize ${DBSIZE} > /dev/null 2>&1
# Prepare Ends
docker-compose down

echo 3 | sudo tee /proc/sys/vm/drop_caches

docker-compose up -d
# docker-compose stop grafana # if you dont want online monitoring

# RUN Starts
# Mysql: |-----|-----|ooooo|-----|ooooo|-----
# Sort :       |-----|-----|-----------------
PERIODE=$((60))
docker-compose exec sysbench run --dbsize ${DBSIZE} --duration ${PERIODE} > /dev/null 2>&1
docker-compose exec sort online
docker-compose exec sysbench run --dbsize ${DBSIZE} --duration ${PERIODE} > /dev/null 2>&1
while docker-compose exec sort status | grep running
do
    sleep ${PERIODE}
    if ! docker-compose exec sort status | grep running
    then
	break
    fi
    docker-compose exec sysbench run --dbsize ${DBSIZE} --duration ${PERIODE} > /dev/null 2>&1
done
# RUN Ends
docker-compose stop collector
docker-compose start grafana
docker-compose exec influxdb influx -database dockerstats -execute 'select * from /.*/' -format=csv > dockerstats.csv
docker-compose exec influxdb influx -database sysbenchstats -execute 'select * from /.*/' -format=csv > sysbenchstats.csv
