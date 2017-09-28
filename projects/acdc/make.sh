#!/bin/bash

docker-compose -f prepare.yml up --build
docker-compose -f run.yml     up --build
docker-compose -f report.yml  up --build
