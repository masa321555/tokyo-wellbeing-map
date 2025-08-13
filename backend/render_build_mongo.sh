#!/bin/bash

# render_build_mongo.sh - Build script for MongoDB version on Render

set -e

echo "Building MongoDB version of Tokyo Wellbeing Map API..."

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories if they don't exist
mkdir -p app/static app/logs

echo "Build completed successfully!"
echo "Note: Database initialization will happen on application startup"