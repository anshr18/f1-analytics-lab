#!/bin/bash
set -e

echo "🛑 Stopping F1 Intelligence Hub..."
echo ""

# Stop containers
docker compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 Tip: To remove all data volumes as well, run:"
echo "   docker compose down -v"
echo ""
echo "   Or use: make clean"
echo ""
