#!/bin/bash
# Start script for Deep Research fullstack app

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your API keys, then run this script again.${NC}"
    exit 1
fi

# Source environment variables
export $(cat .env | xargs)

# Check if API keys are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$TAVILY_API_KEY" ]; then
    echo -e "${YELLOW}❌ API keys not set in .env file${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting Deep Research Fullstack App${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Stopping services...${NC}"
    pkill -f "python app/backend/main.py" || true
    pkill -f "streamlit run app/frontend/app.py" || true
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Start backend
echo -e "${BLUE}Starting backend...${NC}"
python app/backend/main.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Wait for backend to be ready
echo -e "${BLUE}Waiting for backend to be healthy...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}❌ Backend health check timeout${NC}"
    fi
    sleep 1
done

echo ""

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
streamlit run app/frontend/app.py &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo -e "  Frontend: ${BLUE}http://localhost:8501${NC}"
echo -e "  Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for signals
wait
