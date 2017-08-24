FROM python:3-alpine

COPY . /chaospizza
WORKDIR /chaospizza

RUN apk update
RUN apk add build-base python-dev libffi-dev postgresql-dev
RUN pip install -r /chaospizza/requirements/prod.txt

ENV DJANGO_DATABASE_URL=
ENV DJANGO_SECRET_KEY=
ENV DJANGO_ALLOWED_HOSTS=
ENV DJANGO_STATIC_ROOT=
ENV DJANGO_STATIC_URL=

CMD python manage.py migrate && python manage.py runserver
