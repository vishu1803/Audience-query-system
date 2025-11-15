"""
Intelligent query assignment and routing service.
Automatically assigns queries to the best available agent based on:
- Team/department matching
- Current workload (load balancing)
- Agent availability
- Query priority
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app.models.query import Query, QueryCategory, QueryPriority, QueryStatus
from app.models.user import User, UserTeam, UserRole
from app.models.activity import QueryActivity

class AssignmentService:
    """Service for intelligent query assignment and routing"""
    
    # Category to team mapping
    CATEGORY_TEAM_MAP = {
        QueryCategory.QUESTION: UserTeam.SUPPORT,
        QueryCategory.COMPLAINT: UserTeam.SUPPORT,
        QueryCategory.FEEDBACK: UserTeam.SUPPORT,
        QueryCategory.REQUEST: UserTeam.SALES,
        QueryCategory.BUG_REPORT: UserTeam.ENGINEERING,
        QueryCategory.GENERAL: UserTeam.SUPPORT,
    }
    
    # Maximum tickets per agent (for load balancing)
    MAX_TICKETS_PER_AGENT = {
        QueryPriority.URGENT: 3,    # Max 3 urgent tickets
        QueryPriority.HIGH: 5,       # Max 5 high priority
        QueryPriority.MEDIUM: 10,    # Max 10 medium
        QueryPriority.LOW: 15        # Max 15 low priority
    }
    
    @staticmethod
    def get_target_team(query: Query) -> UserTeam:
        """
        Determine which team should handle this query based on category.
        """
        # Check tags for specific routing
        if query.tags:
            if 'billing' in query.tags or 'payment' in query.tags:
                return UserTeam.FINANCE
            if 'api' in query.tags or 'technical' in query.tags:
                return UserTeam.ENGINEERING
            if 'sales' in query.tags or 'pricing' in query.tags:
                return UserTeam.SALES
        
        # Default to category mapping
        return AssignmentService.CATEGORY_TEAM_MAP.get(
            query.category,
            UserTeam.SUPPORT
        )
    
    @staticmethod
    def get_agent_load(db: Session, agent_id: int) -> dict:
        """
        Calculate current workload for an agent.
        Returns dict with counts by priority.
        """
        # Count active tickets (not resolved/closed)
        active_statuses = [
            QueryStatus.NEW,
            QueryStatus.ASSIGNED,
            QueryStatus.IN_PROGRESS
        ]
        
        load = {
            'total': 0,
            'urgent': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        # Get all active queries for this agent
        queries = db.query(Query).filter(
            Query.assigned_to == agent_id,
            Query.status.in_(active_statuses)
        ).all()
        
        for query in queries:
            load['total'] += 1
            load[query.priority.value] += 1
        
        return load
    
    @staticmethod
    def get_available_agents(
        db: Session,
        team: UserTeam,
        exclude_overloaded: bool = True
    ) -> List[tuple[User, dict]]:
        """
        Get list of available agents in a team with their current load.
        Returns list of (agent, load_dict) tuples sorted by availability.
        """
        # Get all active agents in the team
        agents = db.query(User).filter(
            User.team == team,
            User.role == UserRole.AGENT,
            User.is_active == True
        ).all()
        
        # Calculate load for each agent
        agents_with_load = []
        for agent in agents:
            load = AssignmentService.get_agent_load(db, agent.id)
            
            # Skip overloaded agents if requested
            if exclude_overloaded:
                max_total = sum(AssignmentService.MAX_TICKETS_PER_AGENT.values())
                if load['total'] >= max_total:
                    continue
            
            agents_with_load.append((agent, load))
        
        # Sort by total load (least busy first)
        agents_with_load.sort(key=lambda x: x[1]['total'])
        
        return agents_with_load
    
    @staticmethod
    def find_best_agent(
        db: Session,
        query: Query
    ) -> Optional[User]:
        """
        Find the best agent to handle this query using load-balanced routing.
        
        Algorithm:
        1. Determine target team based on category/tags
        2. Get available agents in that team
        3. Filter out agents at capacity for this priority
        4. Select agent with lowest total load (round-robin style)
        """
        # Get target team
        team = AssignmentService.get_target_team(query)
        
        print(f"🎯 Finding agent for query #{query.id} in team: {team.value}")
        
        # Get available agents
        available_agents = AssignmentService.get_available_agents(db, team)
        
        if not available_agents:
            print(f"⚠️  No available agents in {team.value} team")
            return None
        
        # Filter agents based on priority capacity
        priority = query.priority
        max_for_priority = AssignmentService.MAX_TICKETS_PER_AGENT[priority]
        
        suitable_agents = []
        for agent, load in available_agents:
            # Check if agent can handle another ticket of this priority
            if load[priority.value] < max_for_priority:
                suitable_agents.append((agent, load))
        
        if not suitable_agents:
            # All agents at capacity for this priority
            # Fall back to least loaded agent overall
            print(f"⚠️  All agents at capacity for {priority.value}, using least loaded")
            suitable_agents = available_agents
        
        # Select agent with lowest total load (load balancing)
        best_agent, best_load = suitable_agents[0]
        
        print(f"✅ Selected agent: {best_agent.name} (current load: {best_load['total']})")
        
        return best_agent
    
    @staticmethod
    def assign_query(
        db: Session,
        query_id: int,
        agent_id: Optional[int] = None,
        assigner_id: Optional[int] = None,
        auto: bool = True
    ) -> Optional[Query]:
        """
        Assign a query to an agent.
        
        Args:
            query_id: ID of query to assign
            agent_id: Specific agent to assign to (None = auto-select)
            assigner_id: ID of user making the assignment
            auto: Whether this is automatic assignment
        
        Returns:
            Updated query or None if not found
        """
        query = db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            return None
        
        # If no agent specified, find best one automatically
        if agent_id is None:
            agent = AssignmentService.find_best_agent(db, query)
            if not agent:
                print(f"❌ No agent available for query #{query_id}")
                return query  # Return unassigned
            agent_id = agent.id
        
        # Store old assignee for logging
        old_assignee = query.assigned_to
        
        # Update query
        query.assigned_to = agent_id
        query.assigned_at = datetime.utcnow()
        
        # Update status if it was NEW
        if query.status == QueryStatus.NEW:
            query.status = QueryStatus.ASSIGNED
        
        db.commit()
        db.refresh(query)
        
        # Log activity
        activity = QueryActivity(
            query_id=query_id,
            user_id=assigner_id,
            action="assigned" if auto else "manually_assigned",
            details={
                "old_assignee_id": old_assignee,
                "new_assignee_id": agent_id,
                "method": "auto" if auto else "manual"
            }
        )
        db.add(activity)
        db.commit()
        
        # Get agent name for logging
        agent = db.query(User).filter(User.id == agent_id).first()
        print(f"✅ Query #{query_id} assigned to {agent.name if agent else f'Agent #{agent_id}'}")
        
        return query
    
    @staticmethod
    def reassign_query(
        db: Session,
        query_id: int,
        new_agent_id: int,
        assigner_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Optional[Query]:
        """
        Reassign a query to a different agent.
        """
        return AssignmentService.assign_query(
            db=db,
            query_id=query_id,
            agent_id=new_agent_id,
            assigner_id=assigner_id,
            auto=False
        )
    
    @staticmethod
    def auto_assign_batch(
        db: Session,
        limit: int = 50
    ) -> List[Query]:
        """
        Auto-assign all unassigned queries in batch.
        Useful for processing backlog or running as scheduled job.
        """
        # Get unassigned queries
        unassigned = db.query(Query).filter(
            Query.assigned_to.is_(None),
            Query.status == QueryStatus.NEW
        ).order_by(
            # Process urgent queries first
            Query.priority.desc(),
            Query.received_at.asc()
        ).limit(limit).all()
        
        assigned_count = 0
        assigned_queries = []
        
        for query in unassigned:
            result = AssignmentService.assign_query(db, query.id)
            if result and result.assigned_to:
                assigned_count += 1
                assigned_queries.append(result)
        
        print(f"✅ Batch assigned {assigned_count}/{len(unassigned)} queries")
        
        return assigned_queries
    
    @staticmethod
    def get_assignment_stats(db: Session) -> dict:
        """
        Get statistics about query assignments.
        """
        # Count unassigned queries
        unassigned = db.query(Query).filter(
            Query.assigned_to.is_(None),
            Query.status == QueryStatus.NEW
        ).count()
        
        # Count by team
        team_counts = {}
        for team in UserTeam:
            team_queries = db.query(Query).join(
                User, Query.assigned_to == User.id
            ).filter(
                User.team == team,
                Query.status.in_([QueryStatus.ASSIGNED, QueryStatus.IN_PROGRESS])
            ).count()
            team_counts[team.value] = team_queries
        
        # Agent workload distribution
        agent_loads = db.query(
            User.id,
            User.name,
            User.team,
            func.count(Query.id).label('active_tickets')
        ).join(
            Query, User.id == Query.assigned_to
        ).filter(
            Query.status.in_([QueryStatus.ASSIGNED, QueryStatus.IN_PROGRESS])
        ).group_by(
            User.id, User.name, User.team
        ).all()
        
        return {
            "unassigned": unassigned,
            "by_team": team_counts,
            "agent_workloads": [
                {
                    "agent_id": agent_id,
                    "agent_name": name,
                    "team": team.value if hasattr(team, 'value') else team,
                    "active_tickets": count
                }
                for agent_id, name, team, count in agent_loads
            ]
        }
