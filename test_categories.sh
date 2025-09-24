#!/bin/bash

echo "Testing category functionality..."
echo "1. Testing categories page:"
curl -s http://localhost:8000/categories/ | grep -i "categories\|error" | head -5

echo -e "\n2. Testing if categories page loads without errors:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/categories/)
echo "Status code: $STATUS"

if [ "$STATUS" = "200" ]; then
    echo "✅ Categories page loads successfully"
else
    echo "❌ Categories page failed to load"
fi
