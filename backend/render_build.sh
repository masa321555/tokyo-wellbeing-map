#!/usr/bin/env bash
# Build script for Render

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p instance

# Initialize database
python -m app.database.init_db

# Verify uvicorn is installed
which uvicorn
uvicorn --version

echo "Build completed successfully!"