#!/bin/bash

# Test using the deployed AWS stack

export NAME_PREFIX=testapi
export DB_TABLE_NAME=$NAME_PREFIX-function-dynamodb
export CLOUD_URL=https://peil328b55.execute-api.eu-west-2.amazonaws.com

python -m pytest cloud_tests
