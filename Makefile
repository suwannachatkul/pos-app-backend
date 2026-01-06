.PHONY: help dev test test-cov lint db-migrate db-upgrade db-downgrade clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development server
	docker-compose up --build

test: ## Run tests (brings up test DB)
	docker-compose up -d postgres_test
	docker-compose run --rm api pytest

test-cov: ## Run tests with coverage (brings up test DB)
	docker-compose up -d postgres_test
	docker-compose run --rm api pytest --cov=. --cov-report=html

lint: ## Run linter
	docker-compose run --rm api ruff check .

lint-fix: ## Run linter with auto-fix
	docker-compose run --rm api ruff check . --fix

db-migrate: ## Create a new migration (use message="description")
	docker-compose run --rm api alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply migrations
	docker-compose run --rm api alembic upgrade head

db-downgrade: ## Rollback one migration
	docker-compose run --rm api alembic downgrade -1

clean: ## Clean up containers and volumes
	docker-compose down -v
