#!/bin/bash

# Run the FastAPI app locally, using a temporary test dynamoDB instance, and run unit tests.
# Then also run static analysis and linting checks.

rm -rf package

export DB_TABLE_NAME=testTable
export TEST=true

# Prevent terminal output waiting:
export AWS_PAGER=""

docker run --rm --name dynamodb_test_local -d -p 8000:8000 amazon/dynamodb-local

sleep 5

./create_test_table.sh

python -m pytest --cov=function/app tests -p no:cacheprovider

docker stop -t 0 dynamodb_test_local


python -m bandit -r . --exclude=/tests/,/venv/,/cloud_tests/,message_tests.py
python -m flake8 --exclude=tests/*,venv/*,cloud_tests/*,django_app/django_app/settings.py,django_app/app/migrations/*
python -m mypy . --explicit-package-bases --exclude 'tests/' --exclude 'venv/' --exclude 'cloud_tests/'
python -m pycodestyle function
python -m pydocstyle function --ignore=D107,D203,D213
python -m pylint function
python -m pyright function
