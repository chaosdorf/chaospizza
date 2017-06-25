"""
Per-environment settings for the django web application.

The base module contains most settings which are shared by all environments and
is never used directly. For each environment there is a module named after the
environment (e.g. dev.py) which imports everything from base and adds additional
settings.

Those modules are then configured in the DJANGO_SETTINGS_MODULE variable before
django is started.
"""
