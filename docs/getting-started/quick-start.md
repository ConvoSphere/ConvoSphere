# Quick Start Guide

Get the AI Assistant Platform up and running in under 10 minutes!

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 6+** - [Download Redis](https://redis.io/download)
- **Weaviate** - [Weaviate Documentation](https://weaviate.io/developers/weaviate)

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/chatassistant.git
cd chatassistant
```

### 2. Set Up Backend Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements-basic.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit the environment file with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatassistant

# Redis
REDIS_URL=redis://localhost:6379/0

# Weaviate
WEAVIATE_URL=http://localhost:8080

# Security
SECRET_KEY=your-secret-key-here
```

### 4. Start Required Services

Make sure your services are running:

```bash
# PostgreSQL (example for Ubuntu/Debian)
sudo systemctl start postgresql

# Redis (example for Ubuntu/Debian)
sudo systemctl start redis-server

# Weaviate (using Docker)
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

### 5. Start the Application

```bash
# Start the FastAPI application
python main.py
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ✅ Verify Installation

### Check Health Status

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX",
  "version": "1.0.0"
}
```

### Check Detailed Health

```bash
curl http://localhost:8000/api/v1/health/detailed
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "connected",
      "response_time": "0.002s"
    },
    "redis": {
      "status": "connected",
      "response_time": "0.001s"
    },
    "weaviate": {
      "status": "connected",
      "response_time": "0.015s"
    }
  }
}
```

### Test API Documentation

Visit http://localhost:8000/docs to see the interactive API documentation.

## 🧪 Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_health.py -v
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_database.py -v
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error**: `Connection refused` or `database does not exist`

**Solution**:
```bash
# Create database
sudo -u postgres createdb chatassistant

# Or connect to PostgreSQL and create manually
sudo -u postgres psql
CREATE DATABASE chatassistant;
\q
```

#### 2. Redis Connection Error

**Error**: `Connection refused`

**Solution**:
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start Redis if not running
sudo systemctl start redis-server
```

#### 3. Weaviate Connection Error

**Error**: `Connection refused`

**Solution**:
```bash
# Check if Weaviate container is running
docker ps | grep weaviate

# Start Weaviate if not running
docker start weaviate
```

#### 4. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 5. Virtual Environment Issues

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-basic.txt
```

### Getting Help

If you're still having issues:

1. **Check the logs**: Look for error messages in the terminal
2. **Verify services**: Ensure PostgreSQL, Redis, and Weaviate are running
3. **Check configuration**: Verify your `.env` file has correct settings
4. **Search issues**: Check [GitHub Issues](https://github.com/your-org/chatassistant/issues)
5. **Ask for help**: Join our [Discord server](https://discord.gg/your-server)

## 🎯 Next Steps

Now that you have the basic setup running:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Documentation**: Check out the [Architecture Overview](architecture/overview.md)
3. **Run Tests**: Ensure everything is working with `python -m pytest tests/ -v`
4. **Configure Development**: Set up your development environment following the [Development Setup](development/setup.md) guide

## 📚 Additional Resources

- [Installation Guide](installation.md) - Detailed installation instructions
- [Configuration Guide](configuration.md) - Environment and service configuration
- [Development Setup](development/setup.md) - Setting up for development
- [Testing Guide](development/testing.md) - Running and writing tests 