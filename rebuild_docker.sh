#!/bin/bash
source .env

image=$(docker inspect --format='{{.Config.Image}}' demeter)
CURRENT_DEMETER_VERSION="${image##*:}"

if [ $CURRENT_DEMETER_VERSION = $DEMETER_VERSION ]; then
    echo "please change version in .env"
else
    sudo docker compose down
    echo "rm a old container: demeter"

    sudo docker image rm athena/demeter:$CURRENT_DEMETER_VERSION
    echo "rm image athena/demeter:$CURRENT_DEMETER_VERSION"

    sudo docker build -t athena/demeter:$DEMETER_VERSION .
    echo "build a new image: athena/demeter:$DEMETER_VERSION"

    sudo docker compose up -d
    echo "run a new container: demeter"
fi
