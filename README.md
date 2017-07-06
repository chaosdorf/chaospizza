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
requests are frozen and can't be changed anymore. Finally, people pay, food is
delivered, everyone is happy.  

![System Context Diagram](docs/system-context.png "System Context Diagram")


# Development

Minimum software required:  
 
- pyenv
- vagrant

To setup a minimal development environment:  

1. Create virtualenv: `make venv` 
2. Install dependencies: `make install-dev`
3. Launch postgres: `vagrant up`

## Linting

The makefile is configured to always run linters before tests or the local development server is started.  
 
To only run linters:  

    $ make lint

## Testing

Run tests:  

    $ make test

Linting always takes a few seconds.  This can be annoying e.g. when debugging complicated problems.  When a tighter
feedback loop is required, run:

    $ make testonly

**Note:** This won't check code for correctness so make sure to always lint afterwards.  

Run a django shell in the test environment:  

    $ make repl-test

When using the django test client, make sure to run the [following lines][dj-test-client] first:

    import django
    django.test.utils.setup_test_environment()

[dj-test-client]: https://docs.djangoproject.com/en/1.11/intro/tutorial05/#the-django-test-client

## Web server 

Run the django development server:    

    $ make run

The application is available at `http://localhost:8000`.  

Django admin:  

- Admin: `http://localhost:8000/admin/`
- Documentation: `http://localhost:8000/admin/doc/` 

The admin user must be created via `python manage.py createsuperuser`.    

Run a django shell in the development environment:  

    $ make repl-dev

## Python requirements

Requirements are managed via `pip-compile` and a separate Makefile in the `requirements/` directory.  This
[blogpost][pip-compile-workflow] explains how it works.  

**tl;dr:** put top-level dependencies without versions in `(base|dev|prod).in`, run `make requirements`, commit both
`.in` and `.txt` files.  

[pip-compile-workflow]: http://jamescooke.info/a-successful-pip-tools-workflow-for-managing-python-package-requirements.html


# Deployment

TODO

### Environment variables

The django application requires a set of environment variables to be configured.  In development, those can be
configured by placing an `.env` file in the project root containing `key=value` pairs.  

**Note:** When using vagrant, the `.env` is automatically created and configured to use the vagrant-provided postgres
database.   

Variables:

- `DJANGO_DATABASE_URL`

    URL to postgres database, e.g. `postgresql://[username]:[password]@[hostname]:5432/[dbname]`
    
    **Required**

- `DJANGO_EMAIL_BACKEND`

    Set to `django.core.mail.backends.console.EmailBackend` to disable SMTP delivery.
    
    **Optional**, default: `django.core.mail.backends.smtp.EmailBackend`

- `DJANGO_EMAIL_URL`

    Mail server to send mails.
    
    **Required**

- `DJANGO_EMAIL_SUBJECT_PREFIX`

    Subject prefix of sent emails.
    
    **Optional**, default: `[chaospizza]`

- `DJANGO_DEFAULT_FROM_EMAIL`

    Mail sender name.
    
    **Optional**, default: `chaospizza <noreply@pizza.chaosdorf.de>`

**For production:**

- `DJANGO_SECRET_KEY`

    Secret key for cryptographic signing.
    
    **Required**

- `DJANGO_ALLOWED_HOSTS`

    Public http hostname of the site.
    
    **Required**

- `DJANGO_STATIC_ROOT`

    Local directory where static files are stored for serving.
     
    **Optional**, default: `[projectroot]/staticfiles`

- `DJANGO_STATIC_URL`

    URL prefix where static files are served.
    
    **Optional**, default: `/static/`

# License

The MIT License (MIT)

Copyright (c) 2017 Chaosdorf e.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
