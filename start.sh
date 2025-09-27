#!/bin/bash
set -e  # Exit on any error

echo "Starting deployment process..."

# Print environment info for debugging
echo "=== Environment Debug ==="
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-'not set'}"
echo "PGDATABASE: ${PGDATABASE:-'not set'}"
echo "PGUSER: ${PGUSER:-'not set'}"
echo "PGHOST: ${PGHOST:-'not set'}"
echo "DATABASE_URL exists: $([ -n "$DATABASE_URL" ] && echo "true" || echo "false")"
echo "DATABASE_PUBLIC_URL exists: $([ -n "$DATABASE_PUBLIC_URL" ] && echo "true" || echo "false")"
echo "=========================="

# Change to backend directory
cd backend

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --log-file -
