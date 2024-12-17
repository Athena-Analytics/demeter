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

    sudo docker build -t athena/demeter:$DEMETER_VERSION .
    echo "build a new image: athena/demeter:$DEMETER_VERSION"

    sudo docker run -d -p 5000:5000 --name demeter --restart unless-stopped -v /home/leaf/demeter/src/demeter/config.ini:/root/demeter/src/demeter/config.ini athena/demeter:$DEMETER_VERSION
    echo "run a new container: demeter"
fi
