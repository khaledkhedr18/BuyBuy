#!/bin/bash

echo "=== BuyBuy Django Railway Deployment Setup ==="
echo ""
echo "IMPORTANT: When prompted, please select:"
echo "1. Workspace: Khaled Khedr's Projects"
echo "2. Project: lavish-communication (NOT discerning-curiosity)"
echo "3. Environment: production"
echo "4. Service: BuyBuy (or create new service if needed)"
echo ""
echo "The Django app is now configured to connect to the PostgreSQL database"
echo "in the discerning-curiosity project using the public URL:"
echo "postgresql://postgres:***@nozomi.proxy.rlwy.net:24106/railway"
echo ""
read -p "Press Enter to continue with Railway linking..."

railway link

echo ""
echo "Checking current Railway project status..."
railway status

echo ""
echo "Current Django settings are configured for cross-project database connection."
echo "You can now deploy with: railway up"
echo ""
echo "=== Setup Complete! ==="
