#!/usr/bin/env python3
"""
OpenHealth Agent Setup Script
Automates the complete setup process for both backend and frontend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    required_tools = [
        ("python3", "Python 3.8+"),
        ("node", "Node.js 18+"),
        ("npm", "npm package manager"),
        ("psql", "PostgreSQL client"),
        ("redis-cli", "Redis client (optional)")
    ]
    
    missing = []
    for tool, description in required_tools:
        result = run_command(f"which {tool}", check=False)
        if result is None or result.returncode != 0:
            if tool != "redis-cli":  # Redis is optional for development
                missing.append(f"{tool} ({description})")
    
    if missing:
        print("❌ Missing required tools:")
        for tool in missing:
            print(f"  - {tool}")
        print("\nPlease install missing tools and run setup again.")
        return False
    
    print("✅ All prerequisites satisfied!")
    return True

def setup_database():
    """Set up PostgreSQL database"""
    print("\n🗄️ Setting up database...")
    
    # Run database initialization script
    db_init_result = run_command(
        "python3 database/init_db.py", 
        check=False
    )
    
    if db_init_result and db_init_result.returncode == 0:
        print("✅ Database initialization completed successfully")
    else:
        print("⚠️  Database initialization encountered issues")
        print("   You may need to:")
        print("   1. Start PostgreSQL: brew services start postgresql (macOS)")
        print("   2. Install psycopg2: pip install psycopg2-binary")
        print("   3. Check database credentials in shared-backend/.env")
        print("   4. Run manually: python3 database/init_db.py")

def setup_backend():
    """Set up Python backend"""
    print("\n🐍 Setting up shared backend...")
    
    backend_dir = Path("shared-backend")
    
    # Create virtual environment
    if not (backend_dir / "venv").exists():
        print("Creating virtual environment...")
        run_command("python3 -m venv venv", cwd=backend_dir)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    print("Installing Python dependencies...")
    pip_install = run_command(
        "venv/bin/pip install -r requirements.txt",
        cwd=backend_dir,
        check=False
    )
    
    if pip_install and pip_install.returncode == 0:
        print("✅ Python dependencies installed")
    else:
        print("⚠️  Some dependencies may have failed to install")
        print("   Try manually: cd shared-backend && pip install fastapi uvicorn anthropic openai psycopg2-binary")
    
    # Check if .env file exists (we already created it)
    env_file = backend_dir / ".env"
    if env_file.exists():
        print("✅ Environment file already configured with API keys")
    else:
        print("⚠️  .env file not found - please check API key setup")

def setup_frontend():
    """Set up React frontends"""
    print("\n⚛️  Setting up frontends...")
    
    # Setup chat system frontend
    chat_frontend_dir = Path("chat-system/web-interface")
    if chat_frontend_dir.exists():
        print("Installing chat system dependencies...")
        npm_install = run_command("npm install", cwd=chat_frontend_dir, check=False)
        
        if npm_install and npm_install.returncode == 0:
            print("✅ Chat system dependencies installed")
        else:
            print("⚠️  Chat system npm packages may have failed to install")
    
    # Setup admin dashboard frontend
    admin_frontend_dir = Path("admin-dashboard/frontend")
    if admin_frontend_dir.exists():
        print("Installing admin dashboard dependencies...")
        npm_install = run_command("npm install", cwd=admin_frontend_dir, check=False)
        
        if npm_install and npm_install.returncode == 0:
            print("✅ Admin dashboard dependencies installed")
        else:
            print("⚠️  Admin dashboard npm packages may have failed to install")
    
    print("Note: You may need to run 'npm install' manually in each frontend directory")

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📝 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🏥 Starting OpenHealth Backend..."
cd shared-backend
source venv/bin/activate
python -m main
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    os.chmod("start_backend.sh", 0o755)
    
    # Chat frontend startup script
    chat_frontend_script = """#!/bin/bash
