# Example parameters for creating an instance of this stack.
# Source this script, then run setup.sh

#########################################################

# Stack name and name prefix for the resources to be created
NAME_PREFIX=testapi

# Lambda CloudWatch log level
LOG_LEVEL=DEBUG

# Lambda timeout:
LAMBDA_TIMEOUT_SEC=10

# The name of the RDS instance whose VPC is required
RDS_INSTANCE_NAME=testdbi

# Security group in the database's VPC to use
SEC_GRP_NAME=lambda-rds-1

# TODO: make new security group
