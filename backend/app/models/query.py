from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class QueryChannel(str, enum.Enum):
    """Source channels for queries"""
    EMAIL = "email"
    CHAT = "chat"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class QueryStatus(str, enum.Enum):
    """Query lifecycle status"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class QueryPriority(str, enum.Enum):
    """Query urgency level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class QueryCategory(str, enum.Enum):
    """Auto-detected query type"""
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    BUG_REPORT = "bug_report"
    GENERAL = "general"

class Query(Base):
    """
    Main query/ticket model.
    Stores all incoming messages from various channels.
    """
    __tablename__ = "queries"
    
    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(SQLEnum(QueryChannel), nullable=False, index=True)
    sender_email = Column(String, index=True)
    sender_name = Column(String)
    sender_id = Column(String)  # External ID (Twitter handle, etc.)
    
    # Content
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Classification (AI-generated)
    category = Column(SQLEnum(QueryCategory), default=QueryCategory.GENERAL, index=True)
    priority = Column(SQLEnum(QueryPriority), default=QueryPriority.MEDIUM, index=True)
    tags = Column(ARRAY(String), default=[])  # Auto-extracted tags
    
    # Status tracking
    status = Column(SQLEnum(QueryStatus), default=QueryStatus.NEW, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metrics (calculated)
    response_time = Column(Float, nullable=True)  # Hours until first response
    resolution_time = Column(Float, nullable=True)  # Hours until resolved
    
    # Relationships
    assignee = relationship("User", back_populates="assigned_queries", foreign_keys=[assigned_to])
    responses = relationship("QueryResponse", back_populates="query", cascade="all, delete-orphan")
    activities = relationship("QueryActivity", back_populates="query", cascade="all, delete-orphan")
