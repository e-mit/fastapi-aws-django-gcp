#!/bin/bash

# Create a stack instance according to the parameters supplied in the
# environment variables. For an example configuration, see config.sh

####################################################

source stack.sh $NAME_PREFIX create "timeout=$LAMBDA_TIMEOUT_SEC"

DB_TABLE_NAME=$NAME_PREFIX-function-dynamodb

# Add environment variables to the lambda
aws lambda update-function-configuration \
--function-name $FUNCTION_NAME \
--environment "Variables={LOG_LEVEL=$LOG_LEVEL, \
DB_TABLE_NAME=$DB_TABLE_NAME}" &> /dev/null
