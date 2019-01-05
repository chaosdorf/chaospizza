# chaospizza

[![Build Status](https://travis-ci.org/chaosdorf/chaospizza.svg?branch=master)][travis]
[![Coverage Status](https://coveralls.io/repos/github/chaosdorf/chaospizza/badge.svg?branch=master)][coveralls]

[travis]: https://travis-ci.org/chaosdorf/chaospizza
[coveralls]: https://coveralls.io/github/chaosdorf/chaospizza?branch=master

This repository contains a django web project that provides a simple way to
coordinate food delivery orders.

# System Context

A coordinator can announce a food delivery order and then tell other people to
add food requests.  When the coordinator decides to place the order, food
requests are frozen and can't be changed anymore.  Finally, people pay, food is
delivered, everyone is happy.

![System Context Diagram](docs/system-context.png "System Context Diagram")

# Development

Software required:

- docker

To setup the development environment:

1. Create build image: `make build-image`
2. Start database: `make start-db`

## Linting

Run linters:

    $ make lint

## Testing

Run tests:

    $ make test

Pass additional parameters to pytest, e.g. to only run model tests:

    $ TESTOPS='-k test_models' make test

Run a shell using the build image (access `manage.py`, etc):

    $ make dev-shell

When using the django test client, make sure to run the [following lines][1]
first:

    import django
    django.test.utils.setup_test_environment()

[1]: https://docs.djangoproject.com/en/1.11/intro/tutorial05/#the-django-test-client

## Web server

Create database schema:

    $ make migrate

Run the django development server:

    $ make run

The application is available at `http://localhost:8000`.

Django admin:

- Admin: `http://localhost:8000/admin/`
- Documentation: `http://localhost:8000/admin/doc/`

The admin user must be created via `python manage.py createsuperuser`.

## Python requirements

Requirements are managed via `pipenv`.

### Environment variables

The django application requires a set of environment variables to be
configured.  For development, only `DJANGO_DATABASE_URL` is required and can be
configured by e.g. direnv.

- `DJANGO_DATABASE_URL`:

    URL to database.

    Format: `postgresql://[username]:[password]@[hostname]:5432/[dbname]`

    [dj-environ](https://github.com/joke2k/django-environ) explains this in detail.

# Deployment

The project provides a docker container to runs the django application in
gunicorn.  For production, the following parameters must be configured:

- `DJANGO_SECRET_KEY`:

    Secret key for cryptographic signing.

- `DJANGO_ALLOWED_HOSTS`:

    Public http hostname of the site.

Optional parameters:

- `DJANGO_STATIC_ROOT`:

    Default value: `[projectroot]/staticfiles`

    Local directory where static files are stored for serving.

- `DJANGO_STATIC_URL`:

    Default value: `/static/`

    URL prefix where static files are served.

- `DJANGO_ADMIN_EMAIL`:

    Default value: `admin@example.org`

- `DJANGO_ADMIN_USERNAME`:

    Default value: `admin`

- `DJANGO_ADMIN_PASSWORD`:

    Default value: `admin`

- `GUNICORN_BIND_PORT`:

    Default value: `8000`

- `GUNICORN_WORKERS`:

    Default value: `4`

- `SENTRY_DSN`:

    The production environment includes sentry error reporting, this must be set
    to the DSN as shown by sentry when creating a new project.