echo "💬 Starting OpenHealth Chat System..."
cd chat-system/web-interface
npm start
"""
    
    with open("start_chat_frontend.sh", "w") as f:
        f.write(chat_frontend_script)
    os.chmod("start_chat_frontend.sh", 0o755)
    
    # Admin frontend startup script
    admin_frontend_script = """#!/bin/bash
echo "🔧 Starting OpenHealth Admin Dashboard..."
cd admin-dashboard/frontend
npm start
"""
    
    with open("start_admin_frontend.sh", "w") as f:
        f.write(admin_frontend_script)
    os.chmod("start_admin_frontend.sh", 0o755)
    
    # Combined startup script
    combined_script = """#!/bin/bash
echo "🚀 Starting OpenHealth Platform..."
echo "Backend API: http://localhost:8000"
echo "Chat System: http://localhost:3000"
echo "Admin Dashboard: http://localhost:3001"
echo ""

# Start backend in background
echo "Starting shared backend..."
cd shared-backend && source venv/bin/activate && python -m main &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start chat frontend
echo "Starting chat system..."
cd chat-system/web-interface && npm start &
CHAT_PID=$!

# Wait a moment
sleep 2

# Start admin frontend
echo "Starting admin dashboard..."
cd admin-dashboard/frontend && npm start &
ADMIN_PID=$!

echo "✅ All services started!"
echo "Backend PID: $BACKEND_PID"
echo "Chat Frontend PID: $CHAT_PID"
echo "Admin Frontend PID: $ADMIN_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "Stopping all services..."; kill $BACKEND_PID $CHAT_PID $ADMIN_PID; exit' INT
wait
"""
    
    with open("start_all.sh", "w") as f:
        f.write(combined_script)
    os.chmod("start_all.sh", 0o755)
    
    print("✅ Startup scripts created:")
    print("  - start_backend.sh (shared backend)")
    print("  - start_chat_frontend.sh (user chat system)")
    print("  - start_admin_frontend.sh (admin dashboard)")
    print("  - start_all.sh (all services)")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 OpenHealth Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. ✅ API keys already configured in shared-backend/.env")
    print("   - ANTHROPIC_API_KEY: Set")
    print("   - OPENAI_API_KEY: Set")
    print("")
    print("2. Start the services:")
    print("   ./start_all.sh          # Start all services")
    print("   # OR start individually:")
    print("   ./start_backend.sh      # Backend API on http://localhost:8000")
    print("   ./start_chat_frontend.sh     # Chat system on http://localhost:3000")
    print("   ./start_admin_frontend.sh    # Admin dashboard on http://localhost:3001")
    print("")
    print("3. Access the applications:")
    print("   - 💬 User Chat System: http://localhost:3000")
    print("   - 🔧 Admin Dashboard: http://localhost:3001")
    print("   - 🔗 Backend API: http://localhost:8000")
    print("   - 📚 API Documentation: http://localhost:8000/docs")
    print("")
    print("4. Test the system:")
    print("   - Register as a healthcare founder on the chat system")
    print("   - Share your healthcare startup idea with the AI")
    print("   - Login to admin dashboard (admin@openhealth.com / admin123)")
    print("   - View conversations and venture analysis")
    print("")
    print("🔧 Troubleshooting:")
    print("- Ensure PostgreSQL is running: brew services start postgresql (macOS)")
    print("- Check database connection: psql openhealth -c 'SELECT COUNT(*) FROM users;'")
    print("- Check logs in terminal for any errors")
    print("- Verify Node.js and npm are installed: node --version && npm --version")
    print("")
    print("📖 Documentation:")
    print("- Development guide: docs/DEVELOPMENT_SETUP.md")
    print("- React components guide: docs/REACT_COMPONENTS_GUIDE.md")

def main():
    """Main setup function"""
    print("🏥 OpenHealth Agent Setup")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Setup components
    setup_database()
    setup_backend()
    setup_frontend()
    create_startup_scripts()
    
    # Print completion message
    print_next_steps()

if __name__ == "__main__":
    main()
