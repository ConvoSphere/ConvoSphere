# AI Assistant Platform Makefile

.PHONY: help install dev test clean docker-up docker-down docker-build docker-logs migrate migrate-create format lint security-check docs-install docs-serve docs-build docs-deploy docs-clean pre-commit-install pre-commit-run pre-commit-update code-quality test-communication admin-cli admin-backup admin-health admin-config admin-test-data

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
	@echo "  code-quality   Run comprehensive code quality checks"
	@echo ""
	@echo "Pre-commit:"
	@echo "  pre-commit-install  Install pre-commit hooks"
	@echo "  pre-commit-run      Run pre-commit hooks on all files"
	@echo "  pre-commit-update   Update pre-commit hooks"
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
	@echo "Admin CLI:"
	@echo "  admin-cli      Show admin CLI help"
	@echo "  admin-backup   Create database backup"
	@echo "  admin-health   Check system health"
	@echo "  admin-config   Show configuration"
	@echo "  admin-test-data Create test data"
	@echo "  admin-debug    Run debug tools"
	@echo "  admin-monitor  Monitor containers"
	@echo "  admin-assistant Manage assistants"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean up temporary files"
	@echo "  test-communication Test frontend-backend communication"
	@echo "  help           Show this help message"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-install   Install documentation dependencies"
	@echo "  docs-serve     Serve documentation"
	@echo "  docs-build     Build documentation"
	@echo "  docs-deploy    Deploy documentation"
	@echo "  docs-clean     Clean documentation build files"

# Development
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -r docs/requirements-docs.txt

dev:
	@echo "Starting development environment..."
	docker-compose up -d postgres redis weaviate
	@echo "Starting backend..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	cd frontend-react && npm run dev

test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend-react && npm run test

format:
	@echo "Formatting code..."
	black backend/ frontend-react/
	isort backend/ frontend-react/

lint:
	@echo "Running linting..."
	ruff check backend/ frontend-react/
	black --check backend/ frontend-react/

security-check:
	@echo "Running security checks..."
	bandit -r backend/ frontend-react/ -f json -o bandit-report.json || true
	@echo "Security report saved to bandit-report.json"

code-quality:
	@echo "Running comprehensive code quality checks..."
	@echo "1. Formatting check..."
	black --check backend/ frontend-react/
	@echo "2. Linting check..."
	ruff check backend/ frontend-react/
	@echo "3. Import sorting check..."
	isort --check-only --diff backend/ frontend-react/
	@echo "4. Type checking..."
	mypy backend/ --ignore-missing-imports
	@echo "5. Security check..."
	bandit -r backend/ frontend-react/ -f json -o bandit-report.json || true
	@echo "Code quality checks completed!"

# Communication testing
test-communication:
	@echo "Testing frontend-backend communication..."
	./scripts/test-communication.sh

# Pre-commit hooks
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg

pre-commit-run:
	@echo "Running pre-commit hooks on all files..."
	pre-commit run --all-files

pre-commit-update:
	@echo "Updating pre-commit hooks..."
	pre-commit autoupdate

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

