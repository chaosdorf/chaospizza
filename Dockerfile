FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add build-base python-dev libffi-dev postgresql-dev

RUN mkdir -p /usr/src/app
COPY requirements/prod.txt /usr/src/app/requirements.txt
RUN cd /usr/src/app && pip install --no-cache-dir -r /usr/src/app/requirements.txt
COPY src /usr/src/app

ENV DJANGO_SETTINGS_MODULE='config.settings.prod' \
    DJANGO_STATIC_ROOT='/var/src/app/staticfiles' \
    DJANGO_STATIC_URL='/static/' \
    DJANGO_ADMIN_EMAIL='admin@example.org' \
    DJANGO_ADMIN_USERNAME='admin' \
    DJANGO_ADMIN_PASSWORD='admin' \
    GUNICORN_BIND_PORT=8000 \
    GUNICORN_WORKERS=4

WORKDIR /usr/src/app
CMD ["./wait-for-db.sh", "run.sh"]
EXPOSE 8000
