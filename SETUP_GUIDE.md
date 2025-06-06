# 🏥 OpenHealth Setup Guide

Complete setup and troubleshooting guide for the OpenHealth healthcare venture screening platform.

## 📋 Quick Start Checklist

Before running OpenHealth, ensure you have:
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ and npm installed
- [ ] PostgreSQL installed and running
- [ ] API keys for Anthropic and OpenAI
- [ ] Git installed

## 🔍 Prerequisites Check

Run the automated prerequisites checker:
```bash
./check_prerequisites.sh
```

This will verify all requirements and guide you through any missing dependencies.

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended)
```bash
# Clone or ensure you're in the OpenHealth directory
cd OpenHealth

# Run automated setup
python3 setup.py

# Start all services
./start_all.sh
```

### Method 2: Manual Setup
```bash
# 1. Setup backend
cd shared-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup chat system
cd ../chat-system/web-interface
npm install

# 3. Setup admin dashboard
cd ../../admin-dashboard/frontend
npm install

# 4. Return to root and start services
cd ../..
./start_all.sh
```

### Method 3: Streamlit Interface (Quick Demo)
```bash
# Install streamlit dependencies
pip install -r streamlit_requirements.txt

# Set environment variable
export ANTHROPIC_API_KEY="your_api_key_here"

# Run streamlit app
streamlit run streamlit_app.py
```

## ⚙️ Configuration

### 1. API Keys Setup
Edit `shared-backend/.env`:
```bash
# Replace with your actual API keys
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 2. Database Configuration
Default PostgreSQL settings in `.env`:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/openhealth
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=openhealth
DATABASE_USER=postgres
DATABASE_PASSWORD=password
```

### 3. Port Configuration
Default ports:
- Backend API: `8000`
- Chat System: `3000`
- Admin Dashboard: `3001`

Change ports in respective `package.json` files if needed.

## 🗄️ Database Setup

### PostgreSQL Installation

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### Database Initialization
```bash
# Create database and user
psql postgres
CREATE DATABASE openhealth;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE openhealth TO postgres;
\q

# Run database migrations
cd database
python3 init_db.py
```

## 🔧 Component Details

### Shared Backend (`shared-backend/`)
- **Purpose**: Central API serving both chat system and admin dashboard
- **Technology**: FastAPI + PostgreSQL + Redis
- **Port**: 8000
- **Key Features**: 
  - AI integration (Claude + OpenAI)
  - Authentication & authorization
  - Database management
  - WebSocket support

### Chat System (`chat-system/web-interface/`)
- **Purpose**: User-facing healthcare founder chat interface
- **Technology**: React + TypeScript + Tailwind CSS
- **Port**: 3000
- **Key Features**:
  - Healthcare idea discussion
  - Meeting scheduling
  - Real-time chat
  - Mobile responsive

### Admin Dashboard (`admin-dashboard/frontend/`)
- **Purpose**: Management interface for OpenHealth team
- **Technology**: React + TypeScript + Advanced UI components
- **Port**: 3001
- **Key Features**:
  - Conversation monitoring
  - Venture scoring
  - Analytics & reporting
  - Document management

## 🚦 Running Services

### Start All Services
```bash
./start_all.sh
```

### Start Individual Services
```bash
# Backend only
./start_backend.sh

# Chat system only
./start_chat_frontend.sh

# Admin dashboard only
./start_admin_frontend.sh
```

### Service URLs
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Chat System**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3001

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors in Backend
**Error**: `Import "fastapi" could not be resolved`
**Solution**:
```bash
cd shared-backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Database Connection Failed
**Error**: `database "openhealth" does not exist`
**Solution**:
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Create database
psql postgres -c "CREATE DATABASE openhealth;"
```

#### 3. Port Already in Use
**Error**: `Port 8000 is already in use`
**Solution**:
```bash
# Find process using port
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

#### 4. Node Modules Missing
**Error**: `Module not found` in React apps
**Solution**:
```bash
# Chat system
cd chat-system/web-interface
rm -rf node_modules package-lock.json
npm install

# Admin dashboard
cd admin-dashboard/frontend
rm -rf node_modules package-lock.json
npm install
```

#### 5. API Keys Not Working
**Error**: `Authentication failed` or `Invalid API key`
**Solution**:
1. Verify API keys in `shared-backend/.env`
2. Ensure no extra spaces or quotes
3. Test API keys with curl:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.anthropic.com/v1/messages
```

#### 6. Redis Connection Issues
**Error**: `Redis connection failed`
**Solution**:
```bash
# Install Redis (optional for development)
brew install redis  # macOS
sudo apt install redis-server  # Linux

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Development Issues

#### Hot Reload Not Working
```bash
# React apps
cd chat-system/web-interface
npm start

# If still not working, clear cache
npm start -- --reset-cache
```

#### Backend Changes Not Reflected
```bash
cd shared-backend
source venv/bin/activate
python -m main  # Manual restart
```

#### Database Schema Issues
```bash
cd database
python3 reset_db.py  # Reset database
python3 init_db.py   # Reinitialize
```

## 🔐 Security Notes

### Production Deployment
1. **Change default passwords** in `.env`
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** for all endpoints
4. **Configure proper CORS** settings
5. **Set up rate limiting**
6. **Use Redis for session management**

### API Key Management
- Store keys in environment variables only
- Use different keys for development/production
- Rotate keys regularly
- Monitor usage and costs

## 📊 Monitoring & Logs

### View Logs
```bash
# Backend logs
cd shared-backend
source venv/bin/activate
python -m main  # View in terminal

# Frontend logs
# Check browser developer console (F12)
```

### Health Checks
- Backend: http://localhost:8000/health
- Database connection status included in health check

### Performance Monitoring
- Monitor API response times in `/docs`
- Check database query performance
- Monitor frontend bundle size

## 🚀 Production Deployment

### Docker Deployment (Recommended)
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Deployment
1. Set up production database
2. Configure environment variables
3. Build frontend applications
4. Use process manager (PM2, systemd)
5. Set up reverse proxy (nginx)
6. Configure SSL certificates

## 📚 Additional Resources

### Documentation
- **Backend API**: http://localhost:8000/docs (when running)
- **React Components**: Check component documentation in each frontend
- **Database Schema**: `database/schema.sql`

### Development
- **Code Style**: ESLint + Prettier for frontend, Black for backend
- **Testing**: Jest for frontend, pytest for backend
- **Git Hooks**: Pre-commit hooks for code quality

### Support
- Check GitHub issues for known problems
- Review component documentation
- Use browser developer tools for frontend debugging
- Check server logs for backend issues

## 🎯 Next Steps

After successful setup:
1. **Test the chat system** with sample healthcare ideas
2. **Explore the admin dashboard** features
3. **Configure your screening criteria**
4. **Customize the UI** for your branding
5. **Set up production deployment**
6. **Configure monitoring and alerts**

---

**Need Help?** 
- Run `./check_prerequisites.sh` for system verification
- Check logs in terminal when running services
- Review this guide's troubleshooting section
- Ensure all prerequisites are met before proceeding