#!/bin/bash

# Create or update a stack instance according to the parameters supplied in
# the environment variables. For an example configuration, see config.sh

####################################################

# Prevent terminal output waiting:
export AWS_PAGER=""

source stack.sh $NAME_PREFIX create "timeout=$LAMBDA_TIMEOUT_SEC"

export DB_TABLE_NAME=$NAME_PREFIX-function-dynamodb

# Add environment variables to the lambda
aws lambda update-function-configuration \
--function-name $FUNCTION_NAME \
--environment "Variables={LOG_LEVEL=$LOG_LEVEL, \
DB_TABLE_NAME=$DB_TABLE_NAME}" &> /dev/null

echo ""
echo "Waiting for stack creation..."
CLOUD_URL=
while [[ -z $CLOUD_URL ]]; do
    export CLOUD_URL=$(aws apigatewayv2 get-apis --no-paginate | \
    python3 -c \
    "import sys, json
    for item in json.load(sys.stdin)['Items']:
        if item['Name'] == '${DB_TABLE_NAME}':
            print(item['ApiEndpoint'])")
    sleep 1
done

echo ""
echo "The API endpoint is:"
echo $CLOUD_URL
echo ""

python -m pytest cloud_tests
