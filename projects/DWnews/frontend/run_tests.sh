#!/bin/bash

# Frontend Test Runner Script
# Run from projects/DWnews/frontend directory

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Daily Worker Frontend Tests${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo ""
fi

# Run tests based on arguments
if [ $# -eq 0 ]; then
    # No arguments - run all tests
    echo -e "${GREEN}Running all tests...${NC}"
    echo ""
    echo -e "${BLUE}1. Unit & Integration Tests${NC}"
    npm test
    echo ""
    echo -e "${BLUE}2. E2E Tests${NC}"
    echo -e "${YELLOW}Note: E2E tests require backend server running${NC}"
    npm run test:e2e || echo -e "${YELLOW}E2E tests skipped (backend may not be running)${NC}"

elif [ "$1" = "unit" ]; then
    echo -e "${GREEN}Running unit & integration tests...${NC}"
    echo ""
    npm test

elif [ "$1" = "e2e" ]; then
    echo -e "${GREEN}Running E2E tests...${NC}"
    echo ""
    npm run test:e2e

elif [ "$1" = "watch" ]; then
    echo -e "${GREEN}Running tests in watch mode...${NC}"
    echo ""
    npm run test:watch

elif [ "$1" = "coverage" ]; then
    echo -e "${GREEN}Running tests with coverage...${NC}"
    echo ""
    npm run test:coverage
    echo ""
    echo -e "${GREEN}Coverage report generated: coverage/index.html${NC}"

elif [ "$1" = "ui" ]; then
    echo -e "${GREEN}Running tests with UI...${NC}"
    echo ""
    npm run test:ui

elif [ "$1" = "lint" ]; then
    echo -e "${GREEN}Running linter...${NC}"
    echo ""
    npm run lint

elif [ "$1" = "format" ]; then
    echo -e "${GREEN}Checking code formatting...${NC}"
    echo ""
    npm run format:check

elif [ "$1" = "format:fix" ]; then
    echo -e "${GREEN}Fixing code formatting...${NC}"
    echo ""
    npm run format

elif [ "$1" = "build" ]; then
    echo -e "${GREEN}Building frontend...${NC}"
    echo ""
    npm run build

else
    echo -e "${RED}Usage:${NC}"
    echo "  ./run_tests.sh           # Run all tests"
    echo "  ./run_tests.sh unit      # Run unit & integration tests"
    echo "  ./run_tests.sh e2e       # Run E2E tests"
    echo "  ./run_tests.sh watch     # Run tests in watch mode"
    echo "  ./run_tests.sh coverage  # Run with coverage report"
    echo "  ./run_tests.sh ui        # Run with test UI"
    echo "  ./run_tests.sh lint      # Run linter"
    echo "  ./run_tests.sh format    # Check formatting"
    echo "  ./run_tests.sh format:fix # Fix formatting"
    echo "  ./run_tests.sh build     # Build frontend"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Tests complete!${NC}"
echo -e "${GREEN}================================${NC}"
