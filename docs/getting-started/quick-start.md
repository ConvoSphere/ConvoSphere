# Quick Start Guide

Get the AI Chat Application up and running in under 10 minutes! This guide will walk you through the fastest way to get started.

## 🎯 What You'll Build

By the end of this guide, you'll have:

- ✅ A fully functional AI chat application
- ✅ Real-time messaging with WebSocket support
- ✅ AI integration with multiple providers
- ✅ User authentication system
- ✅ File upload and knowledge base
- ✅ Modern React frontend with FastAPI backend

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for manual setup)
- **Node.js 18+** (for manual setup)
- **PostgreSQL 13+** (for manual setup)
- **Git**

### Quick Check

```bash
# Check if Docker is installed
docker --version
docker-compose --version

# Check Python version
python --version

# Check Node.js version
node --version
```

## 🚀 Option 1: Docker (Recommended)

The fastest way to get started is using Docker. This will set up everything automatically.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit the environment file with your settings
nano .env
```

**Key settings to configure:**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ai_chat_app

# Security
SECRET_KEY=your-super-secret-key-here

# AI Services (choose one or more)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# External Services
WEAVIATE_URL=http://localhost:8080
REDIS_URL=redis://localhost:6379
```

### Step 3: Start the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Step 4: Access the Application

Once all services are running, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

## 🛠️ Option 2: Manual Setup

If you prefer to set up the application manually, follow these steps:

### Step 1: Clone and Setup

```bash
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Set up database
createdb ai_chat_app
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend-react

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm start
```

## 🎉 First Steps

### 1. Create Your First User

Visit http://localhost:3000 and click "Sign Up" to create your account.

### 2. Start Your First Conversation

1. Click "New Conversation" in the chat interface
2. Type your first message
3. The AI will respond using the configured provider

### 3. Upload a Document

1. Click the file upload button in the chat
2. Select a PDF, DOCX, or text file
3. The document will be processed and added to your knowledge base

### 4. Explore the API

Visit http://localhost:8000/docs to explore the interactive API documentation.

## 🔧 Configuration Options

### AI Providers

The application supports multiple AI providers through LiteLLM:

```env
# OpenAI
OPENAI_API_KEY=your-openai-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint

# Custom providers
CUSTOM_API_KEY=your-custom-key
CUSTOM_API_BASE=your-custom-endpoint
```

### Database Configuration

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/ai_chat_app

# SQLite (for development)
DATABASE_URL=sqlite:///./ai_chat_app.db
```

### Security Settings

```env
# JWT Settings
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 🧪 Testing Your Setup

### Health Check

```bash
# Check if backend is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
```

### API Test

```bash
# Test authentication endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "password"}'
```

### Frontend Test

Visit http://localhost:3000 and verify:
- ✅ Page loads without errors
- ✅ Login/signup forms work
- ✅ Chat interface is responsive
- ✅ File upload works

## 🐛 Troubleshooting

### Common Issues

#### Docker Issues

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

#### Database Issues

```bash
# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Reset database
docker-compose down -v
docker-compose up --build
```

#### Port Conflicts

If ports are already in use:

```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000

# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Getting Help

- **Documentation**: Check the [User Guide](user-guide/getting-started.md)
- **API Docs**: Visit http://localhost:8000/docs
- **Issues**: Report problems on [GitHub](https://github.com/your-org/ai-chat-app/issues)
- **Discord**: Join our [community server](https://discord.gg/your-server)

## 🚀 Next Steps

Now that you have the application running, explore these features:

1. **[User Guide](user-guide/getting-started.md)** - Learn how to use the chat interface
2. **[API Reference](api/overview.md)** - Explore the complete API
3. **[Architecture](architecture/overview.md)** - Understand the system design
4. **[Deployment](deployment/docker.md)** - Deploy to production
5. **[Contributing](development/contributing.md)** - Help improve the project

## 📊 Performance Tips

### Development

- Use `docker-compose up --build` for the first run
- Use `docker-compose up -d` for subsequent runs
- Monitor logs with `docker-compose logs -f`

### Production

- Set `DEBUG=false` in environment
- Use proper database credentials
- Configure SSL/TLS certificates
- Set up monitoring and logging

---

**🎉 Congratulations!** You now have a fully functional AI chat application running. 

**Ready to explore more?** Check out the [User Guide](user-guide/getting-started.md) to learn how to use all the features! 