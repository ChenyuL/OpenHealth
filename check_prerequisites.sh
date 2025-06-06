#!/bin/bash

# OpenHealth Prerequisites Checker
# Verifies all required tools and services are installed and configured

set -e

echo "🔍 OpenHealth Prerequisites Checker"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Function to check if command exists
check_command() {
    local cmd=$1
    local description=$2
    local required=${3:-true}
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "✅ ${GREEN}$description${NC} - $(command -v $cmd)"
        if [ "$cmd" = "node" ]; then
            echo "   Version: $(node --version)"
        elif [ "$cmd" = "npm" ]; then
            echo "   Version: $(npm --version)"
        elif [ "$cmd" = "python3" ]; then
            echo "   Version: $(python3 --version)"
        elif [ "$cmd" = "psql" ]; then
            echo "   Version: $(psql --version | head -n1)"
        fi
        ((PASS++))
        return 0
    else
        if [ "$required" = true ]; then
            echo -e "❌ ${RED}$description - NOT FOUND${NC}"
            ((FAIL++))
        else
            echo -e "⚠️  ${YELLOW}$description - NOT FOUND (Optional)${NC}"
            ((WARN++))
        fi
        return 1
    fi
}

# Function to check service status
check_service() {
    local service=$1
    local port=$2
    local description=$3
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "✅ ${GREEN}$description${NC} - Running on port $port"
        ((PASS++))
    else
        echo -e "⚠️  ${YELLOW}$description - Not running on port $port${NC}"
        ((WARN++))
    fi
}

# Function to check file exists
check_file() {
    local file=$1
    local description=$2
    local required=${3:-true}
    
    if [ -f "$file" ]; then
        echo -e "✅ ${GREEN}$description${NC} - Found"
        ((PASS++))
    else
        if [ "$required" = true ]; then
            echo -e "❌ ${RED}$description - NOT FOUND${NC}"
            ((FAIL++))
        else
            echo -e "⚠️  ${YELLOW}$description - NOT FOUND (Optional)${NC}"
            ((WARN++))
        fi
    fi
}

# Function to check directory exists
check_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "✅ ${GREEN}$description${NC} - Found"
        ((PASS++))
    else
        echo -e "❌ ${RED}$description - NOT FOUND${NC}"
        ((FAIL++))
    fi
}

# System Requirements
echo "🖥️  System Requirements"
echo "----------------------"
check_command "python3" "Python 3.8+"
check_command "node" "Node.js 16+"
check_command "npm" "NPM Package Manager"
echo ""

# Database Requirements
echo "🗄️  Database Requirements"
echo "-------------------------"
check_command "psql" "PostgreSQL Client"
check_command "redis-cli" "Redis Client" false
echo ""

# Development Tools
echo "🛠️  Development Tools"
echo "---------------------"
check_command "git" "Git Version Control"
check_command "curl" "cURL HTTP Client"
check_command "lsof" "Port Checker"
echo ""

# Project Structure
echo "📁 Project Structure"
echo "--------------------"
check_dir "shared-backend" "Shared Backend Directory"
check_dir "chat-system/web-interface" "Chat System Frontend"
check_dir "admin-dashboard/frontend" "Admin Dashboard Frontend"
check_dir "database" "Database Scripts Directory"
echo ""

# Configuration Files
echo "⚙️  Configuration Files"
echo "-----------------------"
check_file "shared-backend/.env" "Backend Environment File"
check_file "shared-backend/requirements.txt" "Backend Dependencies"
check_file "chat-system/web-interface/package.json" "Chat System Package Config"
check_file "admin-dashboard/frontend/package.json" "Admin Dashboard Package Config"
echo ""

# Dependencies Check
echo "📦 Dependencies Status"
echo "----------------------"

# Check Python virtual environment
if [ -d "shared-backend/venv" ]; then
    echo -e "✅ ${GREEN}Python Virtual Environment${NC} - Found"
    ((PASS++))
    
    # Check if FastAPI is installed
    if [ -f "shared-backend/venv/bin/python" ]; then
        if shared-backend/venv/bin/python -c "import fastapi" 2>/dev/null; then
            echo -e "✅ ${GREEN}Backend Dependencies${NC} - Installed"
            ((PASS++))
        else
            echo -e "❌ ${RED}Backend Dependencies${NC} - Not installed"
            ((FAIL++))
        fi
    fi
else
    echo -e "❌ ${RED}Python Virtual Environment${NC} - Not found"
    ((FAIL++))
fi

# Check Node modules
if [ -d "chat-system/web-interface/node_modules" ]; then
    echo -e "✅ ${GREEN}Chat System Dependencies${NC} - Installed"
    ((PASS++))
else
    echo -e "❌ ${RED}Chat System Dependencies${NC} - Not installed"
    ((FAIL++))
