#!/bin/bash
set -x -e

docker-compose -f metric.yml  up --build -d # Remote machine
docker-compose -f prepare.yml up --build
docker-compose -f run.yml     up --build
docker-compose -f report.yml  up --build    # Remote machine
