# pylint: disable=C0103
"""
WSGI config for webapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior
# chaospizza directory.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace('/config', ''), 'chaospizza'))

application = get_wsgi_application()
