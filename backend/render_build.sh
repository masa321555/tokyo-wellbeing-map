#!/usr/bin/env bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p instance

# Initialize database
python -m app.database.init_db

echo "Build completed successfully!"