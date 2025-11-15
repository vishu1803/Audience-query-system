"""
API endpoints for query assignment and escalation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.services.assignment_service import AssignmentService
from app.services.escalation_service import EscalationService
from app.schemas.query import QueryResponse

router = APIRouter()

class ManualAssignment(BaseModel):
    """Schema for manual assignment"""
    query_id: int
    agent_id: int
    reason: Optional[str] = None

class EscalationRequest(BaseModel):
    """Schema for manual escalation"""
    query_id: int
    reason: str
    escalate_to: Optional[int] = None

@router.post("/auto-assign/{query_id}", response_model=QueryResponse)
def auto_assign_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """
    Automatically assign a query to the best available agent.
    
    Example: POST /api/assignment/auto-assign/123
    """
    query = AssignmentService.assign_query(db, query_id, auto=True)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    if not query.assigned_to:
        raise HTTPException(
            status_code=503,
            detail="No available agents to assign query"
        )
    
    return query

@router.post("/manual-assign", response_model=QueryResponse)
def manual_assign_query(
    assignment: ManualAssignment,
    db: Session = Depends(get_db)
):
    """
    Manually assign a query to a specific agent.
    
    Example: POST /api/assignment/manual-assign
    Body: {"query_id": 123, "agent_id": 5, "reason": "Expert in this area"}
    """
    query = AssignmentService.assign_query(
        db=db,
        query_id=assignment.query_id,
        agent_id=assignment.agent_id,
        auto=False
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query

@router.post("/batch-assign")
def batch_assign_queries(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Auto-assign all unassigned queries in batch.
    
    Example: POST /api/assignment/batch-assign?limit=20
    """
    assigned_queries = AssignmentService.auto_assign_batch(db, limit)
    
    return {
        "assigned_count": len(assigned_queries),
        "query_ids": [q.id for q in assigned_queries]
    }

@router.get("/stats")
def get_assignment_stats(db: Session = Depends(get_db)):
    """
    Get statistics about query assignments and agent workload.
    
    Example: GET /api/assignment/stats
    """
    return AssignmentService.get_assignment_stats(db)

@router.get("/agent-load/{agent_id}")
def get_agent_load(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current workload for a specific agent.
    
    Example: GET /api/assignment/agent-load/2
    """
    from app.models.user import User
    
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    load = AssignmentService.get_agent_load(db, agent_id)
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "team": agent.team.value,
        "load": load
    }

@router.post("/escalate", response_model=QueryResponse)
def escalate_query(
    escalation: EscalationRequest,
    db: Session = Depends(get_db)
):
    """
    Manually escalate a query.
    
    Example: POST /api/assignment/escalate
    Body: {"query_id": 123, "reason": "Customer threatening to cancel"}
    """
    try:
        query = EscalationService.escalate_query(
            db=db,
            query_id=escalation.query_id,
            reason=escalation.reason,
            escalate_to=escalation.escalate_to
        )
        return query
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/check-escalations")
def check_escalations(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Check all queries and escalate those that need it.
    This should be called by a scheduled job (cron).
    
    Example: POST /api/assignment/check-escalations
    """
    result = EscalationService.check_and_escalate_all(db)
    
    return {
        "message": "Escalation check complete",
        "escalated": result
    }

@router.get("/at-risk")
def get_at_risk_queries(db: Session = Depends(get_db)):
    """
    Get queries that are at risk of needing escalation.
    Used for dashboard warnings.
    
    Example: GET /api/assignment/at-risk
    """
    return EscalationService.get_at_risk_queries(db)
