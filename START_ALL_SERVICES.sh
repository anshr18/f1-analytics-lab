#!/bin/bash

# Start All Services for F1 Analytics Lab
# This script checks and starts all required services

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     F1 Analytics Lab - Service Startup Script          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -n "Checking Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo ""
    echo "Starting Redis..."
    echo "Please run in a separate terminal:"
    echo -e "${YELLOW}redis-server${NC}"
    echo ""
    echo "Or with Homebrew:"
    echo -e "${YELLOW}brew services start redis${NC}"
    echo ""
    echo "Or with Docker:"
    echo -e "${YELLOW}docker run -d -p 6379:6379 redis:latest${NC}"
    echo ""
    exit 1
fi

# Check if PostgreSQL is running
echo -n "Checking PostgreSQL... "
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${YELLOW}⚠ Not detected (may be OK if using Docker)${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Ready to start services!"
echo ""
echo "Open 3 separate terminal windows and run:"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend API:${NC}"
echo "  cd apps/api"
echo "  uvicorn f1hub.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo -e "${YELLOW}Terminal 2 - Frontend:${NC}"
echo "  cd apps/web"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Terminal 3 - Race Replay (for testing):${NC}"
echo "  cd apps/api"
echo "  python3 replay_race.py"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Then open: ${GREEN}http://localhost:3000/live${NC}"
echo ""
