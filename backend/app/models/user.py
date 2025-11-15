from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    AGENT = "agent"
    VIEWER = "viewer"

class UserTeam(str, enum.Enum):
    """Teams for query routing"""
    SUPPORT = "support"
    ENGINEERING = "engineering"
    SALES = "sales"
    FINANCE = "finance"

class User(Base):
    """
    User model representing agents and admins.
    Used for authentication and query assignment.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.AGENT)
    team = Column(SQLEnum(UserTeam), default=UserTeam.SUPPORT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assigned_queries = relationship("Query", back_populates="assignee", foreign_keys="Query.assigned_to")
    responses = relationship("QueryResponse", back_populates="responder")
    activities = relationship("QueryActivity", back_populates="user")
