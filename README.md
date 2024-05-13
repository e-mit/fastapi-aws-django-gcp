# FastAPI-AWS-Django-GCP


![tests](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/tests.yml/badge.svg)
![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/e-mit/9df92671b4e2859b1e75cf762121b73f/raw/fastapi-aws-django-gcp.json)
![flake8](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/flake8.yml/badge.svg)
![mypy](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/mypy.yml/badge.svg)
![pycodestyle](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/pycodestyle.yml/badge.svg)
![pydocstyle](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/pydocstyle.yml/badge.svg)
![pylint](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/pylint.yml/badge.svg)
![pyright](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/pyright.yml/badge.svg)
![bandit](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/bandit.yml/badge.svg)
![aws-deploy](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/aws-deploy.yml/badge.svg)


A demo project for posting and displaying text messages online, comprising:
- A FastAPI app hosted on AWS, using API Gateway, Lambda and DynamoDB.
- A Django app hosted on GCP, using Cloud Run, SQLite, Gunicorn and Docker.

[View the FastAPI Swagger UI on AWS.](https://peil328b55.execute-api.eu-west-2.amazonaws.com/docs)


## TO DO
- Django release configuration
- Docker containerisation
- Deployment on GCP Cloud Run


## Continuous automated test, build and deploy

Tests, linting and Docker build run via GitHub actions after each git push.

If all action workflows pass, the new Docker image (Django) is automatically pushed to Docker Hub and deployed to Google Cloud Run as a new revision. The AWS Cloudformation stack (FastAPI) is also created/updated.


## Configure, build and deploy manually

1. Choose values for the environment variables listed in ```config.sh```
2. Run ```setup.sh``` to create the AWS stack, start the API and print the public endpoint URL
3. Repeat these steps to update the stack if anything is changed. Changes can be applied more quickly by running ```stack.sh``` directly, in the following cases:
    - Update the lambda code
    - Update the lambda layer, which contains the Python dependency packages
    - Change the log level
4. Build, check and push the Docker image


## Local tests

These use uvicorn and the official test dynamoDB Docker container to run entirely without AWS cloud.

- Unit and integration tests: ```./run_tests.sh```
- Manual testing and evaluation: ```./run_dev.sh```


## Cloud tests

After deploying to AWS, do ```./run_cloud_tests.sh```
