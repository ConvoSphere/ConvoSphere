# Quick Start - Get Started in 5 Minutes

## 🚀 Quick Start with Docker

### 1. Clone Repository
```bash
git clone https://github.com/your-org/convosphere.git
cd convosphere
```

### 2. Start with Docker
```bash
docker-compose up --build
```

### 3. Open Browser
→ [http://localhost:5173](http://localhost:5173)

**That's it!** 🎉

## 📝 First Steps

### 1. Registration
- Click "Register" in the top right corner
- Fill out the form
- Confirm your email

### 2. First Conversation
- Click "New Chat" or "New Conversation"
- Type a message
- The AI will respond automatically

### 3. Use Knowledge Base
- Go to "Knowledge Base"
- Upload a PDF or DOCX file
- Ask the AI about the content

## 🔧 Alternative: Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Start Backend
```bash
# Backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

### Start Frontend
```bash
# Frontend directory
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
lsof -i :5173  # Frontend

# Use different ports
docker-compose -f docker-compose.yml -p convosphere up
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

- **GitHub Issues**: [Report Bug](https://github.com/your-org/convosphere/issues)
- **Discord**: [Community Support](https://discord.gg/your-server)
- **Documentation**: [Complete Guides](index.md)