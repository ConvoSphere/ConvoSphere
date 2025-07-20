# Installation Guide

This comprehensive installation guide covers all aspects of setting up the AI Assistant Platform, from development environments to production deployments.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Development Installation](#development-installation)
- [Production Installation](#production-installation)
- [Docker Installation](#docker-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## 🖥️ System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB free space
- **OS**: Linux, macOS, or Windows 10+

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **OS**: Ubuntu 20.04+, macOS 12+, or Windows 11+

### Software Dependencies
- **Python**: 3.13+
- **PostgreSQL**: 14+
- **Redis**: 6+
- **Docker**: 20.10+ (optional but recommended)

## 🚀 Installation Methods

Choose the installation method that best fits your needs:

| Method | Use Case | Complexity | Time |
|--------|----------|------------|------|
| [Docker](#docker-installation) | Production, Quick Start | Low | 5 minutes |
| [Development](#development-installation) | Development, Customization | Medium | 15 minutes |
| [Production](#production-installation) | Production, High Performance | High | 30 minutes |

## 🔧 Development Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/chatassistant.git
cd chatassistant

# Verify the clone
ls -la
```

### Step 2: Set Up Python Environment

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements-basic.txt

# For development, also install dev dependencies
pip install -r requirements-dev.txt
```

### Step 3: Install System Dependencies

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis
sudo apt install redis-server

# Install build dependencies
sudo apt install build-essential python3-dev libpq-dev
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql

# Install Redis
brew install redis

# Start services
brew services start postgresql
brew services start redis
```

#### Windows
```bash
# Install PostgreSQL from https://www.postgresql.org/download/windows/
# Install Redis from https://redis.io/download#redis-on-windows
# Or use WSL2 for a Linux-like environment
```

### Step 4: Configure Services

#### PostgreSQL Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE chatassistant;
CREATE USER chatassistant_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE chatassistant TO chatassistant_user;
ALTER USER chatassistant_user CREATEDB;
\q
```

#### Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

#### Weaviate Setup
```bash
# Using Docker (recommended)
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

# Verify Weaviate is running
curl http://localhost:8080/v1/.well-known/ready
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Environment Configuration:**

```env
# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql://chatassistant_user:your_secure_password@localhost:5432/chatassistant

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# WEAVIATE CONFIGURATION
# =============================================================================
WEAVIATE_URL=http://localhost:8080

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LITELLM_MODEL=openai/gpt-4

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# =============================================================================
# FILE UPLOAD
# =============================================================================
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,md
```

### Step 6: Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Create initial admin user
python scripts/create_admin.py
```

### Step 7: Start the Application

```bash
# Start the development server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🏭 Production Installation

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Install Docker (for Weaviate)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Step 2: Create Application User

```bash
# Create application user
sudo useradd -m -s /bin/bash chatassistant
sudo usermod -aG docker chatassistant

# Switch to application user
sudo su - chatassistant
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/your-org/chatassistant.git
cd chatassistant

# Set up Python environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

### Step 4: Configure Services

#### PostgreSQL Production Configuration
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/14/main/postgresql.conf

# Add/modify these settings:
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Redis Production Configuration
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add/modify these settings:
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Restart Redis
sudo systemctl restart redis-server
```

### Step 5: Set Up Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/chatassistant.service
```

**Service Configuration:**
```ini
[Unit]
Description=AI Assistant Platform
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=chatassistant
Group=chatassistant
WorkingDirectory=/home/chatassistant/chatassistant/backend
Environment=PATH=/home/chatassistant/chatassistant/backend/venv/bin
ExecStart=/home/chatassistant/chatassistant/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable chatassistant
sudo systemctl start chatassistant
```

### Step 6: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/chatassistant
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/chatassistant/chatassistant/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/chatassistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🐳 Docker Installation

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/chatassistant.git
cd chatassistant

# Configure environment
cp .env.example .env
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Manual Docker Setup

```bash
# Create network
docker network create chatassistant-network

# Start PostgreSQL
docker run -d \
  --name postgres \
  --network chatassistant-network \
  -e POSTGRES_DB=chatassistant \
  -e POSTGRES_USER=chatassistant \
  -e POSTGRES_PASSWORD=your_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# Start Redis
docker run -d \
  --name redis \
  --network chatassistant-network \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine

# Start Weaviate
docker run -d \
  --name weaviate \
  --network chatassistant-network \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:1.22.4

# Build and run application
docker build -t chatassistant .
docker run -d \
  --name chatassistant-app \
  --network chatassistant-network \
  -p 8000:8000 \
  --env-file .env \
  chatassistant
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `WEAVIATE_URL` | Weaviate server URL | - | Yes |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `DEBUG` | Debug mode | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `[]` | No |

### Security Configuration

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set up SSL certificates (production)
sudo certbot --nginx -d your-domain.com
```

### Performance Tuning

```bash
# PostgreSQL tuning
sudo nano /etc/postgresql/14/main/postgresql.conf

# Redis tuning
sudo nano /etc/redis/redis.conf

# Application tuning
# Adjust worker processes in systemd service
```

## ✅ Verification

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# Database connection test
curl http://localhost:8000/api/v1/health/database

# Redis connection test
curl http://localhost:8000/api/v1/health/redis

# Weaviate connection test
curl http://localhost:8000/api/v1/health/weaviate
```

### API Testing

```bash
# Test user registration
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'

# Test user login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/health
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U chatassistant_user -d chatassistant

# Check logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

#### Application Issues
```bash
# Check application logs
sudo journalctl -u chatassistant -f

# Check application status
sudo systemctl status chatassistant

# Restart application
sudo systemctl restart chatassistant
```

#### Docker Issues
```bash
# Check container status
docker ps -a

# Check container logs
docker logs chatassistant-app

# Restart containers
docker-compose restart
```

### Performance Issues

#### High Memory Usage
```bash
# Check memory usage
free -h

# Check PostgreSQL memory
ps aux | grep postgres

# Optimize PostgreSQL settings
sudo nano /etc/postgresql/14/main/postgresql.conf
```

#### Slow Response Times
```bash
# Check CPU usage
top

# Check disk I/O
iotop

# Check network connections
netstat -tulpn
```

### Getting Help

- **Documentation**: Check the [API Reference](../api/overview.md) and [Architecture](../architecture/overview.md) sections
- **Logs**: Check application and service logs for error messages
- **Issues**: Report problems on [GitHub Issues](https://github.com/your-org/chatassistant/issues)
- **Community**: Join our [Discord server](https://discord.gg/your-server)

## 📚 Next Steps

After successful installation:

1. **Configure AI Providers**: Add your OpenAI or Anthropic API keys
2. **Set Up Frontend**: Follow the [Frontend Setup Guide](../architecture/frontend.md)
3. **Create First Assistant**: Use the API to create your first AI assistant
4. **Explore Features**: Check out the [Features Documentation](../features/ai-integration.md)
5. **Monitor Performance**: Set up monitoring and alerting for production

---

<div align="center">

**Ready to configure your installation?** [Configuration Guide →](configuration.md)

</div> 