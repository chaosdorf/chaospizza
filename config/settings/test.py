# pylint: disable=C0111
# pylint: disable=W0401
# pylint: disable=W0614
"""
Test settings.

For testing in development environment and CI:
- The secret key is hardcoded in the file
- A console email backend is used
"""
from .base import *  # noqa

SECRET_KEY = 'yoloyolo123'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
