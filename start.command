#!/bin/bash
# ============================================
#  EngageShield — One-Click Startup Script
#  Double-click this file to start everything!
# ============================================

# Change to project directory (wherever this script lives)
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC}  🛡️  ${CYAN}EngageShield${NC} — Starting Up...             ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}  Intelligent Fake Engagement Detection       ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ---- Helper Functions ----
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed. Please install it first.${NC}"
        return 1
    fi
    return 0
}

wait_for_port() {
    local port=$1
    local name=$2
    local timeout=30
    local count=0
    while ! lsof -i :$port -sTCP:LISTEN &> /dev/null; do
        sleep 1
        count=$((count + 1))
        if [ $count -ge $timeout ]; then
            echo -e "${RED}❌ Timeout waiting for $name on port $port${NC}"
            return 1
        fi
    done
    echo -e "${GREEN}✅ $name is ready on port $port${NC}"
    return 0
}

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down EngageShield...${NC}"
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${CYAN}   Stopped backend (PID $BACKEND_PID)${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${CYAN}   Stopped frontend (PID $FRONTEND_PID)${NC}"
    fi
    
    # Stop Docker services
    if [ "$DOCKER_STARTED" = true ]; then
        echo -e "${CYAN}   Stopping Docker services...${NC}"
        docker compose stop postgres redis 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ EngageShield stopped. Goodbye!${NC}"
    echo ""
    exit 0
}

# Trap Ctrl+C and terminal close
trap cleanup EXIT INT TERM

# ---- Pre-flight Checks ----
echo -e "${CYAN}[1/6] Pre-flight checks...${NC}"

MISSING=false
for cmd in python3 node npm; do
    if ! check_command $cmd; then
        MISSING=true
    fi
done

if [ "$MISSING" = true ]; then
    echo ""
    echo -e "${RED}Please install missing dependencies and try again.${NC}"
    echo -e "${YELLOW}  • Python 3: https://www.python.org/downloads/${NC}"
    echo -e "${YELLOW}  • Node.js:  https://nodejs.org/${NC}"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}   All dependencies found ✓${NC}"

# ---- Start Database & Redis ----
echo ""
echo -e "${CYAN}[2/6] Starting PostgreSQL & Redis...${NC}"

DOCKER_STARTED=false
if check_command docker; then
    if docker info &> /dev/null; then
        docker compose up -d postgres redis 2>/dev/null
        if [ $? -eq 0 ]; then
            DOCKER_STARTED=true
            echo -e "${GREEN}   Docker services started ✓${NC}"
            sleep 3  # Wait for databases to initialize
        else
            echo -e "${YELLOW}   ⚠️  Docker compose failed. Using existing DB if available.${NC}"
        fi
    else
        echo -e "${YELLOW}   ⚠️  Docker is installed but not running. Start Docker Desktop first.${NC}"
        echo -e "${YELLOW}       Or ensure PostgreSQL & Redis are running locally.${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Docker not found. Ensure PostgreSQL (5432) & Redis (6379) are running.${NC}"
fi

# ---- Setup Backend ----
echo ""
echo -e "${CYAN}[3/6] Setting up backend...${NC}"

cd "$PROJECT_DIR/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${CYAN}   Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "${CYAN}   Installing Python dependencies (first run)...${NC}"
    pip install -r requirements.txt --quiet 2>&1 | tail -1
    touch venv/.deps_installed
    echo -e "${GREEN}   Dependencies installed ✓${NC}"
else
    echo -e "${GREEN}   Dependencies already installed ✓${NC}"
fi

# ---- Start Backend ----
echo ""
echo -e "${CYAN}[4/6] Starting FastAPI backend...${NC}"

export DATABASE_URL="postgresql+asyncpg://engageshield:engageshield_dev_pw@localhost:5432/engageshield"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export CORS_ORIGINS='["http://localhost:5173","http://localhost:3000"]'

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${CYAN}   Backend starting (PID $BACKEND_PID)...${NC}"

# ---- Setup & Start Frontend ----
echo ""
echo -e "${CYAN}[5/6] Setting up frontend...${NC}"

cd "$PROJECT_DIR/frontend"

# Install node modules if needed
if [ ! -d "node_modules" ]; then
    echo -e "${CYAN}   Installing npm dependencies (first run)...${NC}"
    npm install --silent 2>&1 | tail -1
    echo -e "${GREEN}   Dependencies installed ✓${NC}"
else
    echo -e "${GREEN}   Dependencies already installed ✓${NC}"
fi

echo ""
echo -e "${CYAN}[6/6] Starting React frontend...${NC}"

npm run dev &
FRONTEND_PID=$!
echo -e "${CYAN}   Frontend starting (PID $FRONTEND_PID)...${NC}"

# ---- Wait for services ----
echo ""
echo -e "${CYAN}Waiting for services to be ready...${NC}"
wait_for_port 8000 "Backend API"
wait_for_port 5173 "Frontend Dev Server"

# ---- Open Browser ----
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC}  🚀 ${GREEN}EngageShield is running!${NC}                   ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}                                              ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}  🌐 Frontend:  ${CYAN}http://localhost:5173${NC}          ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}  🔌 Backend:   ${CYAN}http://localhost:8000${NC}          ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}  📚 API Docs:  ${CYAN}http://localhost:8000/docs${NC}     ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}                                              ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}  Press ${YELLOW}Ctrl+C${NC} to stop all services           ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Open browser
if command -v open &> /dev/null; then
    sleep 1
    open "http://localhost:5173"
elif command -v xdg-open &> /dev/null; then
    sleep 1
    xdg-open "http://localhost:5173"
fi

# Keep script running until Ctrl+C
wait
