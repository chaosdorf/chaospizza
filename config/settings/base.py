"""
Django settings for web-application project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import environ

# (web-application/config/settings/base.py - 3 = web-application/)
ROOT_DIR = environ.Path(__file__) - 3
# web-application/chaospizza
APPS_DIR = ROOT_DIR.path('chaospizza')

# Load django configuration from environment variables
env = environ.Env()


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
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
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
USE_I18N = True
USE_L10N = True
USE_TZ = True


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


# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:////tmp/my-tmp-sqlite.db'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


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
            ],
        },
    },
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
STATICFILES_DIRS = [str(APPS_DIR.path('static'))]
STATIC_ROOT = str(ROOT_DIR('staticfiles'))
STATIC_URL = '/static/'
