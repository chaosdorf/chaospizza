#!/bin/sh
echo "*** Exporting django static files"
python manage.py collectstatic --no-input

echo "*** Running django migrations"
python manage.py migrate --no-input

echo "*** Creating default admin user"
EMAIL=${DJANGO_ADMIN_EMAIL:-admin@example.org}
USERNAME=${DJANGO_ADMIN_USERNAME:-admin}
PASSWORD=${DJANGO_ADMIN_PASSWORD:-admin}
echo "from django.contrib.auth.models import User; \
  User.objects.filter(email='$EMAIL').delete(); \
  User.objects.create_superuser('$USERNAME', '$EMAIL', '$PASSWORD')" \
   | python manage.py shell

echo "*** Launching application server"
exec gunicorn config.wsgi:application \
    --name chaospizza \
    --bind 0.0.0.0:${GUNICORN_BIND_PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-4} \
    "$@"
