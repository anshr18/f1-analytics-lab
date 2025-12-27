.PHONY: help dev-up dev-down dev-logs dev-restart db-migrate db-rollback db-seed db-shell api-shell worker-shell web-shell redis-shell minio-console test-api test-web lint format clean

# ============================================================================
# Help
# ============================================================================
help:
	@echo "F1 Intelligence Hub - Development Commands"
	@echo ""
	@echo "🚀 Docker Compose:"
	@echo "  make dev-up          - Start all services (detached)"
	@echo "  make dev-down        - Stop all services"
	@echo "  make dev-logs        - Tail logs from all services"
	@echo "  make dev-restart     - Restart all services"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make db-migrate      - Run database migrations"
	@echo "  make db-rollback     - Rollback last migration"
	@echo "  make db-seed         - Seed database with demo data"
	@echo "  make db-shell        - Open PostgreSQL shell"
	@echo ""
	@echo "🐚 Container Shells:"
	@echo "  make api-shell       - Open API container bash shell"
	@echo "  make worker-shell    - Open worker container bash shell"
	@echo "  make web-shell       - Open web container bash shell"
	@echo "  make redis-shell     - Open Redis CLI"
	@echo "  make minio-console   - Open MinIO console URL"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test-api        - Run API tests"
	@echo "  make test-web        - Run frontend tests"
	@echo ""
	@echo "🎨 Code Quality:"
	@echo "  make lint            - Lint all code (API + Web)"
	@echo "  make format          - Format all code (API + Web)"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean           - Remove all containers, volumes, and caches"

# ============================================================================
# Docker Compose - Development
# ============================================================================
dev-up:
	@echo "🚀 Starting F1 Intelligence Hub..."
	@bash scripts/dev_up.sh

dev-down:
	@echo "🛑 Stopping F1 Intelligence Hub..."
	@docker compose down

dev-logs:
	@docker compose logs -f

dev-restart:
	@echo "🔄 Restarting F1 Intelligence Hub..."
	@docker compose restart

# ============================================================================
# Database Operations
# ============================================================================
db-migrate:
	@echo "🗄️  Running database migrations..."
	@docker compose exec api alembic upgrade head

db-rollback:
	@echo "⏪ Rolling back last migration..."
	@docker compose exec api alembic downgrade -1

db-seed:
	@echo "🌱 Seeding database with demo data..."
	@docker compose exec api python /app/scripts/seed_demo_data.py

db-shell:
	@echo "🐘 Opening PostgreSQL shell..."
	@docker compose exec postgres psql -U f1hub -d f1hub

# ============================================================================
# Container Shells
# ============================================================================
api-shell:
	@docker compose exec api bash

worker-shell:
	@docker compose exec worker bash

web-shell:
	@docker compose exec web sh

redis-shell:
	@docker compose exec redis redis-cli

minio-console:
	@echo "🗂️  MinIO Console: http://localhost:9001"
	@echo "   User: minioadmin"
	@echo "   Password: minioadmin"

# ============================================================================
# Testing
# ============================================================================
test-api:
	@echo "🧪 Running API tests..."
	@docker compose exec api pytest

test-web:
	@echo "�� Running frontend tests..."
	@docker compose exec web npm test

# ============================================================================
# Code Quality
# ============================================================================
lint:
	@echo "🔍 Linting API..."
	@docker compose exec api ruff check .
	@echo "🔍 Linting Web..."
	@docker compose exec web npm run lint

format:
	@echo "🎨 Formatting API..."
	@docker compose exec api ruff format .
	@docker compose exec api black .
	@echo "🎨 Formatting Web..."
	@docker compose exec web npm run format

# ============================================================================
# Cleanup
# ============================================================================
clean:
	@echo "🧹 Cleaning up Docker resources..."
	@docker compose down -v --remove-orphans
	@echo "🧹 Removing Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "🧹 Removing Node modules cache..."
	@rm -rf apps/web/node_modules apps/web/.next 2>/dev/null || true
	@echo "✅ Cleanup complete!"
