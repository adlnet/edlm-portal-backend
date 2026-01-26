#!/usr/bin/env bash
# start-server.sh

# python manage.py waitdb 
python3 manage.py collectstatic --no-input
python3 manage.py migrate
python3 manage.py createcachetable
mkdir -p ./media/graphs
cd /opt/app/ 
pwd 
./start-server.sh 
