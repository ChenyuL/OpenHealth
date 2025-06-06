"""
SQLAlchemy models for OpenHealth database
"""

from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, ForeignKey, 
    TIMESTAMP, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from .connection import Base


class User(Base):
    """Healthcare founders using the chat system"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    role = Column(String(100))
    phone = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB, default={})
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    ventures = relationship("Venture", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    

class AdminUser(Base):
    """OpenHealth team members with admin access"""
    __tablename__ = "admin_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # 'admin', 'analyst', 'partner'
    permissions = Column(JSONB, default=[])
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    knowledge_base_entries = relationship("KnowledgeBase", back_populates="created_by_user")
    extraction_schemas = relationship("ExtractionSchema", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="admin_user")


class Conversation(Base):
    """Conversations between users and AI"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    status = Column(String(50), default="active")  # 'active', 'archived', 'flagged'
    priority = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    ventures = relationship("Venture", back_populates="conversation")
    meetings = relationship("Meeting", back_populates="conversation")
    documents = relationship("Document", back_populates="conversation")
    analytics_events = relationship("AnalyticsEvent", back_populates="conversation")


class Message(Base):
    """Individual messages within conversations"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # 'text', 'file', 'meeting_request'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB, default={})
    # embedding = Column(Vector(1536))  # For similarity search - requires pgvector
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_created_at", "created_at"),
    )


class Venture(Base):
    """Healthcare venture information extracted from conversations"""
    __tablename__ = "ventures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    stage = Column(String(100))  # 'idea', 'mvp', 'early_stage', 'growth'
    market_size = Column(String(100))
    funding_status = Column(String(100))
    team_size = Column(Integer)
    location = Column(String(255))
    score = Column(Integer)  # Venture scoring (1-100)
    score_breakdown = Column(JSONB)
    status = Column(String(50), default="screening")  # 'screening', 'interested', 'passed', 'investment'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    extracted_data = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="ventures")
    conversation = relationship("Conversation", back_populates="ventures")
    meetings = relationship("Meeting", back_populates="venture")
    documents = relationship("Document", back_populates="venture")


class Meeting(Base):
    """Meeting scheduling"""
    __tablename__ = "meetings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    venture_id = Column(UUID(as_uuid=True), ForeignKey("ventures.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    scheduled_time = Column(TIMESTAMP(timezone=True))
    duration_minutes = Column(Integer, default=30)
    meeting_type = Column(String(50), default="discovery")  # 'discovery', 'pitch', 'follow_up'
    status = Column(String(50), default="scheduled")  # 'scheduled', 'completed', 'cancelled', 'no_show'
    meeting_link = Column(String(500))
    attendees = Column(JSONB, default=[])
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meetings")
    conversation = relationship("Conversation", back_populates="meetings")
    venture = relationship("Venture", back_populates="meetings")


class Document(Base):
    """File attachments and documents"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    venture_id = Column(UUID(as_uuid=True), ForeignKey("ventures.id", ondelete="SET NULL"))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    storage_path = Column(String(500))
    processing_status = Column(String(50), default="pending")  # 'pending', 'processed', 'error'
    extracted_text = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="documents")
    conversation = relationship("Conversation", back_populates="documents")
    venture = relationship("Venture", back_populates="documents")


class KnowledgeBase(Base):
    """RAG knowledge base for AI context"""
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255))
    category = Column(String(100))  # 'healthcare_trends', 'investment_criteria'
    # embedding = Column(Vector(1536))  # For similarity search
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    tags = Column(JSONB, default=[])
    
    # Relationships
    created_by_user = relationship("AdminUser", back_populates="knowledge_base_entries")


class ExtractionSchema(Base):
    """AI extraction schemas (configurable by admin)"""
    __tablename__ = "extraction_schemas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    schema_definition = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Relationships
    created_by_user = relationship("AdminUser", back_populates="extraction_schemas")


class SystemSettings(Base):
    """System settings and configuration"""
    __tablename__ = "system_settings"
    
    key = Column(String(255), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))


class AuditLog(Base):
    """Audit log for admin actions"""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))  # 'user', 'conversation', 'venture'
    resource_id = Column(UUID(as_uuid=True))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="audit_logs")


class AnalyticsEvent(Base):
    """Analytics and metrics"""
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False)  # 'message_sent', 'meeting_scheduled'
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    properties = Column(JSONB, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation", back_populates="analytics_events")
