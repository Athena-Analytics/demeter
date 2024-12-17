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

    sudo docker volume rm demeter_app
    echo "rm a volume: demeter_app"

    sudo docker build -t athena/demeter:$DEMETER_VERSION .
    echo "build a new image: athena/demeter:$DEMETER_VERSION"

    sudo docker volume create demeter_app
    echo "create a volume: demeter_app"

    sudo docker run -d -p 5000:5000 --name demeter --restart unless-stopped -v demeter_app:/app/src/demeter athena/demeter:$DEMETER_VERSION
    echo "run a new container: demeter"
fi
