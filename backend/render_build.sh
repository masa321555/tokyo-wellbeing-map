#!/usr/bin/env bash
# Build script for Render

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p instance

# Skip database initialization during build to avoid timeout
# Database will be initialized on first request or manually
echo "Skipping database initialization during build to avoid timeout"

# Verify uvicorn is installed
which uvicorn
uvicorn --version

echo "Build completed successfully!"