# Installation Guide

## Overview

This guide provides detailed installation instructions for the AI Assistant Platform in different environments.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for dependencies

### Required Services

- **PostgreSQL**: 13 or higher
- **Redis**: 6 or higher
- **Weaviate**: 1.19 or higher (optional, for vector search)

## Installation Methods

### 1. Local Development Installation

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/chatassistant.git
cd chatassistant
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install frontend dependencies
cd ../frontend
pip install -r requirements.txt
```

#### Step 4: Setup Environment Variables

Create `.env` file in the backend directory:

```bash
# Backend configuration
APP_NAME=AI Assistant Platform
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatassistant

# Redis
REDIS_URL=redis://localhost:6379

# Weaviate (optional)
WEAVIATE_URL=http://localhost:8080

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

#### Step 5: Setup Database

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE chatassistant;
CREATE USER chatassistant_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatassistant TO chatassistant_user;
\q

# Run migrations
cd backend
alembic upgrade head
```

#### Step 6: Setup Redis

```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Step 7: Run the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
python main.py
```

### 2. Docker Installation

#### Step 1: Install Docker

```bash
# Install Docker (Ubuntu/Debian)
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Clone and Run

```bash
git clone https://github.com/your-org/chatassistant.git
cd chatassistant

# Copy environment file
cp env.example .env

# Edit .env with your configuration
nano .env

# Start services
docker-compose up -d
```

#### Step 3: Verify Installation

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Production Installation

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql redis-server nginx
```

#### Step 2: Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash chatassistant
sudo su - chatassistant

# Clone repository
git clone https://github.com/your-org/chatassistant.git
cd chatassistant

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

#### Step 3: Database Setup

```bash
# Create database
sudo -u postgres createdb chatassistant
sudo -u postgres createuser chatassistant_user

# Set password
sudo -u postgres psql
ALTER USER chatassistant_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE chatassistant TO chatassistant_user;
\q
```

#### Step 4: Systemd Service

Create service file `/etc/systemd/system/chatassistant.service`:

```ini
[Unit]
Description=AI Assistant Platform
After=network.target

[Service]
Type=simple
User=chatassistant
WorkingDirectory=/home/chatassistant/chatassistant/backend
Environment=PATH=/home/chatassistant/chatassistant/venv/bin
ExecStart=/home/chatassistant/chatassistant/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/chatassistant`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Step 6: Enable Services

```bash
# Enable and start services
sudo systemctl enable chatassistant
sudo systemctl start chatassistant

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/chatassistant /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Verification

### Health Check

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "app_name": "AI Assistant Platform",
  "version": "1.0.0",
  "environment": "development"
}
```

### API Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend

Access the web interface:

- **Development**: http://localhost:8080
- **Production**: http://your-domain.com

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U chatassistant_user -d chatassistant
```

#### Redis Connection Error

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

#### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# System logs
sudo journalctl -u chatassistant -f

# Docker logs
docker-compose logs -f backend
```

## Next Steps

After successful installation:

1. **Configure AI Providers**: Add API keys for OpenAI, Anthropic, etc.
2. **Setup Users**: Create admin user and configure permissions
3. **Upload Documents**: Add documents to the knowledge base
4. **Configure Tools**: Setup MCP servers and external tools
5. **Monitor Performance**: Setup monitoring and alerting

## Support

For installation issues:

- **Documentation**: Check this guide and other documentation
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions 