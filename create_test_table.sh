#!/bin/bash

# Make a table in the local dynamodb test system

aws dynamodb create-table \
    --table-name $DB_TABLE_NAME \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=pk,AttributeType=N \
        AttributeName=timestamp_ms,AttributeType=N \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3 \
    --table-class STANDARD \
    --endpoint-url http://localhost:8000 \
    --global-secondary-indexes \
    "[
        {
            \"IndexName\": \"gsi\",
            \"KeySchema\": [{\"AttributeName\":\"pk\",\"KeyType\":\"HASH\"},
                            {\"AttributeName\":\"timestamp_ms\",\"KeyType\":\"RANGE\"}],
            \"Projection\":{\"ProjectionType\":\"ALL\"},
            \"ProvisionedThroughput\": {
                \"ReadCapacityUnits\": 3,
                \"WriteCapacityUnits\": 3
            }
        }
    ]" &> /dev/null
