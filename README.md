# FastAPI-AWS-Django-GCP


## Configure and deploy

1. Choose values for the environment variables listed in ```config.sh```
2. Run ```setup.sh``` to create the stack, start the API and print the public endpoint URL
3. Repeat these steps to update the stack if anything is changed. Faster changes can be applied by running ```stack.sh``` directly, in the following cases:
    - Update the lambda code
    - Update the lambda layer, which contains the Python dependency packages
    - Change the log level


## Local tests

These use uvicorn and the official local test dynamoDB Docker container to run entirely without AWS cloud.

- Unit and integration tests: ```./run_tests.sh```
- Manual test and evaluation: ```./run_dev.sh```


## Cloud tests

After deploying to AWS, run ```python -m pytest cloud_tests```
