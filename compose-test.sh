#!/bin/bash
set -x
echo "Script is executing!"
docker-compose up -d --network=host -f ./docker-compose.yml

