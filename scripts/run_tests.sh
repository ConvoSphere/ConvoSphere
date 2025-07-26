#!/bin/bash

# Unified Test Runner for ConvoSphere
# This script runs tests from the consolidated test structure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default values
TEST_TYPE="all"
PARALLEL=false
COVERAGE=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --type TYPE       Test type: all, unit, integration, e2e, performance, security"
            echo "  --parallel        Run tests in parallel"
            echo "  --no-coverage     Disable coverage reporting"
            echo "  --verbose         Verbose output"
            echo "  --help            Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python3 -m pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=backend/app --cov=frontend-react/src --cov-report=term-missing --cov-report=html:htmlcov"
fi

# Select test path based on type
case $TEST_TYPE in
    "all")
        TEST_PATH="tests/"
        ;;
    "unit")
        TEST_PATH="tests/unit/"
        ;;
    "integration")
        TEST_PATH="tests/integration/"
        ;;
    "e2e")
        TEST_PATH="tests/e2e/"
        ;;
    "performance")
        TEST_PATH="tests/performance/"
        ;;
    "security")
        TEST_PATH="tests/security/"
        ;;
    "backend")
        TEST_PATH="tests/unit/backend/ tests/integration/backend/"
        ;;
    "frontend")
        TEST_PATH="tests/unit/frontend/ tests/integration/frontend/"
        ;;
    *)
        echo "Unknown test type: $TEST_TYPE"
        exit 1
        ;;
esac

print_status "Running $TEST_TYPE tests..."
print_status "Command: $PYTEST_CMD $TEST_PATH"

# Run tests
if $PYTEST_CMD $TEST_PATH; then
    print_success "All tests passed!"
else
    print_warning "Some tests failed. Check the output above."
    exit 1
fi