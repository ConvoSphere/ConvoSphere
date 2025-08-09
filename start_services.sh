#!/bin/bash

echo "🚀 Starting ConvoSphere AI Assistant Platform..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if ss -tlnp | grep -q ":$port "; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if not already installed
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p backend/logs
mkdir -p backups

# Set environment variables
export DATABASE_URL="sqlite:///./backend/test.db"
export REDIS_URL="redis://localhost:6379"
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="convosphere-api-key"
export SECRET_KEY="dev-secret-key-for-development-only-change-in-production"
export DEBUG="true"
export ENVIRONMENT="development"
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000,http://localhost:8081"

echo "Environment variables set:"
echo "DATABASE_URL: $DATABASE_URL"
echo "DEBUG: $DEBUG"
echo "ENVIRONMENT: $ENVIRONMENT"

# Start backend if not already running
echo "🔧 Starting Backend..."
if check_port 8000; then
    echo "   ✅ Backend is already running on port 8000"
else
    echo "   🚀 Starting backend..."
    source venv/bin/activate
    python simple_backend.py &
    sleep 5
    if check_port 8000; then
        echo "   ✅ Backend started successfully"
    else
        echo "   ❌ Failed to start backend"
    fi
fi

# Start frontend if not already running
echo "🎨 Starting Frontend..."
if check_port 8080; then
    echo "   ✅ Frontend is already running on port 8080"
else
    echo "   🚀 Starting frontend..."
    cd frontend-react
    npm run dev &
    sleep 10
    if check_port 8080; then
        echo "   ✅ Frontend started successfully"
    else
        echo "   ❌ Failed to start frontend"
    fi
    cd ..
fi

echo ""
echo "🎉 Services started! Access URLs:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📊 Run './monitor_logs.sh' to check status and logs"