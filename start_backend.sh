#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Starting F1 Analytics Backend API             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Navigate to the project root
cd "$(dirname "$0")"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies if needed
echo "Installing dependencies..."
pip install -q -e apps/api

# Navigate to API directory
cd apps/api

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f ../../.env ]; then
        cp ../../.env .env
    else
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/f1hub" > .env
        echo "REDIS_URL=redis://localhost:6379/0" >> .env
        echo "CORS_ORIGINS=http://localhost:3000" >> .env
    fi
fi

echo ""
echo "Starting Uvicorn server..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn f1hub.main:app --reload --host 0.0.0.0 --port 8000
