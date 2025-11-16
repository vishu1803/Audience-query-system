from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import webhooks, queries, assignment, users  # Add assignment


app = FastAPI(
    title="Audience Query Management System",
    description="Unified inbox for multi-channel customer queries with AI categorization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://audience-query-system.vercel.app"

         
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "Audience Query Management API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "database": "connected",
        "ai": "ready" if settings.OPENAI_API_KEY else "not configured"
    }

# Register routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(assignment.router, prefix="/api/assignment", tags=["Assignment"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])  # Add this

@app.on_event("startup")
async def startup_event():
    print("🚀 API Server Started")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔗 Available endpoints:")
    print("   POST /api/webhooks/email")
    print("   GET  /api/queries")
    print("   POST /api/assignment/auto-assign/{id}")
    print("   POST /api/assignment/escalate")
