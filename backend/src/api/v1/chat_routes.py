"""
Chat routes for the AI Assistant Chat feature.
This module defines the API endpoints for chat functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from ...database.database import get_db
from ...auth.auth_handler import get_current_user
from ...services.chat_service import ChatService
from ...services.conversation_service import ConversationService
from ...utils.error_handlers import validate_input
from ...config.settings import settings

router = APIRouter(prefix="", tags=["chat"])


@router.post("/chat")
async def send_message(
    request: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI assistant and receive a response.

    Args:
        request (dict): Contains conversation_id, content (or message), and optional message_type
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: The AI assistant's response
    """
    try:
        # Support both 'content' and 'message' as the message field name
        content = request.get("content") or request.get("message")
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="content or message field is required"
            )

        # Get or create a conversation_id
        conversation_id = request.get("conversation_id")
        if not conversation_id:
            # Create a new conversation using the ConversationService
            conversation_service = ConversationService(db)
            # Create conversation with a generic title, convert current_user to string
            user_id = str(current_user)
            new_conversation = conversation_service.create_conversation(
                user_id=user_id,
                title="New Chat"
            )
            conversation_id = str(new_conversation.id)  # Use .id for integer ID
        else:
            # Validate conversation ID is an integer if provided
            try:
                conversation_id = int(conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format, must be an integer"
                )
            conversation_id = str(conversation_id)  # Convert back to string for consistency

        # Validate message content
        validate_input(content, max_length=settings.max_message_length)

        # Get optional message type hint
        message_type_hint = request.get("message_type")
        if message_type_hint and message_type_hint not in ["task_related", "greeting", "non_task"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message_type must be one of: task_related, greeting, non_task"
            )

        # Create chat service instance
        chat_service = ChatService(db)

        # Process the message and get response
        response_content = await chat_service.handle_message(
            conversation_id=conversation_id,
            user_message=content,
            user_id=current_user
        )

        # For now, we'll return a simple response structure
        # In a more complete implementation, we'd return the full message and response objects
        return {
            "conversation_id": conversation_id,
            "response": response_content,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your message: {str(e)}"
        )


@router.get("/chat/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for a specific conversation.

    Args:
        conversation_id (str): The ID of the conversation
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: Chat history for the conversation
    """
    try:
        # Validate conversation ID format
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation_id format"
            )

        # Create chat service instance
        chat_service = ChatService(db)

        # Get chat history
        history = await chat_service.get_conversation_history(conversation_id, current_user)

        return {
            "conversation_id": conversation_id,
            "history": history,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving chat history: {str(e)}"
        )


@router.post("/chat/analysis")
async def analyze_message(
    message: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a message to get its classification and confidence scores.

    Args:
        message (str): The message to analyze
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: Analysis results including classification and confidence scores
    """
    try:
        # Validate message content
        validate_input(message, max_length=settings.max_message_length)

        # Create chat service instance
        chat_service = ChatService(db)

        # Get message analysis
        analysis = chat_service.get_message_analysis(message)

        return {
            "analysis": analysis,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the message: {str(e)}"
        )


# Additional endpoints can be added here as needed
# For example, endpoints for message history, conversation management, etc.