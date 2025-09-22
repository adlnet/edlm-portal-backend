#!/usr/bin/env bash
# start-server.sh

# python manage.py waitdb 
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable
mkdir -p ./media/graphs
cd /opt/app/ 
pwd 
./start-server.sh 
