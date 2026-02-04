#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd portal-backend; python3 manage.py createsuperuser --no-input)
fi
(cd portal-backend; gunicorn portal.wsgi --reload --user www-data --bind unix:/opt/portal.sock --workers 3) &
nginx -g "daemon off;"
