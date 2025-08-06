# Quick Start Guide

Get the AI Chat Application running in under 5 minutes.

## 🚀 Quick Start with Docker

### 1. Clone Repository
```bash
git clone https://github.com/ConvoSphere/ConvoSphere.git
cd ConvoSphere
```

### 2. Start Application
```bash
docker-compose up --build
```

### 3. Open Browser
→ [http://localhost:8081](http://localhost:8081)

> **⚠️ Beta Version**: This is currently version 0.1.0-beta. Some features may be incomplete or subject to change.

**That's it!** 🎉

## 📝 First Steps

### 1. Registration
- Click "Register" in the top right corner
- Fill out the registration form
- Confirm your email

### 2. First Conversation
- Click "New Chat" or "New Conversation"
- Type a message
- The AI will respond automatically

### 3. Use Knowledge Base
- Go to "Knowledge Base"
- Upload a PDF or DOCX file
- Ask the AI about the content

## 🔧 Manual Setup {#alternative-manual-setup}

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start backend
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend-react

# Install dependencies
npm install

# Start frontend
npm run dev
```

## 🐛 Common Issues

### Port Already in Use
```bash
# Check ports
lsof -i :8000  # Backend
lsof -i :8081  # Frontend

# Use different ports
docker-compose -f docker-compose.yml -p ai-chat-app up
```

### Docker Issues
```bash
# Restart Docker
docker system prune -a
docker-compose down
docker-compose up --build
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

## 📚 Next Steps

- **[User Guide](user-guide.md)** - Learn all features
- **[FAQ](faq.md)** - Common questions and solutions
- **[Developer Guide](developer-guide.md)** - For developers

## 🆘 Need Help?

- **GitHub Issues**: [Report Bug](https://github.com/ConvoSphere/ConvoSphere/issues)
- **Documentation**: [Complete Guides](index.md)