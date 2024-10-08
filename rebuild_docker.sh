#!/bin/bash
source .env

sudo docker stop demeter
echo "stop container demeter"

sudo docker rm demeter
echo "rm container demeter"

sudo docker build -t athena/demeter:$DEMETER_VERSION .
echo "build a new image: athena/demeter:$DEMETE_VERSION"

sudo docker volume rm demeter_results
echo "rm a volume: demeter_results"

sudo docker volume create demeter_results
echo "create a volume: demeter_results"

sudo docker run -d -p 5000:5000 --name demeter --restart unless-stopped -v demeter_results:/app/src/demeter/results athena/demeter:$DEMETER_VERSION
echo "run a new container: demeter"
