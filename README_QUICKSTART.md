# ConvoSphere AI Assistant Platform - Quick Start Guide

## 🚀 Current Status

✅ **Services Running Successfully!**

- **Backend API**: Running on http://localhost:8000
- **Frontend**: Running on http://localhost:8080
- **Health Check**: http://localhost:8000/health

## 📋 Available Scripts

### Start Services
```bash
./start_services.sh
```
This script will start both the backend and frontend services if they're not already running.

### Monitor Logs and Status
```bash
./monitor_logs.sh
```
This script provides a comprehensive status report including:
- Service health checks
- Running processes
- Port usage
- Access URLs

## 🌐 Access the Application

1. **Frontend (React App)**: http://localhost:8080
2. **Backend API**: http://localhost:8000
3. **API Health Check**: http://localhost:8000/health
4. **API Status**: http://localhost:8000/api/v1/status

## 🔧 What's Running

### Backend (Simple Version)
- **Port**: 8000
- **Framework**: FastAPI
- **Status**: ✅ Running
- **Features**: Basic health checks and API endpoints

### Frontend (React)
- **Port**: 8080
- **Framework**: React + Vite
- **Status**: ✅ Running
- **Features**: Modern UI with hot reload

## 📊 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### API Status
```bash
curl http://localhost:8000/api/v1/status
```

### Root Endpoint
```bash
curl http://localhost:8000/
```

## 🛠️ Development

### Backend Development
- The backend is currently running a simplified version (`simple_backend.py`)
- Full backend with all features requires additional configuration (database, AI providers, etc.)
- To work on the full backend, see the original `backend/` directory

### Frontend Development
- React development server with hot reload is active
- Changes to frontend code will automatically reload
- Check the browser console for any errors

## 🔍 Troubleshooting

### Check Service Status
```bash
./monitor_logs.sh
```

### Check Port Usage
```bash
ss -tlnp | grep -E "(8000|8080)"
```

### Restart Services
```bash
# Stop current services (if needed)
pkill -f "python.*backend"
pkill -f "npm.*dev"

# Start services again
./start_services.sh
```

## 📝 Next Steps

1. **Access the Frontend**: Open http://localhost:8080 in your browser
2. **Explore the API**: Test the endpoints at http://localhost:8000
3. **Monitor Logs**: Use `./monitor_logs.sh` to check status
4. **Development**: Make changes to the code and see them reflected immediately

## 🎉 Success!

The ConvoSphere AI Assistant Platform is now running successfully! You can:
- Access the web interface at http://localhost:8080
- Test the API at http://localhost:8000
- Monitor the services using the provided scripts

Enjoy exploring the platform! 🚀