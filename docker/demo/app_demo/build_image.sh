#!/bin/sh

IMAGE_NAME="app_server_name"

build_image() {
    # name_prefix="xxxx.com/"
    docker_name="${IMAGE_NAME}:${MODE}_${COMMIT_ID}_${TIMENOW}"
    docker build -t ${docker_name} .
    check_ret $? $FUNCNAME
    echo "docker_name: ${docker_name}"
}

clear() {
    rm -rf target
    rm -rf requirements.txt
}

check_ret() {
  if [ $1 != 0 ]; then
    echo "err: $2 Failure, Exit!"
    exit $1
  fi
}

copy_code() {
    mkdir target
    cp -r ../app target
    cp -r ../conf target
    cp -r ../data target
    cp -r ../test target
    cp -r ../scripts target
    cp ../run.py target
    cp ../place_holder.py target
    cp ../requirements.txt ./
    cp ../requirements.txt target
    cd target && mkdir logs && cd ../
    rm -rf target/conf/global/*
}

if [ $# -lt 1 ]; then
    echo "Usage: sh build.sh {mode}"
    echo "mode argument value: dev, prod"
    exit 1
fi

MODE=$1
TIMENOW=$(date +%y.%m.%d.%H%M)
check_ret $? $FUNCNAME
COMMIT_ID=$(git rev-parse --short HEAD)
check_ret $? $FUNCNAME

if [ "$MODE" != "dev" ] && [ "$MODE" != "prod" ]; then
  echo "mode argument error: $MODE"
  echo "Only 'dev' and 'prod' modes are supported."
  exit 1
fi

echo "build image start..."
clear
copy_code
build_image
clear
echo "build image success..."


