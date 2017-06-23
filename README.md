# chaospizza

This project contains a django web project which provides the main order
functionality for chaospizza.  

The application provides a web UI to announce food delivery orders.  You'll
announce a new order, tell other people to add their requests (or they get
notified).  At some point the order is made, food is delivered, people pay, etc
etc. There are also status updates and deadlines for orders.  

# System Context Diagram

![System Context Diagram](docs/system-context.png "System Context Diagram")

## Local development environment

Python 3.6.1 is required and should be installed in a new virtualenv named
`chaospizza-3.6.1`.  The project contains a `.python-version` file so the
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

# License

The MIT License (MIT)

Copyright (c) 2017 Chaosdorf e.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
