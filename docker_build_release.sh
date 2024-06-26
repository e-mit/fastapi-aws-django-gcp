#!/bin/sh

export API_URL="https://peil328b55.execute-api.eu-west-2.amazonaws.com"
export DJANGO_ALLOWED_HOSTS='localhost 127.0.0.1'

# NB: run locally (without docker) using:
# gunicorn django_app.wsgi:application --bind 0.0.0.0:8080 --conf gunicorn_conf.py

############################################

docker build --no-cache --target release -t django_app:latest .

docker run -p 8080:8080 --name django_app \
  -e API_URL=$API_URL -e DJANGO_ALLOWED_HOSTS="$DJANGO_ALLOWED_HOSTS" \
  --rm django_app:latest

#docker stop -t 0 django_app
