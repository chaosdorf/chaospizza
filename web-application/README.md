# chaosdorf-pizza

This project contains a django web project which provides the main order
functionality for chaospizza.  

## Local development environment

Python 3.6.1 is required and should be installed in a new virtualenv named
`chaospizza-3.6.1`. The project contains a `.python-version` file so the
virtualenv is activated automatically (when pyenv is configured correctly).

TODO: docker-compose

A `Makefile` is provided which automates most development tasks.

Install all dependencies in the current virtualenv:

    $ make install

Run the django development server:

    $ make run

Before the server is started, linters, tests, and migrations are run.

The django application is available at `http://localhost:8000`
The django admin is available at `http://localhost:8000/admin/`

TODO: Automatic admin user creation

## Environment variables

The django application requires the following environment variables:

TODO: Describe environment variables
