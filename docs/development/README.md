# Development Guide

This section contains essential development resources for the ConvoSphere project.

## 📚 Development Resources

### **Design & UI**
- **[Design System](DESIGN_SYSTEM.md)** - UI/UX design guidelines and component library
- **[Export Features](EXTENDED_EXPORT_FEATURES.md)** - Advanced export functionality and customization

### **Architecture & Implementation**
- **[Service Refactoring](service_refactoring_summary.md)** - Service layer refactoring documentation

## 🔧 Development Setup

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL
- Redis

### **Quick Setup**
```bash
# Clone and setup
git clone https://github.com/ConvoSphere/ConvoSphere.git
cd ConvoSphere

# Start with Docker
docker-compose up --build
```

### **Manual Setup**
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend-react
npm install
npm run dev
```

## 🧪 Testing

### **Backend Testing**
```bash
cd backend
pytest
```

### **Frontend Testing**
```bash
cd frontend-react
npm test
```

### **End-to-End Testing**
```bash
npm run test:e2e
```

## 📋 Development Standards

### **Code Quality**
- Type safety with MyPy
- Code formatting with Ruff
- Security scanning with Bandit
- Comprehensive test coverage

### **Documentation**
- API documentation with FastAPI
- Code comments and docstrings
- Architecture documentation
- User and developer guides

### **Git Workflow**
- Feature branches
- Pull request reviews
- Automated testing
- Documentation updates

## 🚀 Deployment

### **Development**
```bash
docker-compose up --build
```

### **Production**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📖 Additional Resources

- **[Main Documentation](../index.md)** - Complete project documentation
- **[API Reference](../api.md)** - API documentation
- **[Architecture](../architecture.md)** - System architecture
- **[Security](../security.md)** - Security guidelines