"""Chat endpoints for the Todo Chatbot API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...database import get_db
from ...agents.ai_agent import AIAgent


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    message: str
    user_id: int = 1  # Default user_id, should come from authentication in production


@router.post("/")
def chat(message_request: ChatMessageRequest, db: Session = Depends(get_db)):
    """Process a chat message and return an AI response."""
    try:
        # Initialize the AI agent with the database session
        ai_agent = AIAgent(db)

        # Process the message using the AI agent
        response = ai_agent.process_message(
            user_id=message_request.user_id,
            message=message_request.message
        )

        return response

    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error processing chat message: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")

        # Return a helpful response for the user
        return {
            "response": "Hello! I'm your AI assistant for todo management. I'm currently unable to process your request, but you can ask me to add, list, complete, or delete tasks.",
            "action": "fallback_response"
        }


@router.get("/{conversation_id}")
def get_chat_history(conversation_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """Get chat history for a specific conversation."""
    # For now, this is a placeholder - in a real implementation,
    # you would retrieve conversation history from the database
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "messages": [],
        "timestamp": "2024-01-01T00:00:00Z"
    }