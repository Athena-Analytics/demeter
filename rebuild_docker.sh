#!/bin/bash
source .env

image=$(docker inspect --format='{{.Config.Image}}' demeter)
CURRENT_DEMETER_VERSION="${image##*:}"

if [ $CURRENT_DEMETER_VERSION = $DEMETER_VERSION ]; then
    echo "please change version in .env"
else
    sudo docker stop demeter
    echo "stop container demeter"

    sudo docker rm demeter
    echo "rm container demeter"

    sudo docker image rm athena/demeter:$CURRENT_DEMETER_VERSION
    echo "rm image athena/demeter:$CURRENT_DEMETER_VERSION"

    sudo docker volume rm demeter_results
    echo "rm a volume: demeter_results"

    sudo docker build -t athena/demeter:$DEMETER_VERSION .
    echo "build a new image: athena/demeter:$DEMETER_VERSION"

    sudo docker volume create demeter_results
    echo "create a volume: demeter_results"

    sudo docker run -d -p 5000:5000 --name demeter --restart unless-stopped -v demeter_results:/app/src/demeter/results athena/demeter:$DEMETER_VERSION
    echo "run a new container: demeter"
fi
