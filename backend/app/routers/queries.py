from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.query import (
    QueryResponse,
    QueryListResponse,
    QueryUpdateStatus,
    QueryAssign,
    QueryStatusEnum,
    QueryPriorityEnum,
    QueryChannelEnum
)
from app.services.query_service import QueryService
from app.models.query import QueryStatus, QueryPriority, QueryChannel

router = APIRouter()

@router.get("/", response_model=QueryListResponse)
def list_queries(
    page: int = QueryParam(1, ge=1, description="Page number"),
    page_size: int = QueryParam(50, ge=1, le=100, description="Items per page"),
    status: Optional[QueryStatusEnum] = None,
    priority: Optional[QueryPriorityEnum] = None,
    channel: Optional[QueryChannelEnum] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of queries with optional filters.
    
    Example: GET /api/queries?page=1&status=new&priority=urgent
    """
    skip = (page - 1) * page_size
    
    # Convert enum strings to model enums
    status_filter = QueryStatus(status.value) if status else None
    priority_filter = QueryPriority(priority.value) if priority else None
    channel_filter = QueryChannel(channel.value) if channel else None
    
    queries, total = QueryService.get_queries(
        db=db,
        skip=skip,
        limit=page_size,
        status=status_filter,
        priority=priority_filter,
        channel=channel_filter,
        assigned_to=assigned_to
    )
    
    return QueryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        queries=queries
    )

@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single query by ID.
    
    Example: GET /api/queries/123
    """
    query = QueryService.get_query_by_id(db, query_id)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query

@router.put("/{query_id}/status", response_model=QueryResponse)
def update_query_status(
    query_id: int,
    status_update: QueryUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Update query status.
    
    Example: PUT /api/queries/123/status
    Body: {"status": "in_progress"}
    """
    query = QueryService.update_query_status(
        db=db,
        query_id=query_id,
        new_status=QueryStatus(status_update.status.value)
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query

@router.put("/{query_id}/assign", response_model=QueryResponse)
def assign_query(
    query_id: int,
    assignment: QueryAssign,
    db: Session = Depends(get_db)
):
    """
    Assign query to an agent.
    
    Example: PUT /api/queries/123/assign
    Body: {"assigned_to": 5}
    """
    query = QueryService.assign_query(
        db=db,
        query_id=query_id,
        assignee_id=assignment.assigned_to
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query

@router.get("/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics.
    
    Returns counts and metrics for the dashboard.
    """
    stats = QueryService.get_stats(db)
    return stats

@router.get("/analytics/categories")
def get_category_analytics(db: Session = Depends(get_db)):
    """
    Get analytics on query categories and priorities.
    Used for dashboard charts.
    """
    from sqlalchemy import func
    from app.models.query import QueryCategory, QueryPriority
    
    # Count by category
    category_counts = (
        db.query(
            Query.category,
            func.count(Query.id).label('count')
        )
        .group_by(Query.category)
        .all()
    )
    
    # Count by priority
    priority_counts = (
        db.query(
            Query.priority,
            func.count(Query.id).label('count')
        )
        .group_by(Query.priority)
        .all()
    )
    
    # Count by status
    status_counts = (
        db.query(
            Query.status,
            func.count(Query.id).label('count')
        )
        .group_by(Query.status)
        .all()
    )
    
    # Top tags
    from sqlalchemy import func as sql_func
    # This is a bit complex - we need to unnest the array
    all_tags = []
    queries_with_tags = db.query(Query.tags).filter(Query.tags != None).all()
    for (tags,) in queries_with_tags:
        all_tags.extend(tags)
    
    from collections import Counter
    tag_counter = Counter(all_tags)
    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(10)
    ]
    
    # Average response times by priority
    avg_response_by_priority = (
        db.query(
            Query.priority,
            func.avg(Query.response_time).label('avg_response_time')
        )
        .filter(Query.response_time.isnot(None))
        .group_by(Query.priority)
        .all()
    )
    
    return {
        "categories": [
            {"category": cat.value if hasattr(cat, 'value') else cat, "count": count}
            for cat, count in category_counts
        ],
        "priorities": [
            {"priority": pri.value if hasattr(pri, 'value') else pri, "count": count}
            for pri, count in priority_counts
        ],
        "statuses": [
            {"status": status.value if hasattr(status, 'value') else status, "count": count}
            for status, count in status_counts
        ],
        "top_tags": top_tags,
        "avg_response_by_priority": [
            {
                "priority": pri.value if hasattr(pri, 'value') else pri,
                "avg_hours": round(avg or 0, 2)
            }
            for pri, avg in avg_response_by_priority
        ]
    }
