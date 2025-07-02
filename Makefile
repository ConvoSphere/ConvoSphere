# AI Assistant Platform Makefile

.PHONY: help install dev test clean docker-up docker-down docker-build docker-logs migrate migrate-create format lint security-check

# Default target
help:
	@echo "AI Assistant Platform - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        Install all dependencies"
	@echo "  dev            Start development environment"
	@echo "  test           Run all tests"
	@echo "  format         Format code with black and isort"
	@echo "  lint           Run linting with ruff"
	@echo "  security-check Run security checks with bandit"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up      Start all services with Docker"
	@echo "  docker-down    Stop all Docker services"
	@echo "  docker-build   Build Docker images"
	@echo "  docker-logs    Show Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  migrate        Run database migrations"
	@echo "  migrate-create Create new migration"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean up temporary files"
	@echo "  help           Show this help message"

# Development
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -r backend/requirements.txt
	pip install -r frontend/requirements.txt

dev:
	@echo "Starting development environment..."
	docker-compose up -d postgres redis weaviate
	@echo "Starting backend..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	cd frontend && python -m main

test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend && pytest

format:
	@echo "Formatting code..."
	black backend/ frontend/
	isort backend/ frontend/

lint:
	@echo "Running linting..."
	ruff check backend/ frontend/
	ruff format --check backend/ frontend/

security-check:
	@echo "Running security checks..."
	bandit -r backend/
	bandit -r frontend/

# Docker
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Database
migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

migrate-create:
	@echo "Creating new migration..."
	cd backend && alembic revision --autogenerate -m "$(message)"

# Utilities
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf build/
	rm -rf dist/

# Production
prod-build:
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.prod.yml down

# Monitoring
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-weaviate:
	docker-compose logs -f weaviate

# Health checks
health:
	@echo "Checking service health..."
	@echo "Backend:"
	curl -f http://localhost:8000/health || echo "Backend not responding"
	@echo "Frontend:"
	curl -f http://localhost:3000 || echo "Frontend not responding"
	@echo "Weaviate:"
	curl -f http://localhost:8080/v1/.well-known/ready || echo "Weaviate not responding"

# Setup
setup:
	@echo "Setting up development environment..."
	cp env.example .env
	@echo "Please edit .env with your configuration"
	make install
	make docker-up
	@echo "Waiting for services to start..."
	sleep 10
	make migrate
	@echo "Setup complete! Access the application at http://localhost:3000" 