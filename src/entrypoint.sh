#!/bin/sh
set -e  # Output on error

uv run manage.py collectstatic --no-input
uv run manage.py migrate
uv run uvicorn app.asgi:application --host 0.0.0.0 --port 8000