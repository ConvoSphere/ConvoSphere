#!/bin/bash

# Test script for frontend-backend communication configuration
# This script verifies that the communication between frontend and backend is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
WS_URL=${WS_URL:-"ws://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:5173"}

echo -e "${YELLOW}Testing Frontend-Backend Communication Configuration${NC}"
echo "=================================================="
echo "Backend URL: $BACKEND_URL"
echo "WebSocket URL: $WS_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to check if a service is running
check_service() {
    local url=$1
    local service_name=$2
    
    echo -n "Checking $service_name... "
    
    if curl -s --max-time 5 "$url/api/v1/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not accessible${NC}"
        return 1
    fi
}

# Function to test API endpoints
test_api_endpoints() {
    echo ""
    echo -e "${YELLOW}Testing API Endpoints${NC}"
    echo "----------------------"
    
    local endpoints=(
        "/api/v1/health"
        "/api/v1/auth/login"
        "/api/v1/users"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo -n "Testing $endpoint... "
        
        if curl -s --max-time 5 "$BACKEND_URL$endpoint" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Accessible${NC}"
        else
            echo -e "${RED}✗ Not accessible${NC}"
        fi
    done
}

# Function to test WebSocket connection
test_websocket() {
    echo ""
    echo -e "${YELLOW}Testing WebSocket Connection${NC}"
    echo "------------------------------"
    
    # Check if websocat is available
    if ! command -v websocat &> /dev/null; then
        echo -e "${YELLOW}websocat not found. Install it to test WebSocket connections.${NC}"
        echo "Installation: brew install websocat (macOS) or apt-get install websocat (Ubuntu)"
        return 0
    fi
    
    echo -n "Testing WebSocket endpoint... "
    
    # Test WebSocket connection (without authentication)
    if timeout 5 websocat "$WS_URL/api/v1/ws/chat" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ WebSocket accessible${NC}"
    else
        echo -e "${RED}✗ WebSocket not accessible${NC}"
    fi
}

# Function to test CORS configuration
test_cors() {
    echo ""
    echo -e "${YELLOW}Testing CORS Configuration${NC}"
    echo "---------------------------"
    
    echo -n "Testing CORS headers... "
    
    local cors_response=$(curl -s -I -H "Origin: $FRONTEND_URL" "$BACKEND_URL/api/v1/health" 2>/dev/null | grep -i "access-control-allow-origin" || true)
    
    if [[ -n "$cors_response" ]]; then
        echo -e "${GREEN}✓ CORS headers present${NC}"
        echo "  $cors_response"
    else
        echo -e "${RED}✗ CORS headers missing${NC}"
    fi
}

# Function to validate environment variables
validate_env_vars() {
    echo ""
    echo -e "${YELLOW}Validating Environment Variables${NC}"
    echo "--------------------------------"
    
    local required_vars=("BACKEND_URL" "WS_URL" "FRONTEND_URL")
    
    for var in "${required_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            echo -e "${GREEN}✓ $var is set: ${!var}${NC}"
        else
            echo -e "${RED}✗ $var is not set${NC}"
        fi
    done
}

# Function to test Docker Compose configuration
test_docker_compose() {
    echo ""
    echo -e "${YELLOW}Testing Docker Compose Configuration${NC}"
    echo "-------------------------------------"
    
    if [[ -f "docker-compose.yml" ]]; then
        echo -n "Checking docker-compose.yml... "
        
        # Check if the required environment variables are defined
        if grep -q "BACKEND_URL\|VITE_API_URL\|VITE_WS_URL" docker-compose.yml; then
            echo -e "${GREEN}✓ Configuration found${NC}"
        else
            echo -e "${YELLOW}⚠ Configuration may be incomplete${NC}"
        fi
    else
        echo -e "${RED}✗ docker-compose.yml not found${NC}"
    fi
}

# Main execution
main() {
    validate_env_vars
    
    if check_service "$BACKEND_URL" "Backend"; then
        test_api_endpoints
        test_cors
    fi
    
    test_websocket
    test_docker_compose
    
    echo ""
    echo -e "${GREEN}Communication test completed!${NC}"
    echo ""
    echo "If you see any issues:"
    echo "1. Check that all services are running"
    echo "2. Verify environment variables are set correctly"
    echo "3. Check firewall and network connectivity"
    echo "4. Review the configuration documentation"
}

# Run main function
main "$@" 