#!/bin/bash
set -x -e

: ${STSIZE:=100000000}
: ${DBSIZE:=10000000}

docker-compose down
docker-compose -f unrestricted.yml up -d --build
# Prepare Starts
docker-compose exec sort     prepare -a ${STSIZE}
docker-compose exec sysbench prepare --dbsize ${DBSIZE}
# Prepare Endso
docker-compose down

docker-compose up -d
# docker-compose stop graphana # if you dont want online monitoring

# RUN Starts
# Mysql: |-----|ooooo|-----|ooooo|-----
# Sort : |-----|-----|-----------------
PERIODE=$((5*60))
docker-compose exec -d sort run -S 1G
until docker-compose exec sort terminated
do
    docker-compose exec -d sysbench run --dbsize ${DBSIZE} --duration ${PERIODE}
    sleep ${PERIODE}
done
# RUN Ends
docker-compose stop collector
docker-compose start graphana
