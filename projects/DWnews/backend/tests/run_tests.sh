#!/bin/bash

# Backend API Test Runner Script
# Run from projects/DWnews directory

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Daily Worker Backend API Tests${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${BLUE}Project root: ${NC}$PROJECT_ROOT"
echo ""

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-cov httpx"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT"

# Run tests based on arguments
if [ $# -eq 0 ]; then
    # No arguments - run all tests
    echo -e "${GREEN}Running all tests...${NC}"
    echo ""
    python3 -m pytest backend/tests/test_api_endpoints.py -v
elif [ "$1" = "coverage" ]; then
    # Generate coverage report
    echo -e "${GREEN}Running tests with coverage report...${NC}"
    echo ""
    python3 -m pytest backend/tests/test_api_endpoints.py --cov=backend --cov-report=term --cov-report=html
    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
elif [ "$1" = "quick" ]; then
    # Quick run without verbose output
    echo -e "${GREEN}Running quick test...${NC}"
    echo ""
    python3 -m pytest backend/tests/test_api_endpoints.py
elif [ "$1" = "class" ] && [ -n "$2" ]; then
    # Run specific test class
    echo -e "${GREEN}Running test class: $2${NC}"
    echo ""
    python3 -m pytest "backend/tests/test_api_endpoints.py::$2" -v
elif [ "$1" = "test" ] && [ -n "$2" ]; then
    # Run specific test
    echo -e "${GREEN}Running test: $2${NC}"
    echo ""
    python3 -m pytest "backend/tests/test_api_endpoints.py::$2" -v
else
    echo -e "${RED}Usage:${NC}"
    echo "  ./run_tests.sh                    # Run all tests"
    echo "  ./run_tests.sh quick              # Quick run (less verbose)"
    echo "  ./run_tests.sh coverage           # Run with coverage report"
    echo "  ./run_tests.sh class TestName     # Run specific test class"
    echo "  ./run_tests.sh test TestName::test_method  # Run specific test"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  ./run_tests.sh class TestArticlesEndpoints"
    echo "  ./run_tests.sh test TestArticlesEndpoints::test_get_articles_by_status"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Tests complete!${NC}"
echo -e "${GREEN}================================${NC}"
