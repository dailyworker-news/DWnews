#!/bin/bash
# Quick test runner for The Daily Worker

echo "=========================================="
echo "The Daily Worker - Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest not found. Installing..."
    pip install pytest pytest-cov
fi

echo "Running tests..."
echo ""

# Run all tests
pytest -v

echo ""
echo "=========================================="
echo "Test run complete!"
echo "=========================================="
echo ""
echo "For coverage report, run:"
echo "  pytest --cov --cov-report=html"
echo "  open htmlcov/index.html"
