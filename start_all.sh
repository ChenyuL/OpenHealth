#!/bin/bash
echo "🚀 Starting OpenHealth Platform..."
echo "Shared Backend API: http://localhost:8000"
echo "Chat System: http://localhost:3000"
echo "Admin Dashboard: http://localhost:3001"
echo ""

# Check if required directories exist
if [ ! -d "shared-backend" ]; then
    echo "❌ Error: shared-backend directory not found"
    exit 1
fi

if [ ! -d "chat-system/web-interface" ]; then
    echo "❌ Error: chat-system/web-interface directory not found"
    exit 1
fi

if [ ! -d "admin-dashboard/frontend" ]; then
    echo "❌ Error: admin-dashboard/frontend directory not found"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Check ports
check_port 8000 || echo "   Backend port 8000 is busy"
check_port 3000 || echo "   Frontend port 3000 is busy"
check_port 3001 || echo "   Admin port 3001 is busy"

# Start shared backend in background
echo "Starting shared backend..."
cd shared-backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing backend dependencies..."
    pip install -r requirements.txt
fi

python -m main &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "⚠️  Backend may not have started properly"
fi

# Start chat system frontend
echo "Starting chat system..."
cd chat-system/web-interface

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing chat system dependencies..."
    npm install
fi

npm start &
CHAT_PID=$!
cd ../..

# Wait a moment
sleep 3

# Start admin dashboard frontend
echo "Starting admin dashboard..."
cd admin-dashboard/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing admin dashboard dependencies..."
    npm install
fi

npm start &
ADMIN_PID=$!
cd ../..

echo ""
echo "✅ All services started!"
echo "🔹 Backend PID: $BACKEND_PID"
echo "🔹 Chat Frontend PID: $CHAT_PID"
echo "🔹 Admin Frontend PID: $ADMIN_PID"
echo ""
echo "📱 Access URLs:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Chat System: http://localhost:3000"
echo "   • Admin Dashboard: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    
    # Kill processes gracefully
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    
    if kill -0 $CHAT_PID 2>/dev/null; then
        echo "Stopping chat frontend (PID: $CHAT_PID)..."
        kill $CHAT_PID
    fi
    
    if kill -0 $ADMIN_PID 2>/dev/null; then
        echo "Stopping admin frontend (PID: $ADMIN_PID)..."
        kill $ADMIN_PID
    fi
    
    # Force kill if processes are still running after 5 seconds
    sleep 5
    
    for pid in $BACKEND_PID $CHAT_PID $ADMIN_PID; do
        if kill -0 $pid 2>/dev/null; then
            echo "Force stopping process $pid..."
            kill -9 $pid 2>/dev/null
        fi
    done
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for user interrupt or process completion
wait