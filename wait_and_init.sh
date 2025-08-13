#!/bin/bash

# Simple deployment wait and init script

API_URL="https://tokyo-wellbeing-map.onrender.com"
echo "🔄 Waiting for new deployment..."

# Check every 30 seconds for up to 10 minutes
for i in {1..20}; do
    echo -n "  Attempt $i/20: "
    
    # Check if new endpoint exists
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/admin/init-data-now")
    
    if [ "$STATUS" != "404" ]; then
        echo "✅ New deployment detected!"
        
        # Initialize database
        echo "📦 Initializing database..."
        RESULT=$(curl -s "$API_URL/api/v1/admin/init-data-now")
        echo "   Result: $RESULT"
        
        # Verify
        echo "🔍 Verifying data..."
        curl -s "$API_URL/api/v1/areas/" | head -c 200
        echo
        echo "✨ Done!"
        exit 0
    else
        echo "Still waiting..."
        sleep 30
    fi
done

echo "❌ Timeout - deployment is taking too long"
exit 1