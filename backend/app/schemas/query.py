from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums (must match database enums)
class QueryChannelEnum(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class QueryStatusEnum(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class QueryPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class QueryCategoryEnum(str, Enum):
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    BUG_REPORT = "bug_report"
    GENERAL = "general"

# Input schemas (for creating queries)
class QueryCreateBase(BaseModel):
    """Base schema for creating a query"""
    channel: QueryChannelEnum
    sender_email: Optional[EmailStr] = None
    sender_name: Optional[str] = None
    sender_id: Optional[str] = None  # Social media handle
    subject: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)

class EmailWebhookPayload(BaseModel):
    """
    Schema for incoming email webhooks.
    Matches common email service formats (Postmark, SendGrid, etc.)
    """
    from_email: EmailStr = Field(..., alias="from")
    from_name: Optional[str] = Field(None, alias="fromName")
    to: EmailStr
    subject: str
    text_body: str = Field(..., alias="textBody")
    html_body: Optional[str] = Field(None, alias="htmlBody")
    message_id: Optional[str] = Field(None, alias="messageId")
    
    class Config:
        populate_by_name = True  # Allow both 'from' and 'from_email'

class ChatMessagePayload(BaseModel):
    """Schema for live chat messages"""
    sender_name: str
    sender_email: Optional[EmailStr] = None
    message: str
    session_id: str  # To track conversation

class SocialMediaWebhookPayload(BaseModel):
    """Schema for social media webhooks (Twitter, Instagram, etc.)"""
    platform: str  # "twitter", "instagram", "facebook"
    sender_id: str  # Username or ID
    sender_name: str
    message: str
    post_id: Optional[str] = None  # Original post if it's a comment
    direct_message: bool = False

# Output schemas (for returning queries)
class QueryResponse(BaseModel):
    """Schema for query responses"""
    id: int
    channel: str
    sender_email: Optional[str]
    sender_name: Optional[str]
    subject: str
    content: str
    category: Optional[str]
    priority: str
    status: str
    tags: List[str]
    assigned_to: Optional[int]
    received_at: datetime
    response_time: Optional[float]
    resolution_time: Optional[float]
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models

class QueryListResponse(BaseModel):
    """Paginated list of queries"""
    total: int
    page: int
    page_size: int
    queries: List[QueryResponse]

class QueryUpdateStatus(BaseModel):
    """Schema for updating query status"""
    status: QueryStatusEnum

class QueryAssign(BaseModel):
    """Schema for assigning query to agent"""
    assigned_to: int
