#!/bin/sh

export API_URL="https://peil328b55.execute-api.eu-west-2.amazonaws.com"

# NB: run locally (without docker) using:
# python django_app/manage.py runserver 0.0.0.0:8080

############################################

docker build --no-cache --target dev -t django_dev:latest .

docker run -p 8080:8080 --name django_dev \
  -e API_URL=$API_URL --rm django_dev:latest

#docker stop -t 0 django_dev
