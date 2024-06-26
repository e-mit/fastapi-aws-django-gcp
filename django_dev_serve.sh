#!/bin/bash

# Run the development server, creating a fresh SQLite database

export DJANGO_SECRET_KEY=$(openssl rand -base64 32)
export DJANGO_DEBUG=1
export DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1"
export API_URL="https://peil328b55.execute-api.eu-west-2.amazonaws.com"

rm -f django_app/db.sqlite3

python django_app/manage.py migrate

python django_app/manage.py runserver 0.0.0.0:8080
