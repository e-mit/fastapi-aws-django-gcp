#!/bin/bash
# Version 2.0.0

# A script to create an AWS Lambda function within a Cloudformation stack.

# Run this script like:
# ./stack.sh <stack name> <command> <3rd argument>

# Where "command" is one of the following:
entryFuncs=("delete" "create" "update_function" "update_layer" "loglevel")

# "delete": Delete the existing stack and all of its resources.
# "create": Create the stack. An error occurs if a stack already
#           exists with the provided name, and no update occurs.
# "update_function": Update just the lambda definition.
# "update_layer": Update just the python dependency package layer.
# "loglevel": Change the lambda logging level.

# Possible 3rd arguments:
#   "stack": Optional 3rd argument is a space-separated list
#            of parameter-overrides to pass to cloudformation
#            deploy, which become template parameters.
#   "loglevel": Mandatory 3rd argument is a log level string
#               e.g. INFO, DEBUG, ERROR, etc.

############################################################

STACK_NAME=$1
ARG3=$3

if [[ -z $STACK_NAME ]]; then
    echo ERROR: Please set STACK_NAME
    return 1
else
    # Convert to lower-case
    STACK_NAME_LOWER="$(echo $STACK_NAME | tr '[A-Z]' '[a-z]')"
fi

# Prevent terminal output waiting:
export AWS_PAGER=""

_check_for_existing_stack() {
    aws cloudformation describe-stacks \
    --stack-name $STACK_NAME >/dev/null 2>&1

    if [[ "$?" -eq 0 ]]; then
        echo "ERROR: stack $STACK_NAME already exists. The stack was not updated."
        return 1
    fi
}

_make_names() {
    FUNCTION_NAME="${STACK_NAME}-function"
    BUCKET_NAME="${STACK_NAME_LOWER}-bucket" # Lower case only
    LAYER_NAME=$FUNCTION_NAME-layer
}

_delete_files() {
    rm -rf function/__pycache__
    rm -f function/*.pyc out.yml *.zip
}

delete() {
    _delete_files
    _make_names
    echo "Deleting stack $STACK_NAME and its resources (lambda and role)..."

    aws cloudformation delete-stack --stack-name $STACK_NAME
    if [[ "$?" -eq 0 ]]; then
        echo "Deleted $STACK_NAME"
    fi

    # Note that the layer(s) are not included in the stack.
    while true; do
    VERSION=$(aws lambda list-layer-versions \
    --layer-name $LAYER_NAME | \
    python3 -c \
"import sys, json
try:
    print(json.load(sys.stdin)['LayerVersions'][0]['Version'])
except:
    exit(1)")
    if [[ "$?" -ne 0 ]]; then
        break
    fi
    aws lambda delete-layer-version \
    --layer-name $LAYER_NAME \
    --version-number $VERSION
    echo "Deleted layer $LAYER_NAME:$VERSION"
    done
}

_prepare_packages() {
    rm -rf package venv
    /usr/bin/python3 -m venv venv
    source venv/bin/activate
    pip3 install --target package/python -r requirements.txt &> /dev/null
    pip3 install -r requirements.txt &> /dev/null
    pip3 install -r test_requirements.txt &> /dev/null
}

create() {
    _make_names
    _check_for_existing_stack
    _prepare_packages
    echo "Creating $STACK_NAME with Lambda $FUNCTION_NAME..."

    aws s3 mb s3://$BUCKET_NAME
    echo Made temporary S3 bucket $BUCKET_NAME

    aws cloudformation package \
    --template-file template.yml \
    --s3-bucket $BUCKET_NAME \
    --output-template-file out.yml &> /dev/null

    aws cloudformation deploy \
    --template-file out.yml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides functionName=$FUNCTION_NAME $ARG3

    if [[ "$?" -ne 0 ]]; then
        aws cloudformation describe-stack-events \
        --stack-name $STACK_NAME
    fi

    aws s3 rb --force s3://$BUCKET_NAME
    echo Deleted the temporary S3 bucket
}

loglevel() {
    _make_names

    if [[ -z $ARG3 ]]; then
        echo "ERROR: log level string is required (INFO, DEBUG, etc.)"
        return 1
    fi

    export ARG3
    ENV_VARS=$(aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME | \
    python3 -c \
    "import sys, json, os
environment = json.load(sys.stdin)['Environment']
environment['Variables']['LOG_LEVEL'] = os.environ['ARG3']
print(json.dumps(environment))")

    aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment "$ENV_VARS" &> /dev/null

    if [[ "$?" -eq 0 ]]; then
        echo "Log level set to $ARG3"
    fi
}

update_function() {
    _make_names
    _delete_files
    cd function
    zip -r ../function.zip .
    cd ..
    aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://function.zip &> /dev/null
    if [[ "$?" -eq 0 ]]; then
        echo Updated Lambda $FUNCTION_NAME
    fi
}

update_layer() {
    _make_names
    _prepare_packages
    cd package
    zip -r ../package.zip . &> /dev/null
    cd ..
    LAYER_ARN=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "Python package layer" \
    --zip-file fileb://package.zip \
    --compatible-runtimes python3.10 \
    --compatible-architectures "x86_64" | jq -r '.LayerVersionArn')

    aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --layers $LAYER_ARN &> /dev/null

    if [[ "$?" -eq 0 ]]; then
        echo "Created and assigned layer $LAYER_ARN"
    fi
}

################################################

ok=0
for i in "${entryFuncs[@]}"
do
    if [ "$i" == "$2" ]; then
        echo "Executing $i()"
        $i
        ok=1
    fi
done

if (( ok == 0 )); then
    echo "Error: command not recognised"
fi
