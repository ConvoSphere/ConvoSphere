#!/bin/bash

# Update Dependencies Script
# This script updates the project dependencies and rebuilds containers

set -e

echo "🔄 Updating project dependencies..."

# Update backend dependencies
echo "📦 Updating backend dependencies..."
cd backend
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv pip install --upgrade pip
    uv pip install -r requirements.txt --upgrade
else
    echo "Using pip package manager..."
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
fi
cd ..

# Rebuild containers with new dependencies
echo "🐳 Rebuilding containers with updated dependencies..."
docker compose down
docker compose build --no-cache backend
docker compose up -d

echo "✅ Dependencies updated and containers rebuilt!"
echo "📋 Checking for any remaining issues..."

# Wait for containers to start
sleep 10

# Check container status
docker compose ps

echo "🎉 Update complete! Check the logs for any remaining warnings." 