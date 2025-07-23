# Installation Guide

This guide provides detailed instructions for installing the AI Chat Application on different platforms and environments.

## Prerequisites

Before installing the AI Chat Application, ensure you have the following prerequisites:

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 18.0 or higher
- **Docker**: 20.10 or higher (for containerized deployment)
- **Git**: Latest version

### Hardware Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 10GB free space
- **CPU**: Multi-core processor recommended

## Installation Methods

### Method 1: Docker Installation (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app

# Copy environment configuration
cp .env.example .env

# Edit environment variables
nano .env

# Start the application
docker-compose up -d
```

### Method 2: Manual Installation

#### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Method 3: Production Installation

For production deployment, follow these steps:

```bash
# Clone the repository
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app

# Set up production environment
cp .env.example .env.production
nano .env.production

# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

### Environment Variables

Key environment variables to configure:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ai_chat_db
REDIS_URL=redis://localhost:6379

# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Application Settings
DEBUG=False
ENVIRONMENT=production
```

### Database Setup

#### PostgreSQL

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE ai_chat_db;
CREATE USER ai_chat_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_chat_db TO ai_chat_user;
\q
```

#### Redis

```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## Verification

After installation, verify that everything is working:

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Check Frontend

Open your browser and navigate to `http://localhost:3000` (or the configured frontend URL).

### Check Database Connection

```bash
# Test database connection
python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

#### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U ai_chat_user -d ai_chat_db
```

#### Docker Issues

```bash
# Check Docker status
docker system info

# Clean up Docker resources
docker system prune -a

# Restart Docker service
sudo systemctl restart docker
```

### Logs

Check application logs for debugging:

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres
```

## Next Steps

After successful installation:

1. **Configure AI Providers**: Set up your API keys for OpenAI, Anthropic, or other AI providers
2. **Set Up Authentication**: Configure user authentication and authorization
3. **Customize Settings**: Adjust application settings for your environment
4. **Set Up Monitoring**: Configure logging and monitoring tools
5. **Backup Strategy**: Implement database backup procedures

## Support

If you encounter issues during installation:

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [FAQ](../user-guide/faq.md)
- Open an issue on [GitHub](https://github.com/your-org/ai-chat-app/issues)
- Join our [Discord community](https://discord.gg/your-server) 