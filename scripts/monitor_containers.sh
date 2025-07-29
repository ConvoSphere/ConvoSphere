#!/bin/bash

# Container monitoring script for ChatAssistant
# Monitors all containers for errors and warnings

echo "Starting container monitoring for ChatAssistant..."
echo "Press Ctrl+C to stop monitoring"
echo "=================================="

# Function to check container status
check_status() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking container status..."
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

# Function to check for errors in logs
check_errors() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking for errors in logs..."
    
    # Check for errors in all containers
    errors=$(docker compose logs --since=5m 2>/dev/null | grep -i "error\|exception\|failed\|fatal" || true)
    
    if [ -n "$errors" ]; then
        echo "⚠️  ERRORS FOUND:"
        echo "$errors"
        echo ""
    else
        echo "✅ No errors found in recent logs"
    fi
    
    # Check for warnings
    warnings=$(docker compose logs --since=5m 2>/dev/null | grep -i "warning" || true)
    
    if [ -n "$warnings" ]; then
        echo "⚠️  WARNINGS FOUND:"
        echo "$warnings"
        echo ""
    fi
}

# Function to test API endpoints
test_apis() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Testing API endpoints..."
    
    # Test backend health
    if curl -s -f http://localhost:8000/api/v1/health/ > /dev/null; then
        echo "✅ Backend API is responding"
    else
        echo "❌ Backend API is not responding"
    fi
    
    # Test frontend
    if curl -s -f http://localhost:8081 > /dev/null; then
        echo "✅ Frontend is responding"
    else
        echo "❌ Frontend is not responding"
    fi
    
    echo ""
}

# Main monitoring loop
while true; do
    check_status
    check_errors
    test_apis
    echo "=================================="
    sleep 30  # Check every 30 seconds
done 