# pylint: disable=C0111
# pylint: disable=W0401
# pylint: disable=W0614
"""
Development settings.

In the development environment:
- Debug mode is enabled
- The secret key is hardcoded in the file
- A SMTP email backend with mailhog settings is used
- The django-debug-toolbar is configured
"""
from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True
ALLOWED_HOSTS = []


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = 'yoloyolo123'


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'


# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += ['debug_toolbar']
INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG = {
}
