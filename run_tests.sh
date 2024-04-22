#!/bin/bash

# Run the FastAPI app locally, using a temporary
# test dynamoDB instance, and run unit tests.

rm -rf package

export DB_TABLE_NAME=testTable
export TEST=true

# Prevent terminal output waiting:
export AWS_PAGER=""

docker run --rm --name dynamodb_test_local -d -p 8000:8000 amazon/dynamodb-local

sleep 5

./create_test_table.sh

python -m pytest tests -p no:cacheprovider

docker stop -t 0 dynamodb_test_local
