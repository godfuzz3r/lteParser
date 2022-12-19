#!/bin/sh
echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"
#gunicorn --bind 0.0.0.0:1337 -w 1 app:app
python3 app.py