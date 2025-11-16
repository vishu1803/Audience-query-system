"""
API endpoints for user/agent management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User, UserRole, UserTeam
from app.services.assignment_service import AssignmentService

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    team: str
    is_active: bool
    
    class Config:
        from_attributes = True

class UserWithLoad(BaseModel):
    id: int
    email: str
    name: str
    role: str
    team: str
    is_active: bool
    active_tickets: int
    
@router.get("/", response_model=List[UserWithLoad])
def get_all_users(db: Session = Depends(get_db)):
    """
    Get all users/agents with their current workload.
    """
    users = db.query(User).filter(User.is_active == True).all()
    
    users_with_load = []
    for user in users:
        load = AssignmentService.get_agent_load(db, user.id)
        users_with_load.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "team": user.team.value,
            "is_active": user.is_active,
            "active_tickets": load['total']
        })
    
    return users_with_load

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
