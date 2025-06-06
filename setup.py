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
    
    # Check if database exists
    db_check = run_command(
        "psql -lqt | cut -d \\| -f 1 | grep -qw openhealth", 
        check=False
    )
    
    if db_check and db_check.returncode == 0:
        print("✅ Database 'openhealth' already exists")
    else:
        print("Creating database 'openhealth'...")
        create_db = run_command("createdb openhealth", check=False)
        if create_db and create_db.returncode == 0:
            print("✅ Database created successfully")
        else:
            print("⚠️  Could not create database. You may need to:")
            print("   1. Start PostgreSQL service")
            print("   2. Create database manually: createdb openhealth")
    
    # Apply schema
    print("Applying database schema...")
    schema_result = run_command(
        "psql openhealth -f database/schema.sql",
        check=False
    )
    
    if schema_result and schema_result.returncode == 0:
        print("✅ Database schema applied successfully")
    else:
        print("⚠️  Could not apply schema. Manual setup may be required.")

def setup_backend():
    """Set up Python backend"""
    print("\n🐍 Setting up backend...")
    
    backend_dir = Path("backend")
    
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
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        run_command("cp .env.example .env", cwd=backend_dir)
        print("✅ Created .env file (please configure with your API keys)")
    else:
        print("✅ .env file already exists")

def setup_frontend():
    """Set up React frontend"""
    print("\n⚛️  Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    npm_install = run_command("npm install", cwd=frontend_dir, check=False)
    
    if npm_install and npm_install.returncode == 0:
        print("✅ Node.js dependencies installed")
    else:
        print("⚠️  Some npm packages may have failed to install")

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📝 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
cd backend
source venv/bin/activate
python -m app.main
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    os.chmod("start_backend.sh", 0o755)
    
    # Frontend startup script
    frontend_script = """#!/bin/bash
cd frontend
npm start
"""
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script)
    os.chmod("start_frontend.sh", 0o755)
    
    # Combined startup script
    combined_script = """#!/bin/bash
echo "🚀 Starting OpenHealth Agent..."
echo "Backend will start on http://localhost:8000"
echo "Frontend will start on http://localhost:3000"
echo ""

# Start backend in background
echo "Starting backend..."
cd backend && source venv/bin/activate && python -m app.main &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "✅ Both services started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
"""
    
    with open("start_all.sh", "w") as f:
        f.write(combined_script)
    os.chmod("start_all.sh", 0o755)
    
    print("✅ Startup scripts created:")
    print("  - start_backend.sh (backend only)")
    print("  - start_frontend.sh (frontend only)")
    print("  - start_all.sh (both services)")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Configure your API keys in backend/.env:")
    print("   - ANTHROPIC_API_KEY for Claude AI")
    print("   - OPENAI_API_KEY for embeddings (optional)")
    print("   - AWS credentials for file storage (optional)")
    print("")
    print("2. Start the services:")
    print("   ./start_all.sh    # Start both backend and frontend")
    print("   # OR start separately:")
    print("   ./start_backend.sh  # Backend on http://localhost:8000")
    print("   ./start_frontend.sh # Frontend on http://localhost:3000")
    print("")
    print("3. Access the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("")
    print("4. Create your first tenant and start screening healthcare ventures!")
    print("")
    print("🔧 Troubleshooting:")
    print("- Check backend/.env for correct configuration")
    print("- Ensure PostgreSQL is running: brew services start postgresql")
    print("- Check logs in terminal for any errors")

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
