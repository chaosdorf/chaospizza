# pylint: disable=C0103
"""
Django settings for web-application project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import pathlib
import environ

# (chaosdorf-pizza/config/settings/base.py - 3 = chaosdorf-pizza/)
ROOT_DIR = environ.Path(__file__) - 3
# chaosdorf-pizza/chaospizza
APPS_DIR = ROOT_DIR.path('chaospizza')

# Load django configuration from environment variables
env = environ.Env()
# environ.Env.read_env(str(ROOT_DIR.path('.env')))


def secret(name):
    """Load the named secret from /run/secrets and return None otherwise."""
    path = pathlib.Path("/run/secrets") / name
    if path.exists():
        return path.read_text().strip()
    return None


# DEBUG MODE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/1.11/ref/settings/#debug
# Disable debug by default to prevent accidental usage
DEBUG = False


# APP CONFIGURATION
# https://docs.djangoproject.com/en/1.11/ref/settings/#installed-apps
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'bootstrap3',
]
LOCAL_APPS = [
    'chaospizza.menus.apps.MenusConfig',
    'chaospizza.orders.apps.OrdersConfig',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'


# WSGI Configuration
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/1.11/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
# ------------------------------------------------------------------------------
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
USE_TZ = True


# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {'default': env.db('DJANGO_DATABASE_URL')}


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[chaospizza]')
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default='chaospizza <noreply@pizza.chaosdorf.de>')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)


# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]


# Password validation
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/1.11/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [str(APPS_DIR.path('templates'))],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'chaospizza.orders.context_processors.user_session',
            ],
        },
    },
]


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
STATICFILES_DIRS = [str(APPS_DIR.path('static'))]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = env('DJANGO_STATIC_ROOT', default=str(ROOT_DIR('staticfiles')))
STATIC_URL = env('DJANGO_STATIC_URL', default='/static/')
MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
