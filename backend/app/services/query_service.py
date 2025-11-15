from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.query import Query, QueryStatus, QueryPriority, QueryCategory, QueryChannel
from app.models.activity import QueryActivity
from app.schemas.query import QueryCreateBase, QueryChannelEnum

class QueryService:
    """Service for query operations"""
    
    @staticmethod
    def create_query(db: Session, query_data: QueryCreateBase) -> Query:
        """
        Create a new query in the database.
        Also logs the creation activity.
        """
        # Create query object
        db_query = Query(
            channel=query_data.channel.value,
            sender_email=query_data.sender_email,
            sender_name=query_data.sender_name,
            sender_id=query_data.sender_id,
            subject=query_data.subject,
            content=query_data.content,
            status=QueryStatus.NEW,
            priority=QueryPriority.MEDIUM,  # Default, will be updated by AI
            category=QueryCategory.GENERAL,  # Default, will be updated by AI
            received_at=datetime.utcnow()
        )
        
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        
        # Log activity
        activity = QueryActivity(
            query_id=db_query.id,
            action="created",
            details={
                "channel": query_data.channel.value,
                "sender": query_data.sender_email or query_data.sender_name
            }
        )
        db.add(activity)
        db.commit()
        
        return db_query
    
    @staticmethod
    def get_query_by_id(db: Session, query_id: int) -> Optional[Query]:
        """Get a single query by ID"""
        return db.query(Query).filter(Query.id == query_id).first()
    
    @staticmethod
    def get_queries(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[QueryStatus] = None,
        priority: Optional[QueryPriority] = None,
        channel: Optional[QueryChannel] = None,
        assigned_to: Optional[int] = None
    ) -> tuple[List[Query], int]:
        """
        Get queries with filters and pagination.
        Returns (queries, total_count)
        """
        query = db.query(Query)
        
        # Apply filters
        if status:
            query = query.filter(Query.status == status)
        if priority:
            query = query.filter(Query.priority == priority)
        if channel:
            query = query.filter(Query.channel == channel)
        if assigned_to:
            query = query.filter(Query.assigned_to == assigned_to)
        
        # Get total count before pagination
        total = query.count()
        
        # Order by received_at descending (newest first)
        queries = query.order_by(desc(Query.received_at)).offset(skip).limit(limit).all()
        
        return queries, total
    
    @staticmethod
    def update_query_status(
        db: Session, 
        query_id: int, 
        new_status: QueryStatus,
        user_id: Optional[int] = None
    ) -> Optional[Query]:
        """Update query status and log activity"""
        query = db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            return None
        
        old_status = query.status
        query.status = new_status
        
        # Update timestamps based on status
        if new_status == QueryStatus.IN_PROGRESS and not query.first_response_at:
            query.first_response_at = datetime.utcnow()
            # Calculate response time in hours
            query.response_time = (
                query.first_response_at - query.received_at
            ).total_seconds() / 3600
        
        elif new_status == QueryStatus.RESOLVED and not query.resolved_at:
            query.resolved_at = datetime.utcnow()
            # Calculate resolution time in hours
            query.resolution_time = (
                query.resolved_at - query.received_at
            ).total_seconds() / 3600
        
        db.commit()
        db.refresh(query)
        
        # Log activity
        activity = QueryActivity(
            query_id=query_id,
            user_id=user_id,
            action="status_changed",
            details={
                "old_status": old_status.value,
                "new_status": new_status.value
            }
        )
        db.add(activity)
        db.commit()
        
        return query
    
    @staticmethod
    def assign_query(
        db: Session, 
        query_id: int, 
        assignee_id: int,
        assigner_id: Optional[int] = None
    ) -> Optional[Query]:
        """Assign query to an agent"""
        query = db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            return None
        
        old_assignee = query.assigned_to
        query.assigned_to = assignee_id
        query.assigned_at = datetime.utcnow()
        
        # Auto-update status to ASSIGNED if it was NEW
        if query.status == QueryStatus.NEW:
            query.status = QueryStatus.ASSIGNED
        
        db.commit()
        db.refresh(query)
        
        # Log activity
        activity = QueryActivity(
            query_id=query_id,
            user_id=assigner_id,
            action="assigned",
            details={
                "old_assignee_id": old_assignee,
                "new_assignee_id": assignee_id
            }
        )
        db.add(activity)
        db.commit()
        
        return query
    
    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get dashboard statistics"""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = now - timedelta(days=7)
        
        return {
            "total_queries": db.query(Query).count(),
            "queries_today": db.query(Query).filter(
                Query.received_at >= today_start
            ).count(),
            "queries_this_week": db.query(Query).filter(
                Query.received_at >= week_start
            ).count(),
            "unassigned": db.query(Query).filter(
                Query.assigned_to.is_(None),
                Query.status == QueryStatus.NEW
            ).count(),
            "urgent": db.query(Query).filter(
                Query.priority == QueryPriority.URGENT,
                Query.status != QueryStatus.RESOLVED
            ).count(),
            "avg_response_time": db.query(
                func.avg(Query.response_time)
            ).filter(
                Query.response_time.isnot(None)
            ).scalar() or 0
        }
