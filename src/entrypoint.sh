#!/bin/sh
set -e  # Output on error

python manage.py collectstatic --no-input
python manage.py migrate
uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --workers 3