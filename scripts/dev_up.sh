#!/bin/bash
set -e

echo "🏎️  F1 Intelligence Hub - Development Startup"
echo "=============================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "📝 No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. You may want to review and customize it."
    echo ""
fi

# Create data directories if they don't exist
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed data/fastf1_cache models

# Build and start containers
echo ""
echo "🐳 Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
echo ""

docker compose up --build -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
echo "This typically takes 30-60 seconds..."
echo ""

# Function to check if a service is healthy
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker compose ps | grep $service | grep -q "healthy\|running"; then
            echo "✅ $service is ready"
            return 0
        fi
        echo "⏳ Waiting for $service... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ $service failed to start"
    return 1
}

# Check each service
check_health "postgres"
check_health "redis"
check_health "minio"

echo ""
echo "🎉 F1 Intelligence Hub is starting up!"
echo ""
echo "📍 Service URLs:"
echo "   🌐 Web UI:        http://localhost:3000"
echo "   🚀 API:           http://localhost:8000"
echo "   📚 API Docs:      http://localhost:8000/docs"
echo "   🗂️  MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "📋 Useful commands:"
echo "   make dev-logs    - View logs from all services"
echo "   make dev-down    - Stop all services"
echo "   make db-migrate  - Run database migrations"
echo "   make db-seed     - Seed demo data"
echo "   make help        - Show all available commands"
echo ""
echo "⚠️  Note: API and worker containers may take an additional 10-20 seconds"
echo "   to complete migrations and start serving requests."
echo ""
