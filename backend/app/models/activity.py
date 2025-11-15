from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class QueryActivity(Base):
    """
    Audit log for all query actions.
    Tracks who did what and when.
    """
    __tablename__ = "query_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String, nullable=False)  # "created", "assigned", "status_changed", "responded"
    details = Column(JSON, default={})  # Extra data about the action
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship("Query", back_populates="activities")
    user = relationship("User", back_populates="activities")
