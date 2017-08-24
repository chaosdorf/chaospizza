FROM python:3-alpine

COPY . /chaospizza
WORKDIR /chaospizza

RUN apk update
RUN apk add build-base python-dev libffi-dev postgresql-dev
RUN pip install -r /chaospizza/requirements/prod.txt

CMD python manage.py runserver
