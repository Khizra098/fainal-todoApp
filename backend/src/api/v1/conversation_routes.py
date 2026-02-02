"""
Conversation routes for the AI Assistant Chat feature.
This module defines the API endpoints for conversation management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from ...database.database import get_db
from ...auth.auth_handler import get_current_user
from ...services.conversation_service import ConversationService
from ...utils.error_handlers import validate_input
from ...config.settings import settings

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/")
async def create_conversation(
    request: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.

    Args:
        request (dict): Contains optional initial_message
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: The created conversation details
    """
    try:
        # Get optional initial message
        initial_message = request.get("initial_message")

        if initial_message:
            validate_input(initial_message, max_length=settings.max_message_length)

        # Create conversation service instance
        conversation_service = ConversationService(db)

        # Create new conversation
        conversation = conversation_service.create_conversation(
            user_id=current_user,
            initial_message=initial_message
        )

        return {
            "conversation_id": str(conversation.conversation_id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "status": conversation.status,
            "user_id": conversation.user_id,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the conversation: {str(e)}"
        )


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific conversation.

    Args:
        conversation_id (str): The ID of the conversation to retrieve
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: The conversation details
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

        # Create conversation service instance
        conversation_service = ConversationService(db)

        # Get the conversation
        conversation = conversation_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify that the user owns this conversation
        if conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

        return {
            "conversation_id": str(conversation.conversation_id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "status": conversation.status,
            "user_id": conversation.user_id,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the conversation: {str(e)}"
        )


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get messages for a specific conversation.

    Args:
        conversation_id (str): The ID of the conversation
        limit (int): Maximum number of messages to return (default: 50)
        offset (int): Number of messages to skip (default: 0)
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: List of messages and total count
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

        # Validate limit and offset
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )

        # Create conversation service instance
        conversation_service = ConversationService(db)

        # Get the conversation first to verify it exists and belongs to the user
        conversation = conversation_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify that the user owns this conversation
        if conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

        # Get messages for the conversation
        messages = conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )

        # Get total count of messages
        total_count = conversation_service.get_total_messages_count(conversation_id)

        return {
            "messages": [msg.to_dict() for msg in messages],
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving conversation messages: {str(e)}"
        )


@router.get("/")
async def get_user_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user.

    Args:
        limit (int): Maximum number of conversations to return (default: 20)
        offset (int): Number of conversations to skip (default: 0)
        current_user (str): The authenticated user
        db (Session): Database session

    Returns:
        dict: List of user's conversations
    """
    try:
        # Validate limit and offset
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )

        # Create conversation service instance
        conversation_service = ConversationService(db)

        # Get conversations for the user
        conversations = conversation_service.get_user_conversations(
            user_id=current_user,
            limit=limit,
            offset=offset
        )

        return {
            "conversations": [conv.to_dict() for conv in conversations],
            "limit": limit,
            "offset": offset,
            "success": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user conversations: {str(e)}"
        )