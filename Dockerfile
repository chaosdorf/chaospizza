FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add build-base libffi-dev postgresql-dev
RUN pip install --no-cache-dir pipenv

RUN mkdir -p /opt/app
WORKDIR /opt/app
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install --system --deploy
COPY src /opt/app

ENV DJANGO_SETTINGS_MODULE='config.settings.prod' \
    DJANGO_STATIC_ROOT='/var/src/app/staticfiles' \
    DJANGO_STATIC_URL='/static/' \
    DJANGO_ADMIN_EMAIL='admin@example.org' \
    DJANGO_ADMIN_USERNAME='admin' \
    DJANGO_ADMIN_PASSWORD='admin' \
    GUNICORN_BIND_PORT=8000 \
    GUNICORN_WORKERS=4

CMD ["/opt/app/wait-for-db.sh", "/opt/app/run.sh"]
EXPOSE 8000
