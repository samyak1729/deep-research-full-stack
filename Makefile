.PHONY: help install dev backend frontend docker-build docker-up docker-down clean test lint format docs

# Default target
help:
	@echo "Deep Research - Fullstack App"
	@echo ""
	@echo "Available targets:"
	@echo "  make install        Install dependencies"
	@echo "  make dev            Run development servers (backend + frontend)"
	@echo "  make backend        Run backend only"
	@echo "  make frontend       Run frontend only"
	@echo "  make docker-build   Build Docker images"
	@echo "  make docker-up      Start Docker containers"
	@echo "  make docker-down    Stop Docker containers"
	@echo "  make docker-logs    View Docker logs"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linting"
	@echo "  make format         Format code"
	@echo "  make clean          Clean build artifacts"
	@echo "  make docs           Generate documentation"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	uv sync

install-pip:
	@echo "Installing with pip..."
	pip install -r requirements.txt

# Development
dev: backend frontend

backend:
	@echo "Starting backend server..."
	python app/backend/main.py

frontend:
	@echo "Starting frontend server..."
	streamlit run app/frontend/app.py

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up

docker-up-detached:
	@echo "Starting Docker containers (detached)..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html

# Linting & Formatting
lint:
	@echo "Running linting..."
	ruff check src/ app/

format:
	@echo "Formatting code..."
	ruff format src/ app/

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

# Documentation
docs:
	@echo "Available documentation:"
	@echo "  - README.md        Main project documentation"
	@echo "  - ARCHITECTURE.md  System architecture and design"
	@echo "  - QUICKSTART.md    Quick start guide"
	@echo "  - app/README.md    Frontend/Backend documentation"
	@echo ""

# API documentation
api-docs:
	@echo "API documentation available at:"
	@echo "  http://localhost:8000/docs"
	@echo ""

# Utilities
health-check:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not responding"

env-setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit with your API keys."; \
	else \
		echo ".env file already exists"; \
	fi

# Combined targets
setup: install env-setup
	@echo "✅ Setup complete!"

dev-full: setup dev
	@echo "✅ Development environment ready!"

production: docker-up
	@echo "✅ Production environment ready!"

requirements-update:
	@echo "Updating requirements.txt..."
	uv export > requirements.txt

.PHONY: help install install-pip dev backend frontend docker-build docker-up docker-up-detached docker-down docker-logs docker-clean test test-coverage lint format clean docs api-docs health-check env-setup setup dev-full production requirements-update
