#!/bin/bash
set -x -e

: ${STSIZE:=100000000}
: ${DBSIZE:=10000000}

docker-compose down
docker-compose -f unrestricted.yml up -d --build
# Prepare Starts
docker-compose exec sort     prepare -a ${STSIZE}
docker-compose exec sysbench prepare --dbsize ${DBSIZE}
# Prepare Ends
docker-compose down

echo 3 | sudo tee /proc/sys/vm/drop_caches

docker-compose up -d
# docker-compose stop graphana # if you dont want online monitoring

# RUN Starts
# Mysql: |-----|ooooo|-----|ooooo|-----
# Sort : |-----|-----|-----------------
PERIODE=$((5*60))
docker-compose exec -d sort run -S 1G
while docker-compose exec sort status | grep running
do
    docker-compose exec sysbench run --dbsize ${DBSIZE} --duration ${PERIODE}
    sleep ${PERIODE}
done
# RUN Ends
docker-compose stop collector
docker-compose start graphana
