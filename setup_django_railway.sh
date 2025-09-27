#!/bin/bash

echo "=== Setting up Railway environment for Django deployment ==="

# Delete current railway.json to reset project linking
rm -f .railway/railway.json

echo "Linking to lavish-communication project..."

# Note: After running this script, you'll need to interactively select:
# 1. Khaled Khedr's Projects (workspace)
# 2. lavish-communication (project)
# 3. production (environment)
# 4. BuyBuy (service)

railway link

echo "Checking project status..."
railway status

echo "Setting database environment variables..."

# Set the database connection variables for cross-project connection
railway variables set DATABASE_URL="postgresql://postgres:CalFyXLkugZMUGFHoYEYkRfbGzsmDVxk@nozomi.proxy.rlwy.net:24106/railway"
railway variables set PGHOST="nozomi.proxy.rlwy.net"
railway variables set PGPORT="24106"
railway variables set PGDATABASE="railway"
railway variables set PGUSER="postgres"
railway variables set PGPASSWORD="CalFyXLkugZMUGFHoYEYkRfbGzsmDVxk"

echo "=== Setup complete! ==="
echo "You can now deploy with: railway up"
