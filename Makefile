.PHONY: help install install-dev lint lint-fix format check security test test-cov clean docker-build docker-up docker-down

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

lint: ## Run Ruff linter
	ruff check .

lint-fix: ## Run Ruff linter and auto-fix issues
	ruff check . --fix

format: ## Format code with Ruff
	ruff format .

check: ## Run all code quality checks
	@echo "Running Ruff linter..."
	ruff check .
	@echo "Running Bandit security check..."
	bandit -r backend/ -f json -o bandit-report.json || true
	@echo "Running MyPy type checker..."
	mypy backend/

security: ## Run security checks with Bandit
	bandit -r backend/ -f json -o bandit-report.json
	@echo "Security report generated: bandit-report.json"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=backend --cov-report=html --cov-report=term-missing

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f bandit-report.json

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

setup-dev: ## Setup development environment
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Activate virtual environment: source venv/bin/activate"
	@echo "Then run: make install-dev"

pre-commit: ## Run pre-commit checks
	make format
	make lint-fix
	make check
	make test

ci: ## Run CI pipeline
	make lint
	make security
	make test-cov 