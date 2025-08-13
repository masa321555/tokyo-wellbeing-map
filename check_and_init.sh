#!/bin/bash

# Check deployment and initialize database script

echo "Checking deployment status and initializing database..."

# API URL
API_URL="https://tokyo-wellbeing-map.onrender.com"
INIT_ENDPOINT="$API_URL/api/v1/admin/init-data-now"
AREAS_ENDPOINT="$API_URL/api/v1/areas/"

# Maximum wait time (10 minutes)
MAX_WAIT=600
INTERVAL=30
ELAPSED=0

echo "Waiting for deployment to complete..."

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Check if the new endpoint exists
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$INIT_ENDPOINT")
    
    if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "500" ]; then
        echo "✓ Deployment completed! New endpoint is available."
        break
    fi
    
    echo "  Still deploying... (waited ${ELAPSED}s)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "✗ Timeout: Deployment took too long."
    exit 1
fi

# Initialize database
echo "Initializing database..."
INIT_RESPONSE=$(curl -s "$INIT_ENDPOINT")
echo "Response: $INIT_RESPONSE"

# Check if initialization was successful
if echo "$INIT_RESPONSE" | grep -q "success"; then
    echo "✓ Database initialized successfully!"
    
    # Verify by fetching areas
    echo "Verifying data..."
    AREAS_RESPONSE=$(curl -s "$AREAS_ENDPOINT" | head -c 100)
    echo "Areas API response: $AREAS_RESPONSE..."
    
    if echo "$AREAS_RESPONSE" | grep -q "千代田区"; then
        echo "✓ Data verification successful! Application is ready."
    else
        echo "⚠ Warning: Areas API returned unexpected response."
    fi
else
    echo "✗ Database initialization failed."
    echo "Trying POST method with secret key..."
    curl -X POST "$API_URL/api/v1/admin/init-data?secret_key=tokyo-wellbeing-2024"
fi

echo "Done!"