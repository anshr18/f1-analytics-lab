#!/bin/bash

# Test Feature Computation for F1 Intelligence Hub
echo "========================================"
echo "Testing Feature Computation System"
echo "========================================"
echo ""

# Get session ID
echo "1. Fetching available sessions..."
SESSION_ID=$(curl -s "http://localhost:8000/api/v1/sessions" | jq -r '.sessions[0].id')
echo "   Using session: $SESSION_ID"
echo ""

# Check current feature status
echo "2. Checking current feature status..."
curl -s "http://localhost:8000/api/v1/features/status/$SESSION_ID" | jq '.'
echo ""

# Compute features (if not already done)
echo "3. Computing features..."
curl -X POST "http://localhost:8000/api/v1/features/compute/$SESSION_ID" | jq '.'
echo ""

# Verify features were created
echo "4. Verifying features..."
curl -s "http://localhost:8000/api/v1/features/status/$SESSION_ID" | jq '.'
echo ""

echo "========================================"
echo "Test Complete!"
echo "========================================"
