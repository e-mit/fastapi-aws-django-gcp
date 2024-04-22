#!/bin/bash

# Create a stack instance according to the parameters supplied in the
# environment variables. For an example configuration, see config.sh

####################################################

# Get the Security Group ID corresponding to SEC_GRP_NAME
SEC_GRP_ID=$(aws ec2 describe-security-groups \
--group-names $SEC_GRP_NAME | \
python3 -c \
"import sys, json
print(json.load(sys.stdin)['SecurityGroups'][0]['GroupId'])")

# List the subnets which the RDS is on
SUBNETS=$(aws rds describe-db-instances \
--db-instance-identifier $RDS_INSTANCE_NAME | \
python3 -c \
"import sys, json
sng = json.load(sys.stdin)['DBInstances'][0]['DBSubnetGroup']
subnets = sng['Subnets'][0]['SubnetIdentifier']
for s in sng['Subnets'][1:]:
    subnets += (',' + s['SubnetIdentifier'])
print(subnets)")


source stack.sh $NAME_PREFIX create \
"VPCsecurityGroupID=$SEC_GRP_ID VPCsubnetIDlist=$SUBNETS timeout=$LAMBDA_TIMEOUT_SEC"


# Add environment variables to the lambda
aws lambda update-function-configuration \
--function-name $FUNCTION_NAME \
--environment "Variables={LOG_LEVEL=$LOG_LEVEL, \
DB_TABLE_NAME=$DB_TABLE_NAME}" &> /dev/null
