# OpenHealth Development Setup Guide

This guide will help you set up the OpenHealth development environment from scratch. OpenHealth is a dual-system healthcare venture screening platform with both user-facing chat and admin dashboard components.

## 📋 Prerequisites

### Required Software
- **Python 3.9+** - Backend development
- **Node.js 18+** - Frontend development  
- **PostgreSQL 13+** - Database
- **Redis 6+** - Caching and sessions (optional for development)
- **Git** - Version control

### Recommended Tools
- **VS Code** or **Zed** - Code editor
- **Postman** or **Insomnia** - API testing
- **pgAdmin** or **DBeaver** - Database management
- **Docker** (optional) - Containerized development

### System Requirements
- **macOS**: Use Homebrew for package management
- **Linux**: Use your distribution's package manager
- **Windows**: Use WSL2 with Ubuntu

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd OpenHealth
```

### 2. Run Automated Setup
```bash
# Make setup script executable
chmod +x setup.py

# Run setup (handles everything below automatically)
python3 setup.py
```

If the automated setup works, skip to [Running the Application](#running-the-application).

## 🔧 Manual Setup

### 1. Database Setup

#### Install PostgreSQL
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb openhealth
```

#### Apply Database Schema
```bash
# Navigate to database directory
cd database

# Apply schema
psql openhealth -f schema.sql

# Verify tables created
psql openhealth -c "\dt"
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd shared-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/openhealth

# AI Services (Get from providers)
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional for embeddings

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production

# Application
ENVIRONMENT=development
DEBUG=true
```

### 3. Frontend Setup

#### Chat System Frontend
```bash
cd chat-system/web-interface

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

#### Admin Dashboard Frontend
```bash
cd admin-dashboard/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

#### Widget (Optional)
```bash
cd chat-system/embeddable-widget

# Install dependencies
npm install
```

### 4. Redis Setup (Optional)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Test Redis connection
redis-cli ping
```

## 🏃‍♂️ Running the Application

### Option 1: Start All Services
```bash
# From project root
./start_all.sh
```

### Option 2: Start Services Individually

#### Backend
```bash
cd shared-backend
source venv/bin/activate
python -m main

# Should start on http://localhost:8000
```

#### Chat System Frontend
```bash
cd chat-system/web-interface
npm start

# Should start on http://localhost:3000
```

#### Admin Dashboard Frontend
```bash
cd admin-dashboard/frontend
npm start

# Should start on http://localhost:3001
```

### Option 3: Development Mode
```bash
# Backend with auto-reload
cd shared-backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend with hot reload
npm run dev  # In each frontend directory
```

## 🔍 Verify Installation

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Check API Documentation
Open: http://localhost:8000/docs

### 3. Check Database Connection
```bash
psql openhealth -c "SELECT COUNT(*) FROM users;"
```

### 4. Test AI Integration
```bash
# Create test user and send message via API
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I have a healthcare startup idea"}'
```

## 📁 Project Structure

```
OpenHealth/
├── shared-backend/           # Shared backend services
│   ├── api/                 # API endpoints
│   ├── ai-services/         # Claude AI integration
│   ├── auth/                # Authentication
│   ├── database/            # Database models
│   └── main.py              # FastAPI app
├── chat-system/             # User-facing chat
│   ├── web-interface/       # React web app
│   ├── embeddable-widget/   # Embeddable widget
│   └── shared/              # Shared components
├── admin-dashboard/         # Management interface
│   ├── frontend/            # React admin app
│   └── backend/             # Admin-specific APIs
├── database/                # Database schema
├── docs/                    # Documentation
└── setup.py                 # Automated setup
```

## 🧪 Development Workflow

### 1. Code Organization
- **Backend**: Follow FastAPI patterns, use dependency injection
- **Frontend**: Use React hooks, TypeScript for type safety
- **Database**: Use SQLAlchemy ORM, migrations for schema changes
- **AI**: Centralize AI logic in `ai-services/`

### 2. Environment Management
```bash
# Switch between environments
export ENVIRONMENT=development  # or staging, production

# Use different databases
export DATABASE_URL=postgresql://user:pass@localhost:5432/openhealth_test
```

### 3. Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 4. Testing
```bash
# Backend tests
cd shared-backend
pytest tests/

# Frontend tests
cd chat-system/web-interface
npm test

cd admin-dashboard/frontend
npm test
```

### 5. Code Quality
```bash
# Python formatting
black shared-backend/
isort shared-backend/

# Python linting
flake8 shared-backend/

# JavaScript/TypeScript
npm run lint
npm run format
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Check database exists
psql -l | grep openhealth

# Reset database
dropdb openhealth && createdb openhealth
psql openhealth -f database/schema.sql
```

#### 2. Python Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 3. Node Module Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Port Already in Use
```bash
# Find process using port
lsof -i :8000  # or :3000, :3001

# Kill process
kill -9 <PID>

# Use different port
PORT=8001 python -m main
```

#### 5. AI API Errors
```bash
# Verify API keys are set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Use debugger
python -m pdb main.py
```

#### Frontend Debug
```bash
# Enable development mode
npm run dev

# Use browser developer tools
# React DevTools extension recommended
```

### Performance Issues

#### Database Performance
```bash
# Check database connections
SELECT * FROM pg_stat_activity WHERE datname = 'openhealth';

# Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM conversations WHERE user_id = 'uuid';
```

#### Memory Usage
```bash
# Monitor Python memory
pip install memory-profiler
python -m memory_profiler main.py
```

## 🔧 Configuration Reference

### Backend Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=openhealth
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEFAULT_AI_MODEL=claude-3-sonnet-20240229
EMBEDDING_MODEL=text-embedding-ada-002
MAX_TOKENS=4000
TEMPERATURE=0.7

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
API_VERSION=v1

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
ALLOW_CREDENTIALS=true

# File Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE_MB=10

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@openhealth.com
```

### Frontend Environment Variables
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Authentication
REACT_APP_JWT_STORAGE_KEY=openhealth_token

# Features
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_FILE_UPLOAD=true

# Environment
NODE_ENV=development
```

## 📚 Additional Resources

### Documentation
- [API Documentation](http://localhost:8000/docs) (when backend is running)
- [Database Schema](../database/README.md)
- [Frontend Components](../chat-system/README.md)
- [Admin Dashboard](../admin-dashboard/README.md)

### External APIs
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI API](https://platform.openai.com/docs)

### Tools
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🆘 Getting Help

1. **Check Logs**: Always check backend and frontend console logs first
2. **API Documentation**: Use `/docs` endpoint for API testing
3. **Database**: Use pgAdmin or psql to inspect database state
4. **AI Services**: Test API keys with curl commands
5. **Environment**: Verify all environment variables are set correctly

## 🚀 Next Steps

Once setup is complete:
1. Create your first admin user via API
2. Test the chat system with a healthcare startup scenario
3. Explore the admin dashboard features
4. Review the AI conversation analysis
5. Set up development database with sample data

Happy coding! 🏥✨