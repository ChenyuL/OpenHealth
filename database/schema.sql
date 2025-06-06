-- OpenHealth Database Schema
-- Supports both User Chat System and Admin Dashboard

-- Enable UUID extension for unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (healthcare founders using chat system)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    role VARCHAR(100),
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Admin users table (OpenHealth team members)
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL, -- 'admin', 'analyst', 'partner', etc.
    permissions JSONB DEFAULT '[]', -- Array of permission strings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Conversations between users and AI
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived', 'flagged'
    priority INTEGER DEFAULT 0, -- For admin prioritization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}' -- Store conversation context, tags, etc.
);

-- Individual messages within conversations
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- 'text', 'file', 'meeting_request'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}', -- Store message-specific data
    embedding vector(1536) -- For similarity search (OpenAI embeddings)
);

-- Healthcare venture information extracted from conversations
CREATE TABLE ventures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    stage VARCHAR(100), -- 'idea', 'mvp', 'early_stage', 'growth', etc.
    market_size VARCHAR(100),
    funding_status VARCHAR(100),
    team_size INTEGER,
    location VARCHAR(255),
    score INTEGER, -- Venture scoring (1-100)
    score_breakdown JSONB, -- Detailed scoring components
    status VARCHAR(50) DEFAULT 'screening', -- 'screening', 'interested', 'passed', 'investment'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extracted_data JSONB DEFAULT '{}' -- All extracted information
);

-- Meeting scheduling
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    venture_id UUID REFERENCES ventures(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER DEFAULT 30,
    meeting_type VARCHAR(50) DEFAULT 'discovery', -- 'discovery', 'pitch', 'follow_up'
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no_show'
    meeting_link VARCHAR(500), -- Zoom, Teams, etc.
    attendees JSONB DEFAULT '[]', -- Array of attendee objects
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File attachments and documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    venture_id UUID REFERENCES ventures(id) ON DELETE SET NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size INTEGER,
    storage_path VARCHAR(500), -- S3, local storage path
    processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processed', 'error'
    extracted_text TEXT, -- OCR/parsed content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- RAG knowledge base for AI context
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(255), -- Where this knowledge came from
    category VARCHAR(100), -- 'healthcare_trends', 'investment_criteria', etc.
    embedding vector(1536), -- For similarity search
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES admin_users(id),
    tags JSONB DEFAULT '[]'
);

-- AI extraction schemas (configurable by admin)
CREATE TABLE extraction_schemas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    schema_definition JSONB NOT NULL, -- JSON schema for extraction
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES admin_users(id)
);

-- System settings and configuration
CREATE TABLE system_settings (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES admin_users(id)
);

-- Audit log for admin actions
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID REFERENCES admin_users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100), -- 'user', 'conversation', 'venture', etc.
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Analytics and metrics
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL, -- 'message_sent', 'meeting_scheduled', etc.
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_ventures_user_id ON ventures(user_id);
CREATE INDEX idx_ventures_status ON ventures(status);
CREATE INDEX idx_ventures_score ON ventures(score DESC);
CREATE INDEX idx_meetings_user_id ON meetings(user_id);
CREATE INDEX idx_meetings_scheduled_time ON meetings(scheduled_time);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at DESC);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

-- Full-text search indexes
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('english', content));
CREATE INDEX idx_ventures_search ON ventures USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_knowledge_base_search ON knowledge_base USING gin(to_tsvector('english', title || ' ' || content));

-- Insert default admin user
INSERT INTO admin_users (email, name, role, permissions) VALUES
('admin@openhealth.com', 'OpenHealth Admin', 'admin', '["full_access"]');

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('ai_model', '"claude-3-sonnet"', 'Default AI model for conversations'),
('max_conversation_length', '50', 'Maximum messages per conversation'),
('meeting_duration_options', '[15, 30, 45, 60]', 'Available meeting duration options in minutes'),
('venture_scoring_weights', '{"market_size": 0.3, "team": 0.25, "traction": 0.25, "innovation": 0.2}', 'Weights for venture scoring algorithm'),
('extraction_enabled', 'true', 'Whether to extract venture data from conversations'),
('embedding_model', '"text-embedding-ada-002"', 'Model for generating embeddings');

-- Insert default extraction schema
INSERT INTO extraction_schemas (name, description, schema_definition) VALUES
('Healthcare Venture Basic', 'Basic information extraction for healthcare ventures', '{
  "type": "object",
  "properties": {
    "company_name": {"type": "string"},
    "description": {"type": "string"},
    "stage": {"type": "string", "enum": ["idea", "mvp", "early_stage", "growth"]},
    "market_size": {"type": "string"},
    "team_size": {"type": "integer"},
    "funding_status": {"type": "string"},
    "key_metrics": {"type": "object"},
    "competitive_advantage": {"type": "string"},
    "target_market": {"type": "string"}
  }
}');
