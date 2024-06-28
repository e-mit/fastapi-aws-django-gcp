# How to create a GCP Artifact registry repo and GCR instance

1. login and set project:
gcloud auth login
gcloud config set project fastapi-aws-django-gcp

2. Make a repo:
gcloud artifacts repositories create djangorepo \
  --repository-format=docker \
  --location=europe-west1 \
  --description="repo for django app image"

Also manually configure it to have a cleanup policy where untagged images are deleted. By always
pushing to the same name and tag, the previous one becomes untagged and thus is deleted (eventually).

3. Tag the image with a special name:
docker tag django_app:latest europe-west1-docker.pkg.dev/fastapi-aws-django-gcp/djangorepo/django_app:latest

4. Configure (one time)
gcloud auth configure-docker europe-west1-docker.pkg.dev

5. Push:
docker push europe-west1-docker.pkg.dev/fastapi-aws-django-gcp/djangorepo/django_app:latest

6. Need to set up a new GCR service (manually on web console)
- Provide it with the environment variables
- Also select "cpu-boost" and "session-affinity"


7. Deploy the pushed container to the service
gcloud run deploy django-app-service --image europe-west1-docker.pkg.dev/fastapi-aws-django-gcp/djangorepo/django_app:latest --region europe-west1
