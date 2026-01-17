"""Main entry point for the Todo Chatbot API application."""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, engine
from .models.task import Base
from .models.user import Base as UserBase  # Import user base for table creation
from .api.v1.todo_routes import router as todo_router
from .api.v1.mcp_routes import router as mcp_router
from .api.v1.auth_routes import router as auth_router
from .api.v1.chat_routes import router as chat_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)
UserBase.metadata.create_all(bind=engine)  # Create user tables too

# Create FastAPI app
app = FastAPI(
    title="Todo Chatbot API",
    description="API for the AI-Powered Todo Chatbot with MCP integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(todo_router, prefix="/api/v1")
app.include_router(mcp_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")  # Add chat routes
app.include_router(auth_router)  # Add auth routes without prefix since frontend expects /auth/*


@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"message": "Todo Chatbot API is running!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Todo Chatbot API"}


# Additional endpoints can be added here
@app.get("/api/v1/user/{user_id}/conversations")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a user."""
    from .services.conversation_service import ConversationService

    conversation_service = ConversationService(db)
    conversations = conversation_service.get_user_conversations(user_id)

    return [
        {
            "id": conv.id,
            "title": conv.title,
            "status": conv.status.value,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
        }
        for conv in conversations
    ]



@app.get("/test-endpoint")
def test_endpoint():
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )