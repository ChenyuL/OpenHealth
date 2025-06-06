# OpenHealth - Dual System Architecture

## Overview
OpenHealth consists of two separate but integrated systems:

### 1. User-Facing Chat System (`/chat-system`)
- **Purpose**: Healthcare founders chat with OpenHealth AI Assistant
- **Features**: 
  - Natural language healthcare idea discussion
  - AI-powered meeting scheduling
  - Both web interface and embeddable widget
- **Users**: Healthcare entrepreneurs, startup founders, healthcare CEOs
- **Access**: Public-facing, simple and intuitive

### 2. Management Dashboard (`/admin-dashboard`)
- **Purpose**: OpenHealth team manages all backend operations
- **Features**:
  - Live conversation monitoring
  - Venture scoring & pipeline tracking
  - Document processing & RAG knowledge management
  - User analytics & conversation logs
  - Backend settings & extraction schemas
- **Users**: OpenHealth VCs, investors, internal team
- **Access**: Admin-only, comprehensive management interface

## Architecture

```
OpenHealth/
├── chat-system/           # User-facing chat application
│   ├── web-interface/     # Standalone web app
│   ├── embeddable-widget/ # Widget for third-party sites
│   └── shared/           # Shared components
├── admin-dashboard/       # Management system
│   ├── frontend/         # React admin interface
│   └── backend/          # Admin API endpoints
├── shared-backend/        # Shared backend services
│   ├── api/              # Common API endpoints
│   ├── database/         # Database models & migrations
│   ├── ai-services/      # Claude AI integration
│   └── auth/             # Authentication & authorization
└── database/             # Database schema & setup
```

## Data Flow
- **User Conversations**: Stored in shared database
- **Management Access**: On-demand viewing of conversation logs
- **AI Processing**: Shared AI services for both systems
- **Authentication**: Separate auth flows for users vs admins

## Quick Start

### For Development
```bash
# Setup everything
python3 setup.py

# Start all services
./start_all.sh

# Or start individually
./start_chat_system.sh      # User chat system
./start_admin_dashboard.sh  # Management dashboard
./start_shared_backend.sh   # Shared backend services
```

### Access Points
- **User Chat Web Interface**: http://localhost:3000
- **Embeddable Widget Demo**: http://localhost:3000/widget-demo
- **Admin Dashboard**: http://localhost:3001  
- **Shared Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Configuration
- **Backend Settings**: `shared-backend/.env`
- **Chat System Config**: `chat-system/.env`
- **Admin Dashboard Config**: `admin-dashboard/.env`

## Tech Stack
- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, PostgreSQL
- **AI**: Anthropic Claude, OpenAI (embeddings)
- **Real-time**: WebSocket for chat
- **Authentication**: JWT tokens
- **Deployment**: Docker, Docker Compose

## Key Features

### User Chat System
- Conversational AI for healthcare ideas
- Smart meeting scheduling
- Mobile-responsive design
- Easy website embedding
- Multi-language support (future)

### Admin Dashboard
- Customizable priority views
- Advanced filtering & search
- Conversation analytics
- RAG knowledge base management
- Export capabilities
- Role-based access control

## Next Steps
1. Configure API keys in environment files
2. Set up PostgreSQL database
3. Run setup script
4. Start services and test both systems
5. Customize admin dashboard priorities
6. Deploy to production environment
