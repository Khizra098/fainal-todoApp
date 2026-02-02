"""
MCP tool for chat functionality in the AI Assistant Chat feature.
This module implements the Model Context Protocol tools for chat interactions.
"""

import asyncio
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import logging

from ..services.chat_service import ChatService
from ..services.conversation_service import ConversationService
from ..database.database import SessionLocal, engine
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.response import Response
from ..utils.error_handlers import MessageProcessingError, ConversationNotFoundError, ResponseGenerationError

logger = logging.getLogger(__name__)


class ChatMCP:
    """
    Model Context Protocol tool for chat functionality.
    This class provides MCP-compatible methods for chat interactions.
    """

    def __init__(self):
        """
        Initialize the ChatMCP tool.
        """
        self.db = SessionLocal()

    def __del__(self):
        """
        Clean up database session on deletion.
        """
        self.db.close()

    async def send_message_to_assistant(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send a message to the AI assistant via MCP and return the response.

        Args:
            conversation_id (str): The ID of the conversation
            user_message (str): The message from the user
            user_id (str): The ID of the user

        Returns:
            Dict[str, Any]: The AI assistant's response
        """
        try:
            logger.info(f"MCP: Sending message to assistant for conversation {conversation_id}")

            # Create chat service instance
            chat_service = ChatService(self.db)

            # Process the message and get response
            response_content = await chat_service.handle_message(
                conversation_id=conversation_id,
                user_message=user_message,
                user_id=user_id
            )

            logger.info(f"MCP: Successfully processed message for conversation {conversation_id}")

            return {
                "success": True,
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_response": response_content,
                "timestamp": datetime.utcnow().isoformat()
            }

        except MessageProcessingError as e:
            logger.error(f"MCP: Message processing error: {str(e)}")
            return {
                "success": False,
                "error": "MessageProcessingError",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        except ConversationNotFoundError as e:
            logger.error(f"MCP: Conversation not found: {str(e)}")
            return {
                "success": False,
                "error": "ConversationNotFoundError",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        except ResponseGenerationError as e:
            logger.error(f"MCP: Response generation error: {str(e)}")
            return {
                "success": False,
                "error": "ResponseGenerationError",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"MCP: Unexpected error in send_message_to_assistant: {str(e)}")
            return {
                "success": False,
                "error": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def create_new_conversation(
        self,
        user_id: str,
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation via MCP.

        Args:
            user_id (str): The ID of the user
            initial_message (Optional[str]): An optional initial message

        Returns:
            Dict[str, Any]: Information about the created conversation
        """
        try:
            logger.info(f"MCP: Creating new conversation for user {user_id}")

            # Create conversation service instance
            conversation_service = ConversationService(self.db)

            # Create new conversation
            conversation = conversation_service.create_conversation(
                user_id=user_id,
                initial_message=initial_message
            )

            logger.info(f"MCP: Successfully created conversation {conversation.conversation_id}")

            return {
                "success": True,
                "conversation_id": str(conversation.conversation_id),
                "user_id": user_id,
                "created_at": conversation.created_at.isoformat(),
                "status": conversation.status,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"MCP: Error creating conversation: {str(e)}")
            return {
                "success": False,
                "error": "ConversationCreationError",
                "message": f"Failed to create conversation: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get conversation history via MCP.

        Args:
            conversation_id (str): The ID of the conversation
            limit (int): Maximum number of messages to return
            offset (int): Number of messages to skip

        Returns:
            Dict[str, Any]: The conversation history
        """
        try:
            logger.info(f"MCP: Retrieving history for conversation {conversation_id}")

            # Create conversation service instance
            conversation_service = ConversationService(self.db)

            # Get messages for the conversation
            messages = conversation_service.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit,
                offset=offset
            )

            # Get total count of messages
            total_count = conversation_service.get_total_messages_count(conversation_id)

            logger.info(f"MCP: Retrieved {len(messages)} messages for conversation {conversation_id}")

            return {
                "success": True,
                "conversation_id": conversation_id,
                "messages": [msg.to_dict() for msg in messages],
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"MCP: Error retrieving conversation history: {str(e)}")
            return {
                "success": False,
                "error": "HistoryRetrievalError",
                "message": f"Failed to retrieve conversation history: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def classify_message(
        self,
        message: str
    ) -> Dict[str, Any]:
        """
        Classify a message via MCP.

        Args:
            message (str): The message to classify

        Returns:
            Dict[str, Any]: Classification results
        """
        try:
            logger.info(f"MCP: Classifying message: '{message[:50]}...'")

            # Create chat service instance
            chat_service = ChatService(self.db)

            # Get message analysis
            analysis = chat_service.get_message_analysis(message)

            logger.info(f"MCP: Classified message as {analysis['classification']}")

            return {
                "success": True,
                "original_message": message,
                "classification": analysis["classification"],
                "confidence_scores": analysis["confidence_scores"],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"MCP: Error classifying message: {str(e)}")
            return {
                "success": False,
                "error": "ClassificationError",
                "message": f"Failed to classify message: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def analyze_sentiment(
        self,
        message: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of a message via MCP (placeholder implementation).

        Args:
            message (str): The message to analyze

        Returns:
            Dict[str, Any]: Sentiment analysis results
        """
        try:
            logger.info(f"MCP: Analyzing sentiment for message: '{message[:50]}...'")

            # Placeholder sentiment analysis
            # In a real implementation, this would use a proper NLP model
            positive_keywords = ["good", "great", "excellent", "happy", "love", "like", "wonderful", "fantastic"]
            negative_keywords = ["bad", "terrible", "awful", "hate", "dislike", "horrible", "sad", "angry"]

            message_lower = message.lower()
            pos_count = sum(1 for word in positive_keywords if word in message_lower)
            neg_count = sum(1 for word in negative_keywords if word in message_lower)

            if pos_count > neg_count:
                sentiment = "positive"
                score = min(1.0, pos_count / max(len(message.split()), 1))
            elif neg_count > pos_count:
                sentiment = "negative"
                score = min(1.0, neg_count / max(len(message.split()), 1))
            else:
                sentiment = "neutral"
                score = 0.0

            logger.info(f"MCP: Sentiment analysis complete: {sentiment} with score {score}")

            return {
                "success": True,
                "original_message": message,
                "sentiment": sentiment,
                "score": round(score, 2),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"MCP: Error analyzing sentiment: {str(e)}")
            return {
                "success": False,
                "error": "SentimentAnalysisError",
                "message": f"Failed to analyze sentiment: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }