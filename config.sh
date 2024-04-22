# Example parameters for creating an instance of this stack.
# Source this script, then run setup.sh

#########################################################

# Stack name and name prefix for the resources to be created
export NAME_PREFIX=testapi

# Lambda CloudWatch log level
export LOG_LEVEL=DEBUG

# Lambda timeout:
export LAMBDA_TIMEOUT_SEC=10

# The name of the RDS instance whose VPC is required
export RDS_INSTANCE_NAME=testdbi

# Security group in the database's VPC to use
export SEC_GRP_NAME=lambda-rds-1

export DB_TABLE_NAME=$NAME_PREFIX-function-dynamodb

# TODO: make new security group
