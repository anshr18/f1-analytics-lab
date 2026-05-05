#!/bin/bash
# Simple Backend Startup Script

echo "Starting F1 Analytics Backend..."
echo ""

# Activate venv
source .venv/bin/activate

# Go to API directory
cd apps/api

# Start without reload to avoid subprocess issues
echo "Starting server at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""

exec python -m uvicorn f1hub.main:app --host 0.0.0.0 --port 8000
