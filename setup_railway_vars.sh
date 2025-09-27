#!/bin/bash

# Database connection details from discerning-curiosity project
DATABASE_PUBLIC_URL="postgresql://postgres:CalFyXLkugZMUGFHoYEYkRfbGzsmDVxk@nozomi.proxy.rlwy.net:24106/railway"

echo "Setting up database environment variables for lavish-communication project..."

# Set the environment variables in the Django project
railway variables set DATABASE_URL="$DATABASE_PUBLIC_URL"
railway variables set PGHOST="nozomi.proxy.rlwy.net"
railway variables set PGPORT="24106"
railway variables set PGDATABASE="railway"
railway variables set PGUSER="postgres"
railway variables set PGPASSWORD="CalFyXLkugZMUGFHoYEYkRfbGzsmDVxk"

echo "Database environment variables set successfully!"
echo "Variables set:"
echo "DATABASE_URL: $DATABASE_PUBLIC_URL"
echo "PGHOST: nozomi.proxy.rlwy.net"
echo "PGPORT: 24106"
echo "PGDATABASE: railway"
echo "PGUSER: postgres"
echo "PGPASSWORD: [HIDDEN]"
