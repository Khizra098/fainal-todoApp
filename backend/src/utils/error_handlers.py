"""
Error handling utilities for the AI Assistant Chat feature.
This module contains custom exceptions and error handlers.
"""

from fastapi import HTTPException, status
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatException(HTTPException):
    """
    Base exception class for chat-related errors
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        logger.error(f"ChatException: {detail}")


class MessageProcessingError(ChatException):
    """
    Exception raised when there's an error processing a message
    """
    def __init__(self, detail: str = "Error processing message"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class InvalidMessageTypeError(ChatException):
    """
    Exception raised when an invalid message type is provided
    """
    def __init__(self, detail: str = "Invalid message type"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConversationNotFoundError(ChatException):
    """
    Exception raised when a conversation is not found
    """
    def __init__(self, detail: str = "Conversation not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ResponseGenerationError(ChatException):
    """
    Exception raised when there's an error generating a response
    """
    def __init__(self, detail: str = "Error generating response"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Generic error handler that logs and formats errors
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg)

    return {
        "error": True,
        "message": str(error),
        "context": context
    }


def validate_input(input_str: str, max_length: int = 10000) -> bool:
    """
    Validate input string for length and content
    """
    if not input_str or len(input_str.strip()) == 0:
        raise ChatException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input cannot be empty")

    if len(input_str) > max_length:
        raise ChatException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail=f"Input exceeds maximum length of {max_length} characters")

    return True