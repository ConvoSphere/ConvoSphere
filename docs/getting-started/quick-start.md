# Quick Start Guide

Get the AI Assistant Platform up and running in under 10 minutes! This guide will walk you through the complete setup process from scratch.

## 🎯 What You'll Learn

By the end of this guide, you'll have:
- ✅ A fully functional AI Assistant Platform
- ✅ All required services running (PostgreSQL, Redis, Weaviate)
- ✅ A working API with authentication
- ✅ Basic understanding of the platform architecture

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Docker** - [Download Docker](https://www.docker.com/products/docker-desktop/) (recommended)

### Required Services
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 6+** - [Download Redis](https://redis.io/download)
- **Weaviate** - [Weaviate Documentation](https://weaviate.io/developers/weaviate)

> **💡 Tip**: If you prefer to use Docker for all services, we provide a complete `docker-compose.yml` file that sets up everything automatically.

## 🚀 Quick Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/chatassistant.git

# Navigate to the project directory
cd chatassistant

# Verify the structure
ls -la
```

You should see the following structure:
```
chatassistant/
├── backend/          # FastAPI backend
├── frontend/         # NiceGUI frontend
├── docs/            # Documentation
├── docker/          # Docker configurations
├── docker-compose.yml
├── mkdocs.yml
└── README.md
```

### Step 2: Set Up Backend Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements-basic.txt
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the environment file with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/chatassistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080

# Security Configuration
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider Configuration (Optional for basic setup)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

> **🔒 Security Note**: Generate a strong secret key using:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### Step 4: Start Required Services

You have two options for starting the services:

#### Option A: Using Docker (Recommended)

```bash
# From the project root directory
docker-compose up -d postgres redis weaviate

# Verify services are running
docker-compose ps
```

#### Option B: Manual Installation

**PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE chatassistant;
CREATE USER chatassistant_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatassistant TO chatassistant_user;
\q
```

**Redis:**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

**Weaviate:**
```bash
# Using Docker (easiest method)
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:1.22.4
```

### Step 5: Initialize the Database

```bash
# Navigate back to the backend directory
cd backend

# Run database migrations
alembic upgrade head

# Create initial admin user (optional)
python scripts/create_admin.py
```

### Step 6: Start the Application

```bash
# Start the FastAPI application
python main.py
```

The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Step 7: Verify Installation

1. **Check API Health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API Documentation:**
   Open http://localhost:8000/docs in your browser

3. **Test Authentication:**
   ```bash
   # Register a new user
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpassword123"}'
   ```

## 🎉 Congratulations!

You've successfully set up the AI Assistant Platform! Here's what you can do next:

### Next Steps

1. **Explore the API Documentation**
   - Visit http://localhost:8000/docs
   - Try out the interactive API endpoints

2. **Set Up the Frontend**
   - Follow the [Frontend Setup Guide](../architecture/frontend.md)

3. **Configure AI Providers**
   - Add your OpenAI or Anthropic API keys
   - Test AI assistant creation

4. **Learn More**
   - Read the [Architecture Overview](../architecture/overview.md)
   - Explore [API Reference](../api/overview.md)
   - Check out [Features](../features/ai-integration.md)

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string
psql postgresql://username:password@localhost:5432/chatassistant
```

**Redis Connection Error:**
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

**Weaviate Connection Error:**
```bash
# Check if Weaviate container is running
docker ps | grep weaviate

# Check Weaviate logs
docker logs weaviate
```

**Port Already in Use:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Getting Help

- **Documentation**: Check the [API Reference](../api/overview.md) and [Architecture](../architecture/overview.md) sections
- **Issues**: Report problems on [GitHub Issues](https://github.com/your-org/chatassistant/issues)
- **Community**: Join our [Discord server](https://discord.gg/your-server)

## 📚 Additional Resources

- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Configuration Guide](configuration.md)** - Advanced configuration options
- **[Architecture Overview](../architecture/overview.md)** - System architecture details
- **[API Reference](../api/overview.md)** - Complete API documentation

---

<div align="center">

**Ready to build your first AI assistant?** [API Reference →](../api/overview.md)

</div> 