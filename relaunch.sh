#!/bin/bash
set -e

dockername='email-webhook'

docker stop $dockername || true
docker rm $dockername || true

docker build -t $dockername \
    --build-arg http_proxy=$http_proxy \
    --build-arg https_proxy=$https_proxy \
    .

docker run -p 5000:5000 -d \
    --restart=always \
    --name $dockername \
    $dockername
