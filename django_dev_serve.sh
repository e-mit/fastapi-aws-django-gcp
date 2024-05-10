#!/bin/bash

# Run the development server, creating a fresh SQLite database

rm $(dirname "$0")/django_app/db.sqlite3

python manage.py migrate

python manage.py runserver