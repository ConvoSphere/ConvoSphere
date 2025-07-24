# Development Setup

This guide will help you set up the development environment for the AI Chat Application.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Docker** - [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download Git](https://git-scm.com/)

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lichtbaer/ai-chat-app.git
cd ai-chat-app
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_chat_app

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Redis (for caching and sessions)
REDIS_URL=redis://localhost:6379

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Database Setup

```bash
# Install PostgreSQL (if not already installed)
# On Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# On macOS with Homebrew:
brew install postgresql

# Create database
createdb ai_chat_app

# Run migrations
alembic upgrade head
```

### 5. Start Backend Services

```bash
# Start Redis (if not running)
redis-server

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

## Docker Setup (Alternative)

If you prefer to use Docker for development:

```bash
# Build and start all services
docker-compose up --build

# Or start specific services
docker-compose up backend frontend postgres redis
```

## Verification

1. **Backend API**: Visit `http://localhost:8000/docs` for the API documentation
2. **Frontend**: Visit `http://localhost:3000` for the web application
3. **Health Check**: Visit `http://localhost:8000/health` to verify backend status

## Common Issues

### Port Already in Use

If you get a "port already in use" error:

```bash
# Find process using the port
lsof -i :8000  # For backend
lsof -i :3000  # For frontend

# Kill the process
kill -9 <PID>
```

### Database Connection Issues

Ensure PostgreSQL is running and the database exists:

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Connect to PostgreSQL
psql -U postgres -d ai_chat_app
```

### Node Modules Issues

If you encounter issues with node modules:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- Read the [Testing Guide](testing.md) to learn how to run tests
- Check the [API Development Guide](api-development.md) for backend development
- Review the [Code Style Guide](code-style.md) for coding standards
- See the [Contributing Guide](contributing.md) for contribution guidelines