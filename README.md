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
![docker-release-build](https://github.com/e-mit/fastapi-aws-django-gcp/actions/workflows/docker-release-build.yml/badge.svg)
![release-test](https://github.com/e-mit/ fastapi-aws-django-gcp/actions/workflows/release-test.yml/badge.svg)
![docker-hub-push](https://github.com/e-mit/ fastapi-aws-django-gcp/actions/workflows/docker-hub-push.yml/badge.svg)
![gcp-artifact-push](https://github.com/e-mit/ fastapi-aws-django-gcp/actions/workflows/gcp-artifact-push.yml/badge.svg)
![google-cloud-deploy](https://github.com/e-mit/ fastapi-aws-django-gcp/actions/workflows/google-cloud-deploy.yml/badge.svg)


A demo project for posting and displaying text messages online, comprising:
- A FastAPI app hosted on AWS, using API Gateway, Lambda and DynamoDB.
- A Django app hosted on GCP, using Cloud Run, SQLite, Gunicorn and Docker.

[View the FastAPI Swagger UI on AWS.](https://peil328b55.execute-api.eu-west-2.amazonaws.com/docs)

[Try the Django app on GCP.](https://django-app-service-43e3cwelsq-ew.a.run.app/)


## Continuous automated test, build and deploy

Tests, linting and Docker build run via GitHub actions after each git push.

If all action workflows pass, the new Docker image (Django app) is automatically pushed to Docker Hub and deployed to Google Cloud Run as a new revision. The Cloudformation stack (FastAPI) is also created/updated on AWS.


## Configure, build and deploy manually

1. Run ```setup.sh``` to create the AWS stack, start the API and print the public endpoint URL
2. Repeat these steps to update the stack if anything is changed. Changes can be applied more quickly by running ```stack.sh``` directly, in the following cases:
    - Update the lambda code
    - Update the lambda layer, which contains the Python dependency packages
    - Change the log level
3. Build, check and push the Docker image


## Local tests

These use uvicorn and the official test dynamoDB Docker container to run entirely without AWS cloud.

- Unit and integration tests: ```./run_tests.sh```
- Manual testing and evaluation: ```./run_dev.sh```


## Cloud tests

After deploying to AWS, do ```./run_cloud_tests.sh```


## Use notes

- Google Cloud Run instances are started in response to user access, so will have an initial startup delay.
- Cloud Run instances stay idle for up to 15 minutes after starting, before shutting down (but there is no minimum guaranteed idle period). New accesses within this time will be fast.
- No state is saved between instances, and a new crypographic key is generated on each startup. This means that a CSRF error will occur if the front-end webpage is loaded from one instance and a form is submitted to a second instance.
