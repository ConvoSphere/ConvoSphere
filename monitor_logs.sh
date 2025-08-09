#!/bin/bash

echo "=========================================="
echo "ConvoSphere AI Assistant Platform - Status"
echo "=========================================="
echo ""

# Check backend status
echo "🔧 Backend Status:"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Backend is running on http://localhost:8000"
    echo "   📊 Health check response:"
    curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "   ❌ Backend is not responding"
fi
echo ""

# Check frontend status
echo "🎨 Frontend Status:"
if curl -s http://localhost:8080 > /dev/null; then
    echo "   ✅ Frontend is running on http://localhost:8080"
    echo "   🌐 React development server is active"
else
    echo "   ❌ Frontend is not responding"
fi
echo ""

# Show running processes
echo "📋 Running Processes:"
echo "   Backend (Python):"
ps aux | grep "python.*backend" | grep -v grep | while read line; do
    echo "   - $line"
done

echo "   Frontend (Node.js):"
ps aux | grep -E "(npm|vite)" | grep -v grep | while read line; do
    echo "   - $line"
done
echo ""

# Show port usage
echo "🔌 Port Usage:"
echo "   Port 8000: Backend API"
echo "   Port 8080: Frontend Development Server"
echo ""

# Show recent logs (if available)
echo "📝 Recent Activity:"
echo "   Backend logs:"
if [ -f "backend/logs/app.log" ]; then
    tail -5 backend/logs/app.log 2>/dev/null || echo "   No log file found"
else
    echo "   No log file found"
fi
echo ""

echo "🚀 Access URLs:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo "   API Health: http://localhost:8000/health"
echo "   API Status: http://localhost:8000/api/v1/status"
echo ""

echo "=========================================="
echo "Monitoring complete!"
echo "=========================================="