fi

if [ -d "admin-dashboard/frontend/node_modules" ]; then
    echo -e "✅ ${GREEN}Admin Dashboard Dependencies${NC} - Installed"
    ((PASS++))
else
    echo -e "❌ ${RED}Admin Dashboard Dependencies${NC} - Not installed"
    ((FAIL++))
fi

echo ""

# Services Status
echo "🚀 Services Status"
echo "------------------"
check_service "postgresql" 5432 "PostgreSQL Database"
check_service "redis" 6379 "Redis Cache" 
echo ""

# Port Availability
echo "🔌 Port Availability"
echo "--------------------"
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}Backend Port 8000${NC} - Available"
    ((PASS++))
else
    echo -e "⚠️  ${YELLOW}Backend Port 8000${NC} - In use"
    ((WARN++))
fi

if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}Chat Frontend Port 3000${NC} - Available"
    ((PASS++))
else
    echo -e "⚠️  ${YELLOW}Chat Frontend Port 3000${NC} - In use"
    ((WARN++))
fi

if ! lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}Admin Frontend Port 3001${NC} - Available"
    ((PASS++))
else
    echo -e "⚠️  ${YELLOW}Admin Frontend Port 3001${NC} - In use"
    ((WARN++))
fi

echo ""

# Environment Variables Check
echo "🔐 Environment Variables"
echo "-----------------------"
if [ -f "shared-backend/.env" ] && grep -q "ANTHROPIC_API_KEY=" shared-backend/.env; then
    if grep -q "your_anthropic_api_key_here" shared-backend/.env; then
        echo -e "⚠️  ${YELLOW}Anthropic API Key${NC} - Placeholder found (needs real key)"
        ((WARN++))
    else
        echo -e "✅ ${GREEN}Anthropic API Key${NC} - Configured"
        ((PASS++))
    fi
else
    echo -e "❌ ${RED}Anthropic API Key${NC} - Not configured"
    ((FAIL++))
fi

if [ -f "shared-backend/.env" ] && grep -q "OPENAI_API_KEY=" shared-backend/.env; then
    if grep -q "your_openai_api_key_here" shared-backend/.env; then
        echo -e "⚠️  ${YELLOW}OpenAI API Key${NC} - Placeholder found (needs real key)"
        ((WARN++))
    else
        echo -e "✅ ${GREEN}OpenAI API Key${NC} - Configured"
        ((PASS++))
    fi
else
    echo -e "❌ ${RED}OpenAI API Key${NC} - Not configured"
    ((FAIL++))
fi

echo ""

# Summary
echo "📊 Summary"
echo "----------"
echo -e "✅ ${GREEN}Passed: $PASS${NC}"
echo -e "⚠️  ${YELLOW}Warnings: $WARN${NC}"
echo -e "❌ ${RED}Failed: $FAIL${NC}"
echo ""

# Recommendations
if [ $FAIL -gt 0 ]; then
    echo -e "🔧 ${BLUE}Required Actions:${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo "   • Install Python 3.8+: https://python.org/downloads"
    fi
    
    if ! command -v node &> /dev/null; then
        echo "   • Install Node.js 16+: https://nodejs.org"
    fi
    
    if ! command -v psql &> /dev/null; then
        echo "   • Install PostgreSQL: https://postgresql.org/download"
        echo "     macOS: brew install postgresql"
        echo "     Ubuntu: sudo apt install postgresql postgresql-contrib"
    fi
    
    if [ ! -d "shared-backend/venv" ]; then
        echo "   • Create Python virtual environment: cd shared-backend && python3 -m venv venv"
    fi
    
    if [ ! -f "shared-backend/.env" ]; then
        echo "   • Copy environment template: cp shared-backend/.env.example shared-backend/.env"
    fi
    
    echo "   • Run setup script: python3 setup.py"
    echo ""
fi

if [ $WARN -gt 0 ]; then
    echo -e "💡 ${BLUE}Recommended Actions:${NC}"
    echo "   • Configure API keys in shared-backend/.env"
    echo "   • Start PostgreSQL service if not running"
    echo "   • Install Redis for better caching (optional)"
    echo ""
fi

if [ $FAIL -eq 0 ]; then
    echo -e "🎉 ${GREEN}System is ready! You can now run:${NC}"
    echo "   • ./start_all.sh (start all services)"
    echo "   • python3 setup.py (if first time setup needed)"
    echo "   • streamlit run streamlit_app.py (alternative interface)"
else
    echo -e "⛔ ${RED}System is not ready. Please address the failed checks above.${NC}"
    exit 1
fi

echo ""
echo "📚 Documentation: README.md"
echo "🐛 Issues: Check logs in terminal when running services"