# Admin CLI Commands
admin-cli:
	@echo "ConvoSphere Admin CLI - Available Commands:"
	@echo ""
	@echo "Database Management:"
	@echo "  python3 admin.py db migrate"
	@echo "  python3 admin.py db status"
	@echo "  python3 admin.py db test-connection"
	@echo "  python3 admin.py db info"
	@echo "  python3 admin.py db reset"
	@echo "  python3 admin.py db clear-data"
	@echo ""
	@echo "User Management:"
	@echo "  python3 admin.py user create-admin"
	@echo "  python3 admin.py user list"
	@echo "  python3 admin.py user reset-password"
	@echo ""
	@echo "Backup & Recovery:"
	@echo "  python3 admin.py backup create"
	@echo "  python3 admin.py backup restore <file>"
	@echo "  python3 admin.py backup list"
	@echo ""
	@echo "Monitoring:"
	@echo "  python3 admin.py monitoring health"
	@echo "  python3 admin.py monitoring logs"
	@echo "  python3 admin.py monitoring containers"
	@echo ""
	@echo "Configuration:"
	@echo "  python3 admin.py config show"
	@echo "  python3 admin.py config validate"
	@echo ""
	@echo "Development:"
	@echo "  python3 admin.py dev test-data"
	@echo "  python3 admin.py dev quality-check"
	@echo "  python3 admin.py dev api-test"
	@echo ""
	@echo "Debug:"
	@echo "  python3 admin.py debug auth-flow"
	@echo "  python3 admin.py debug frontend-auth"
	@echo "  python3 admin.py debug test-auth-fix"
	@echo "  python3 admin.py debug test-frontend-auth"
	@echo ""
	@echo "Assistant Management:"
	@echo "  python3 admin.py assistant list"
	@echo "  python3 admin.py assistant create"
	@echo "  python3 admin.py assistant show <id>"
	@echo "  python3 admin.py assistant delete <id>"
	@echo "  python3 admin.py assistant activate <id>"
	@echo "  python3 admin.py assistant deactivate <id>"
	@echo ""
	@echo "For detailed help: python3 admin.py --help"

admin-backup:
	@echo "Creating database backup..."
	cd backend && python3 admin.py backup create

admin-health:
	@echo "Checking system health..."
	cd backend && python3 admin.py monitoring health

admin-config:
	@echo "Showing configuration..."
	cd backend && python3 admin.py config show

admin-test-data:
	@echo "Creating test data..."
	cd backend && python3 admin.py dev test-data

admin-debug:
	@echo "Available debug commands:"
	@echo "  python3 admin.py debug auth-flow"
	@echo "  python3 admin.py debug frontend-auth"
	@echo "  python3 admin.py debug test-auth-fix"
	@echo "  python3 admin.py debug test-frontend-auth"

admin-monitor:
	@echo "Starting container monitoring..."
	cd backend && python3 admin.py monitoring containers

admin-assistant:
	@echo "Available assistant commands:"
	@echo "  python3 admin.py assistant list"
	@echo "  python3 admin.py assistant create"
	@echo "  python3 admin.py assistant show <id>"
	@echo "  python3 admin.py assistant delete <id>"
	@echo "  python3 admin.py assistant activate <id>"
	@echo "  python3 admin.py assistant deactivate <id>"

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
	rm -rf htmlcov/
	rm -f bandit-report.json
	rm -f coverage.xml
	rm -rf .mypy_cache/

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
	make pre-commit-install
	make docker-up
	@echo "Waiting for services to start..."
	sleep 10
	make migrate
	@echo "Setup complete! Access the application at http://localhost:3000"

# Documentation
docs-install:
	pip install -r docs/requirements-docs.txt

docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

docs-deploy:
	mkdocs gh-deploy

docs-clean:
	rm -rf docs/site/

# Code quality reports
quality-report:
	@echo "Generating code quality report..."
	@echo "=== Code Quality Report ===" > quality-report.txt
	@echo "Generated: $(shell date)" >> quality-report.txt
	@echo "" >> quality-report.txt
	@echo "=== Ruff Linting ===" >> quality-report.txt
	ruff check backend/ frontend-react/ >> quality-report.txt 2>&1 || true
	@echo "" >> quality-report.txt
	@echo "=== Security Scan ===" >> quality-report.txt
	bandit -r backend/ frontend-react/ -f txt >> quality-report.txt 2>&1 || true
	@echo "" >> quality-report.txt
	@echo "=== Type Checking ===" >> quality-report.txt
	mypy backend/ --ignore-missing-imports >> quality-report.txt 2>&1 || true
	@echo "Quality report saved to quality-report.txt"

# Performance testing
performance-test:
	@echo "Running performance tests..."
	pytest --benchmark-only backend/tests/performance/ frontend-react/tests/performance/

# Coverage report
coverage-report:
	@echo "Generating coverage report..."
	pytest --cov=backend --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# All checks (for CI/CD)
all-checks: format lint security-check test coverage-report
	@echo "All checks completed successfully!" 