#!/bin/bash

# OpenHealth Quick Initialization Script
# This script sets up the OpenHealth platform quickly

set -e  # Exit on any error

echo "🏥 OpenHealth Platform - Quick Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "setup.py" ]]; then
    print_error "Please run this script from the OpenHealth root directory"
    exit 1
fi

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    print_status "Python 3 found: $(python3 --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    print_status "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    print_status "npm found: $(npm --version)"
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL client (psql) not found in PATH"
        print_info "Please ensure PostgreSQL is installed and running"
    else
        print_status "PostgreSQL client found"
    fi
}

# Create required directories
create_directories() {
    print_info "Creating required directories..."
    
    # Shared backend directories
    mkdir -p shared-backend/uploads
    mkdir -p shared-backend/logs
    
    # Frontend source directories
    mkdir -p chat-system/web-interface/src/components/Layout
    mkdir -p chat-system/web-interface/src/components/Auth
    mkdir -p chat-system/web-interface/src/components/User
    mkdir -p chat-system/web-interface/src/contexts
    mkdir -p chat-system/web-interface/src/services
    mkdir -p chat-system/web-interface/src/hooks
    mkdir -p chat-system/web-interface/src/utils
    
    mkdir -p admin-dashboard/frontend/src/components/Layout
    mkdir -p admin-dashboard/frontend/src/components/Dashboard
    mkdir -p admin-dashboard/frontend/src/components/Conversations
    mkdir -p admin-dashboard/frontend/src/components/Ventures
    mkdir -p admin-dashboard/frontend/src/components/Analytics
    mkdir -p admin-dashboard/frontend/src/components/Auth
    mkdir -p admin-dashboard/frontend/src/contexts
    mkdir -p admin-dashboard/frontend/src/services
    
    print_status "Directories created"
}

# Install Python dependencies
setup_backend() {
    print_info "Setting up backend..."
    
    cd shared-backend
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install basic dependencies
    print_info "Installing Python dependencies..."
    pip install fastapi uvicorn anthropic openai psycopg2-binary python-jose passlib bcrypt python-multipart aiofiles sqlalchemy alembic redis python-dotenv loguru pydantic-settings email-validator
    
    # Create requirements.txt
    pip freeze > requirements.txt
    
    cd ..
    print_status "Backend setup complete"
}

# Initialize database
setup_database() {
    print_info "Setting up database..."
    
    # Check if PostgreSQL is running
    if pg_isready -q; then
        print_status "PostgreSQL is running"
        
        # Run database initialization
        python3 database/init_db.py
        print_status "Database initialized"
    else
        print_warning "PostgreSQL is not running"
        print_info "Please start PostgreSQL manually:"
        print_info "  macOS: brew services start postgresql"
        print_info "  Linux: sudo systemctl start postgresql"
        print_info "Then run: python3 database/init_db.py"
    fi
}

# Install frontend dependencies
setup_frontends() {
    print_info "Setting up frontend dependencies..."
    
    # Chat system frontend
    if [[ -f "chat-system/web-interface/package.json" ]]; then
        print_info "Installing chat system dependencies..."
        cd chat-system/web-interface
        npm install --silent
        cd ../..
        print_status "Chat system dependencies installed"
    fi
    
    # Admin dashboard frontend
    if [[ -f "admin-dashboard/frontend/package.json" ]]; then
        print_info "Installing admin dashboard dependencies..."
        cd admin-dashboard/frontend
        npm install --silent
        cd ../..
        print_status "Admin dashboard dependencies installed"
    fi
}

# Create startup scripts
create_scripts() {
    print_info "Creating startup scripts..."
    
    # Make existing scripts executable
    chmod +x start_*.sh 2>/dev/null || true
    
    # Create a quick dev script
    cat > quick_start.sh << 'EOF'
#!/bin/bash

echo "🚀 OpenHealth Quick Start"
echo "========================="

# Check if backend is ready
if [[ ! -f "shared-backend/.env" ]]; then
    echo "❌ Backend not configured. Please check shared-backend/.env"
    exit 1
fi

# Start backend in background
echo "Starting backend..."
cd shared-backend
source venv/bin/activate
python -m main &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Check if frontend packages are installed
if [[ -d "chat-system/web-interface/node_modules" ]]; then
    echo "Starting chat system..."
    cd chat-system/web-interface
    PORT=3000 npm start &
    CHAT_PID=$!
    cd ../..
fi

if [[ -d "admin-dashboard/frontend/node_modules" ]]; then
    echo "Starting admin dashboard..."
    cd admin-dashboard/frontend
    PORT=3001 npm start &
    ADMIN_PID=$!
    cd ../..
fi

echo ""
echo "🎉 OpenHealth is starting up!"
echo "📱 Chat System: http://localhost:3000"
echo "🔧 Admin Dashboard: http://localhost:3001" 
echo "🔗 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping..."; kill $BACKEND_PID $CHAT_PID $ADMIN_PID 2>/dev/null; exit' INT
wait
EOF

    chmod +x quick_start.sh
    print_status "Startup scripts created"
}

# Main setup function
main() {
    print_info "Starting OpenHealth setup..."
    
    check_prerequisites
    create_directories
    
    # Check if .env exists
    if [[ ! -f "shared-backend/.env" ]]; then
        print_warning "Environment file not found"
        print_info "Your API keys should already be configured in shared-backend/.env"
        print_info "If not, please check the previous setup steps"
    else
        print_status "Environment file found"
    fi
    
    setup_backend
    setup_database
    setup_frontends
    create_scripts
    
    echo ""
    echo "🎉 OpenHealth Setup Complete!"
    echo "=============================="
    echo ""
    print_status "Next steps:"
    echo "1. Start all services: ./quick_start.sh"
    echo "2. Or start individually:"
    echo "   - Backend: ./start_backend.sh"
    echo "   - Chat: ./start_chat_frontend.sh"
    echo "   - Admin: ./start_admin_frontend.sh"
    echo ""
    echo "🌐 Access URLs:"
    echo "   - Chat System: http://localhost:3000"
    echo "   - Admin Dashboard: http://localhost:3001"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    print_info "For detailed setup info, see: docs/DEVELOPMENT_SETUP.md"
    echo ""
}

# Run main function
main "$@"