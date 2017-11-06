#!/bin/sh
cmd="$@"
echo "*** Testing if database is available"
until python manage.py inspectdb >/dev/null 2>&1; do
    >&2 echo "** Database is unavailable - sleeping"
    sleep 1
done
echo $@
exec $cmd
