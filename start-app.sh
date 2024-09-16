#!/usr/bin/env bash
# start-server.sh
pwd 
ls -al
# python manage.py waitdb 
python manage.py collectstatic --no-input
python manage.py migrate 
python manage.py createcachetable 
cd /opt/app/ 
pwd 
./start-server.sh 
