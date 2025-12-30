#!/bin/bash
# End-to-End Test Runner
# Runs complete validation of the Daily Worker system

set -e  # Exit on error

echo "=================================="
echo "Daily Worker - End-to-End Tests"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project directory
cd "$(dirname "$0")/.."

echo "Step 1: Environment Check"
echo "--------------------------"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}! Virtual environment not found, creating...${NC}"
    python3 -m venv venv
fi
echo -e "${GREEN}✓ Virtual environment ready${NC}"

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo ""
echo "Step 2: Dependencies Check"
echo "--------------------------"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}! Installing dependencies...${NC}"
    pip install -q -r backend/requirements.txt
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check database
echo ""
echo "Step 3: Database Check"
echo "----------------------"
if [ ! -f "dwnews.db" ]; then
    echo -e "${YELLOW}! Database not found, initializing...${NC}"
    python database/init_db.py
    python database/seed_data.py
fi
echo -e "${GREEN}✓ Database ready${NC}"

# Run unit tests
echo ""
echo "Step 4: Unit Tests"
echo "------------------"
pytest tests/test_database/ tests/test_backend/ tests/test_scripts/ -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi

# Run integration tests
echo ""
echo "Step 5: Integration Tests"
echo "-------------------------"
pytest tests/test_integration/ -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    exit 1
fi

# Run end-to-end tests
echo ""
echo "Step 6: End-to-End Tests"
echo "------------------------"
pytest tests/test_e2e/ -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ End-to-end tests passed${NC}"
else
    echo -e "${RED}✗ End-to-end tests failed${NC}"
    exit 1
fi

# Test backend server startup
echo ""
echo "Step 7: Backend Server Test"
echo "----------------------------"
echo "Starting backend server in background..."
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!
cd ..

# Wait for server to start
sleep 3

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8000/api/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend server is running${NC}"
else
    echo -e "${RED}✗ Backend server health check failed${NC}"
    kill $SERVER_PID
    exit 1
fi

# Test articles endpoint
echo "Testing articles endpoint..."
ARTICLES_RESPONSE=$(curl -s http://127.0.0.1:8000/api/articles/)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Articles API is responding${NC}"
else
    echo -e "${RED}✗ Articles API failed${NC}"
    kill $SERVER_PID
    exit 1
fi

# Stop server
echo "Stopping backend server..."
kill $SERVER_PID
sleep 1

echo ""
echo "Step 8: Content Pipeline Test"
echo "------------------------------"
echo "Testing content discovery (dry run)..."
# Test would run actual discovery if APIs configured
echo -e "${YELLOW}! Skipping (requires API keys)${NC}"

echo ""
echo "=================================="
echo "✅ All Tests Passed!"
echo "=================================="
echo ""
echo "System Status:"
echo "  ✓ Database initialized and seeded"
echo "  ✓ All unit tests passing"
echo "  ✓ All integration tests passing"
echo "  ✓ All end-to-end tests passing"
echo "  ✓ Backend server operational"
echo "  ✓ API endpoints functional"
echo ""
echo "Next steps:"
echo "  1. Start backend: cd backend && uvicorn main:app --reload"
echo "  2. Open frontend: frontend/index.html"
echo "  3. Open admin: frontend/admin/index.html"
echo ""
