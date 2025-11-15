from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.query import (
    EmailWebhookPayload,
    ChatMessagePayload,
    SocialMediaWebhookPayload,
    QueryCreateBase,
    QueryChannelEnum,
    QueryResponse
)
from app.services.query_service import QueryService
from app.services.ai_categorization import categorize_query  # Import AI service

router = APIRouter()

# Updated the background task function
async def process_query_background(query_id: int):
    """
    Background task to:
    1. Categorize query with AI
    2. Auto-assign to best agent
    """
    from app.database import SessionLocal
    from app.services.assignment_service import AssignmentService
    
    db = SessionLocal()
    try:
        # Step 1: Categorize
        await categorize_query(query_id, db)
        
        # Step 2: Auto-assign
        AssignmentService.assign_query(db, query_id, auto=True)
        
    except Exception as e:
        print(f"❌ Background processing failed for query {query_id}: {e}")
    finally:
        db.close()


@router.post("/email", response_model=QueryResponse, status_code=201)
async def receive_email_webhook(
    payload: EmailWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for receiving emails.
    Now with AI categorization in the background!
    """
    print(f"📧 Received email from: {payload.from_email}")
    
    # Convert email webhook to query format
    query_data = QueryCreateBase(
        channel=QueryChannelEnum.EMAIL,
        sender_email=payload.from_email,
        sender_name=payload.from_name,
        subject=payload.subject,
        content=payload.text_body
    )
    
    # Create query in database
    query = QueryService.create_query(db, query_data)
    
    # Schedule AI categorization in background
    background_tasks.add_task(process_query_background, query.id)
    
    print(f"✅ Created query #{query.id}, AI categorization scheduled")
    
    return query

@router.post("/chat", response_model=QueryResponse, status_code=201)
async def receive_chat_message(
    payload: ChatMessagePayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Endpoint for live chat messages with AI categorization"""
    print(f"💬 Received chat message from: {payload.sender_name}")
    
    query_data = QueryCreateBase(
        channel=QueryChannelEnum.CHAT,
        sender_email=payload.sender_email,
        sender_name=payload.sender_name,
        subject=f"Chat: {payload.message[:50]}...",
        content=payload.message
    )
    
    query = QueryService.create_query(db, query_data)
    
    # Schedule AI categorization
    background_tasks.add_task(process_query_background, query.id)
    
    print(f"✅ Created query #{query.id}, AI categorization scheduled")
    
    return query

@router.post("/social", response_model=QueryResponse, status_code=201)
async def receive_social_media_webhook(
    payload: SocialMediaWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook for social media with AI categorization"""
    print(f"📱 Received {payload.platform} message from: {payload.sender_name}")
    
    channel_map = {
        "twitter": QueryChannelEnum.TWITTER,
        "instagram": QueryChannelEnum.INSTAGRAM,
        "facebook": QueryChannelEnum.FACEBOOK
    }
    
    channel = channel_map.get(payload.platform.lower(), QueryChannelEnum.CHAT)
    
    query_data = QueryCreateBase(
        channel=channel,
        sender_name=payload.sender_name,
        sender_id=payload.sender_id,
        subject=f"{payload.platform.title()}: {payload.message[:50]}...",
        content=payload.message
    )
    
    query = QueryService.create_query(db, query_data)
    
    # Schedule AI categorization
    background_tasks.add_task(process_query_background, query.id)
    
    print(f"✅ Created query #{query.id}, AI categorization scheduled")
    
    return query

@router.post("/generic", response_model=QueryResponse, status_code=201)
async def receive_generic_query(
    query_data: QueryCreateBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generic endpoint with AI categorization"""
    print(f"📥 Received generic query via {query_data.channel}")
    
    query = QueryService.create_query(db, query_data)
    
    # Schedule AI categorization
    background_tasks.add_task(process_query_background, query.id)
    
    print(f"✅ Created query #{query.id}, AI categorization scheduled")
    
    return query

@router.get("/test")
async def webhook_test():
    """Test endpoint"""
    return {
        "status": "success",
        "message": "Webhook endpoint is active with AI categorization",
        "endpoints": {
            "email": "/api/webhooks/email",
            "chat": "/api/webhooks/chat",
            "social": "/api/webhooks/social",
            "generic": "/api/webhooks/generic"
        }
    }
