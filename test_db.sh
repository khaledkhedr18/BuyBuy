#!/bin/bash
# Test script to check environment variables

echo "=== Environment Check ==="
echo "RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"
echo "PGDATABASE: $PGDATABASE"
echo "PGUSER: $PGUSER"
echo "PGHOST: $PGHOST"
echo "PGPORT: $PGPORT"
echo "PGPASSWORD: [masked]"
echo "DATABASE_URL exists: $([ -n "$DATABASE_URL" ] && echo "true" || echo "false")"
echo "========================="

cd backend
python manage.py check --database default
