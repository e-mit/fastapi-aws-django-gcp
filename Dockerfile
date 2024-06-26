# syntax=docker/dockerfile:1.7-labs

FROM python:3.10-slim as base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip
COPY django_app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY django_app .

ENV DJANGO_DB_DIR=/db
# These ENVs will be overwritten later (needed for collectstatic)
ENV DJANGO_DEBUG=0
ENV API_URL="http://example.com"
ENV DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1"
RUN python manage.py collectstatic --noinput

RUN addgroup nonroot
RUN adduser nonroot --disabled-password --ingroup nonroot

# Create a directory for SQLite database
RUN mkdir $DJANGO_DB_DIR
RUN python manage.py migrate
RUN chown -R nonroot:nonroot $DJANGO_DB_DIR
RUN chmod +w ${DJANGO_DB_DIR}/db.sqlite3

USER nonroot

FROM base as release
ENV DJANGO_DEBUG=0
CMD ["gunicorn", "django_app.wsgi:application", "--bind", "0.0.0.0:8080", "--conf", "gunicorn_conf.py"]

FROM base as dev
ENV DJANGO_DEBUG=1
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
