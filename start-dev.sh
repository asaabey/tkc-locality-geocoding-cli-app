#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CHC Geocoding Web App Development Environment${NC}"
echo "========================================================"

# Check if backend dependencies are installed
echo -e "${YELLOW}Checking backend dependencies...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
echo -e "${YELLOW}Checking frontend dependencies...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

# Start backend in background
echo -e "${GREEN}Starting backend server...${NC}"
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend development server...${NC}"
cd frontend && npm run dev

# Cleanup when script exits
trap "echo -e '${YELLOW}Shutting down servers...${NC}'; kill $BACKEND_PID 2>/dev/null; exit" EXIT INT TERM