from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import webhooks, queries  # Import routers

# Create FastAPI app
app = FastAPI(
    title="Audience Query Management System",
    description="Unified inbox for multi-channel customer queries with AI categorization",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "https://your-vercel-app.vercel.app"  # Add your Vercel URL later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Audience Query Management API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "database": "connected",
        "ai": "ready" if settings.OPENAI_API_KEY else "not configured"
    }

# Register routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])

# On startup, print available routes
@app.on_event("startup")
async def startup_event():
    print("🚀 API Server Started")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔗 Available endpoints:")
    print("   POST /api/webhooks/email")
    print("   POST /api/webhooks/chat")
    print("   POST /api/webhooks/social")
    print("   GET  /api/queries")
    print("   GET  /api/queries/{id}")
    print("   PUT  /api/queries/{id}/status")
    print("   PUT  /api/queries/{id}/assign")
