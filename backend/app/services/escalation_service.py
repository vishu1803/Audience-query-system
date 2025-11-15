"""
Escalation service for handling urgent and stale queries.
Automatically escalates queries that:
- Are urgent but unassigned
- Haven't been responded to within SLA
- Are stuck in same status too long
"""

from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.query import Query, QueryStatus, QueryPriority
from app.models.user import User, UserRole
from app.models.activity import QueryActivity
from typing import Optional



class EscalationService:
    """Service for query escalation"""
    
    # SLA times in hours
    SLA_RESPONSE_TIME = {
        QueryPriority.URGENT: 0.5,   # 30 minutes
        QueryPriority.HIGH: 2,        # 2 hours
        QueryPriority.MEDIUM: 8,      # 8 hours
        QueryPriority.LOW: 24         # 24 hours
    }
    
    # Time before escalating stuck queries (in hours)
    STUCK_THRESHOLD = {
        QueryPriority.URGENT: 2,      # Escalate after 2 hours
        QueryPriority.HIGH: 8,        # Escalate after 8 hours
        QueryPriority.MEDIUM: 24,     # Escalate after 24 hours
        QueryPriority.LOW: 72         # Escalate after 72 hours
    }
    
    @staticmethod
    def check_sla_breach(query: Query) -> bool:
        """
        Check if query has breached SLA response time.
        """
        if query.first_response_at:
            # Already responded
            return False
        
        sla_time = EscalationService.SLA_RESPONSE_TIME[query.priority]
        time_elapsed = (datetime.now(timezone.utc) - query.received_at).total_seconds() / 3600
        
        return time_elapsed > sla_time
    
    @staticmethod
    def check_stuck_query(query: Query) -> bool:
        """
        Check if query is stuck in the same status for too long.
        """
        threshold = EscalationService.STUCK_THRESHOLD[query.priority]
        
        # Use assigned_at if available, otherwise received_at
        reference_time = query.assigned_at or query.received_at
        time_elapsed = (datetime.now(timezone.utc) - reference_time).total_seconds() / 3600
        
        # Only check if query is not yet resolved
        if query.status in [QueryStatus.RESOLVED, QueryStatus.CLOSED]:
            return False
        
        return time_elapsed > threshold
    
    @staticmethod
    def escalate_query(
        db: Session,
        query_id: int,
        reason: str,
        escalate_to: Optional[int] = None
    ) -> Query:

        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise ValueError(f"Query {query_id} not found")

        print(f"🚨 Escalating query #{query_id}: {reason}")

        old_priority = query.priority
        old_assignee = query.assigned_to

        # -------- PRIORITY UPDATE --------
        if query.priority == QueryPriority.LOW:
            query.priority = QueryPriority.MEDIUM
        elif query.priority == QueryPriority.MEDIUM:
            query.priority = QueryPriority.HIGH
        elif query.priority == QueryPriority.HIGH:
            query.priority = QueryPriority.URGENT

        # -------- ASSIGNEE FIX --------
        # If escalate_to is given → verify it exists
        if escalate_to:
            user = db.query(User).filter(User.id == escalate_to).first()
            if not user:
                raise ValueError(f"Cannot escalate: user {escalate_to} does not exist")
            query.assigned_to = escalate_to

        # If no escalate_to → assign to actual admin in DB
        elif not query.assigned_to:
            admin = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.is_active == True
            ).first()

            if not admin:
                raise ValueError("No active admin found for escalation")

            query.assigned_to = admin.id  # <-- FIX: uses real admin ID (5)

        # Save query update
        db.commit()
        db.refresh(query)

        # -------- LOG ESCALATION --------
        activity = QueryActivity(
            query_id=query_id,
            action="escalated",
            details={
                "reason": reason,
                "old_priority": old_priority.value,
                "new_priority": query.priority.value,
                "old_assignee_id": old_assignee,
                "new_assignee_id": query.assigned_to
            }
        )
        db.add(activity)
        db.commit()

        print(f"✅ Query #{query_id} escalated: {old_priority.value} → {query.priority.value}")

        return query


    
    @staticmethod
    def check_and_escalate_all(db: Session) -> dict:
        """
        Check all queries and escalate those that need it.
        Run this as a scheduled job (e.g., every 15 minutes).
        
        Returns dict with escalation summary.
        """
        escalated = {
            'sla_breach': [],
            'stuck': [],
            'urgent_unassigned': []
        }
        
        # 1. Check for urgent queries without assignment
        urgent_unassigned = db.query(Query).filter(
            Query.priority == QueryPriority.URGENT,
            Query.assigned_to.is_(None),
            Query.status == QueryStatus.NEW
        ).all()
        
        for query in urgent_unassigned:
            EscalationService.escalate_query(
                db=db,
                query_id=query.id,
                reason="Urgent query unassigned for too long"
            )
            escalated['urgent_unassigned'].append(query.id)
        
        # 2. Check for SLA breaches
        active_queries = db.query(Query).filter(
            Query.status.in_([QueryStatus.NEW, QueryStatus.ASSIGNED, QueryStatus.IN_PROGRESS]),
            Query.first_response_at.is_(None)
        ).all()
        
        for query in active_queries:
            if EscalationService.check_sla_breach(query):
                EscalationService.escalate_query(
                    db=db,
                    query_id=query.id,
                    reason=f"SLA breach: No response within {EscalationService.SLA_RESPONSE_TIME[query.priority]}h"
                )
                escalated['sla_breach'].append(query.id)
        
        # 3. Check for stuck queries
        for query in active_queries:
            if EscalationService.check_stuck_query(query):
                EscalationService.escalate_query(
                    db=db,
                    query_id=query.id,
                    reason=f"Query stuck for {EscalationService.STUCK_THRESHOLD[query.priority]}h"
                )
                escalated['stuck'].append(query.id)
        
        total_escalated = sum(len(v) for v in escalated.values())
        
        print(f"\n📊 Escalation Check Complete:")
        print(f"  🚨 Urgent unassigned: {len(escalated['urgent_unassigned'])}")
        print(f"  ⏰ SLA breaches: {len(escalated['sla_breach'])}")
        print(f"  🐢 Stuck queries: {len(escalated['stuck'])}")
        print(f"  Total escalated: {total_escalated}\n")
        
        return escalated
    
    @staticmethod
    def get_at_risk_queries(db: Session) -> dict:
        """
        Get queries that are at risk of needing escalation.
        Used for dashboard warnings.
        """
        now = datetime.now(timezone.utc)
        at_risk = {
            'approaching_sla': [],
            'getting_stale': []
        }
        
        active_queries = db.query(Query).filter(
            Query.status.in_([QueryStatus.NEW, QueryStatus.ASSIGNED, QueryStatus.IN_PROGRESS]),
            Query.first_response_at.is_(None)
        ).all()
        
        for query in active_queries:
            # Check if approaching SLA (80% of time used)
            sla_time = EscalationService.SLA_RESPONSE_TIME[query.priority]
            time_elapsed = (now - query.received_at).total_seconds() / 3600
            
            if time_elapsed > (sla_time * 0.8) and time_elapsed < sla_time:
                at_risk['approaching_sla'].append({
                    'query_id': query.id,
                    'subject': query.subject,
                    'priority': query.priority.value,
                    'time_remaining_hours': round(sla_time - time_elapsed, 2)
                })
            
            # Check if getting stale (50% of stuck threshold)
            stuck_threshold = EscalationService.STUCK_THRESHOLD[query.priority]
            reference_time = query.assigned_at or query.received_at
            time_in_status = (now - reference_time).total_seconds() / 3600
            
            if time_in_status > (stuck_threshold * 0.5):
                at_risk['getting_stale'].append({
                    'query_id': query.id,
                    'subject': query.subject,
                    'status': query.status.value,
                    'hours_in_status': round(time_in_status, 2)
                })
        
        return at_risk
