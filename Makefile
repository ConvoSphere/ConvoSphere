# AI Assistant Platform Makefile

.PHONY: help install dev test clean docker-up docker-down docker-build docker-logs migrate migrate-create format lint security-check docs-install docs-serve docs-build docs-deploy docs-clean cli-install cli-users cli-database cli-services cli-deploy cli-health cli-config cli-logs

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
	@echo ""
	@echo "Documentation:"
	@echo "  docs-install   Install documentation dependencies"
	@echo "  docs-serve     Serve documentation"
	@echo "  docs-build     Build documentation"
	@echo "  docs-deploy    Deploy documentation"
	@echo "  docs-clean     Clean documentation build files"
	@echo ""
	@echo "CLI Management:"
	@echo "  cli-install    Install CLI tool dependencies"
	@echo "  cli-users      Manage users (list, create, update, delete)"
	@echo "  cli-database   Manage database (status, backup, restore)"
	@echo "  cli-services   Manage services (start, stop, status)"
	@echo "  cli-deploy     Deploy application (dev, staging, prod)"
	@echo "  cli-health     Check system health"
	@echo "  cli-config     Manage configuration"
	@echo "  cli-logs       Show application logs"

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

# Documentation
docs-install:
	cd docs && pip install -r requirements-docs.txt

docs-serve:
	cd docs && mkdocs serve

docs-build:
	cd docs && mkdocs build

docs-deploy:
	cd docs && mkdocs gh-deploy

docs-clean:
	rm -rf docs/site/

# CLI Management Tool
cli-install:
	@echo "Installing CLI tool dependencies..."
	pip install -r requirements-cli.txt
	chmod +x scripts/convosphere.py

cli-users:
	@echo "User management commands:"
	@echo "  make cli-users-list      - List all users"
	@echo "  make cli-users-create    - Create new user"
	@echo "  make cli-users-update    - Update user"
	@echo "  make cli-users-delete    - Delete user"

cli-users-list:
	python scripts/convosphere.py users list

cli-users-create:
	@echo "Usage: make cli-users-create EMAIL=user@example.com PASSWORD=secret123 ROLE=admin"
	python scripts/convosphere.py users create --email $(EMAIL) --password $(PASSWORD) --role $(ROLE)

cli-database:
	@echo "Database management commands:"
	@echo "  make cli-database-status  - Check database status"
	@echo "  make cli-database-backup  - Create database backup"
	@echo "  make cli-database-restore - Restore database from backup"
	@echo "  make cli-database-migrate - Run database migrations"

cli-database-status:
	python scripts/convosphere.py database status

cli-database-backup:
	python scripts/convosphere.py database backup

cli-database-restore:
	@echo "Usage: make cli-database-restore FILE=backup.sql"
	python scripts/convosphere.py database restore --file $(FILE)

cli-database-migrate:
	python scripts/convosphere.py database migrate

cli-services:
	@echo "Service management commands:"
	@echo "  make cli-services-status  - Show service status"
	@echo "  make cli-services-start   - Start all services"
	@echo "  make cli-services-stop    - Stop all services"
	@echo "  make cli-services-restart - Restart all services"

cli-services-status:
	python scripts/convosphere.py services status

cli-services-start:
	python scripts/convosphere.py services start

cli-services-stop:
	python scripts/convosphere.py services stop

cli-services-restart:
	python scripts/convosphere.py services restart

cli-deploy:
	@echo "Deployment commands:"
	@echo "  make cli-deploy-dev       - Deploy to development"
	@echo "  make cli-deploy-staging   - Deploy to staging"
	@echo "  make cli-deploy-prod      - Deploy to production"

cli-deploy-dev:
	python scripts/convosphere.py deploy dev

cli-deploy-staging:
	python scripts/convosphere.py deploy staging

cli-deploy-prod:
	python scripts/convosphere.py deploy prod

cli-health:
	python scripts/convosphere.py health --detailed

cli-config:
	@echo "Configuration commands:"
	@echo "  make cli-config-show      - Show current configuration"
	@echo "  make cli-config-set       - Set configuration value"

cli-config-show:
	python scripts/convosphere.py config show

cli-config-set:
	@echo "Usage: make cli-config-set KEY=DB_HOST VALUE=localhost"
	python scripts/convosphere.py config set --key $(KEY) --value $(VALUE)

cli-logs:
	@echo "Log commands:"
	@echo "  make cli-logs-all         - Show all logs"
	@echo "  make cli-logs-backend     - Show backend logs"
	@echo "  make cli-logs-frontend    - Show frontend logs"

cli-logs-all:
	python scripts/convosphere.py logs

cli-logs-backend:
	python scripts/convosphere.py logs --service backend

cli-logs-frontend:
	python scripts/convosphere.py logs --service frontend 