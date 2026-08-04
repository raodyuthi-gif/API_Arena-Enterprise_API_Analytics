.PHONY: help dev-backend dev-frontend test lint migrate build up down clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────
dev-backend:  ## Run FastAPI backend with hot-reload
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:  ## Run Vite frontend dev server
	cd frontend && npm run dev

# ──────────────────────────────────────────────
# Docker Compose
# ──────────────────────────────────────────────
up:  ## Start all services (Docker Compose)
	docker-compose up --build -d

down:  ## Stop all services
	docker-compose down

logs:  ## Tail backend logs
	docker-compose logs -f backend

# ──────────────────────────────────────────────
# Database / Migrations
# ──────────────────────────────────────────────
migrate:  ## Run Alembic migrations (upgrade head)
	cd backend && alembic upgrade head

migrate-down:  ## Rollback last migration
	cd backend && alembic downgrade -1

migration:  ## Create a new migration (usage: make migration MSG="add xyz table")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed:  ## Seed synthetic historical telemetry for ML training/demo (usage: make seed DAYS=30 APIS=3)
	cd backend && python ../scripts/seed_synthetic_traffic.py --days $(or $(DAYS),30) --apis $(or $(APIS),3)

# ──────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────
test:  ## Run all tests with coverage
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit:  ## Run unit tests only
	cd backend && pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	cd backend && pytest tests/integration/ -v

# ──────────────────────────────────────────────
# Code Quality
# ──────────────────────────────────────────────
lint:  ## Run ruff linter
	cd backend && ruff check app/ tests/

lint-fix:  ## Auto-fix lint issues
	cd backend && ruff check --fix app/ tests/

format:  ## Format code with black
	cd backend && black app/ tests/

typecheck:  ## Run mypy type checking
	cd backend && mypy app/

# ──────────────────────────────────────────────
# Build
# ──────────────────────────────────────────────
build:  ## Build Docker images
	docker-compose build

build-prod:  ## Build production Docker images
	docker-compose -f docker-compose.prod.yml build

# ──────────────────────────────────────────────
# Kubernetes / Helm
# ──────────────────────────────────────────────
k8s-dev:  ## Deploy to K8s dev environment
	kubectl apply -k k8s/overlays/dev/

k8s-prod:  ## Deploy to K8s prod environment
	kubectl apply -k k8s/overlays/prod/

helm-install:  ## Install Helm chart
	helm upgrade --install api-analytics ./helm/api-analytics \
		--namespace api-analytics \
		--create-namespace \
		-f helm/api-analytics/values.yaml

helm-uninstall:  ## Uninstall Helm chart
	helm uninstall api-analytics --namespace api-analytics

# ──────────────────────────────────────────────
# Cleanup
# ──────────────────────────────────────────────
clean:  ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
	rm -rf backend/htmlcov
	rm -rf frontend/dist frontend/node_modules/.vite
