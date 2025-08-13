#!/bin/bash

echo "=========================================="
echo "Tokyo Wellbeing Map - Production Data Check"
echo "=========================================="
echo

# Check number of areas
echo "Checking number of areas in production..."
AREA_COUNT=$(curl -s -X GET "https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/areas/?limit=25" | grep -o '"name":"[^"]*"' | wc -l | tr -d ' ')
echo "Areas found: $AREA_COUNT"

if [ "$AREA_COUNT" -eq "23" ]; then
    echo "✅ All 23 wards are present!"
    
    # Check Nerima specifically
    echo
    echo "Checking Nerima (練馬区) data..."
    NERIMA_DATA=$(curl -s -X GET "https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/areas/" | grep -B5 -A5 "練馬区")
    
    if [ ! -z "$NERIMA_DATA" ]; then
        echo "✅ Nerima (練馬区) found!"
        
        # Get Nerima's area code
        NERIMA_CODE=$(echo "$NERIMA_DATA" | grep -o '"code":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Area code: $NERIMA_CODE"
        
        # Check waste separation strictness
        echo
        echo "Checking waste separation rules..."
        WASTE_DATA=$(curl -s -X GET "https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/areas/$NERIMA_CODE")
        STRICTNESS=$(echo "$WASTE_DATA" | grep -o '"strictness_level":[^,]*' | cut -d':' -f2)
        
        if [ ! -z "$STRICTNESS" ]; then
            echo "Strictness level: $STRICTNESS"
            if (( $(echo "$STRICTNESS > 4" | bc -l) )); then
                echo "✅ Nerima has strict waste separation rules!"
            else
                echo "❌ Nerima waste separation rules are not strict enough"
            fi
        else
            echo "❌ Could not find waste separation data"
        fi
        
        # Check housing data
        echo
        echo "Checking housing data..."
        RENT_2LDK=$(echo "$WASTE_DATA" | grep -o '"rent_2ldk":[^,]*' | cut -d':' -f2)
        if [ ! -z "$RENT_2LDK" ]; then
            echo "2LDK Rent: ${RENT_2LDK}万円"
            echo "✅ Housing data is present"
        else
            echo "❌ Housing data not found"
        fi
        
    else
        echo "❌ Nerima (練馬区) not found"
    fi
else
    echo "❌ Expected 23 areas, but found $AREA_COUNT"
    echo
    echo "The deployment might still be in progress. Please:"
    echo "1. Check Render dashboard at https://dashboard.render.com"
    echo "2. Wait for the deployment to complete"
    echo "3. Run this script again"
fi

echo
echo "=========================================="
echo "To re-initialize production data after deployment:"
echo "curl -X GET 'https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/admin/init-data-now'"
echo "=========================================="