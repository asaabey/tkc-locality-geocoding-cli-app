#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CHC Geocoding Backend Server${NC}"
echo "======================================"

# Check if dependencies are installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting FastAPI server with uvicorn...${NC}"
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

# Start the backend server
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload