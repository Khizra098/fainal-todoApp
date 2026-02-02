"""
Chat service for the AI Assistant Chat feature.
This module orchestrates the chat functionality including message processing and response generation.
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from sqlalchemy.orm import Session
import logging

from .conversation_service import ConversationService
from .message_classifier import MessageClassifier
from .response_generator import ResponseGenerator
from ..models.task import Message as MessageModel
from ..models.response import Response as ResponseModel
from ..models.task import RoleType
from ..utils.logging import log_chat_interaction, log_performance
from ..utils.error_handlers import MessageProcessingError, ConversationNotFoundError, ResponseGenerationError

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service class to handle chat interactions between users and the AI assistant.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.conversation_service = ConversationService(db_session)
        self.message_classifier = MessageClassifier()
        self.response_generator = ResponseGenerator()

    async def handle_message(self, conversation_id: str, user_message: str, user_id: str) -> str:
        """
        Handle a user message and generate an appropriate response.

        Args:
            conversation_id (str): The ID of the conversation
            user_message (str): The message from the user
            user_id (str): The ID of the user

        Returns:
            str: The AI assistant's response
        """
        start_time = datetime.now()

        try:
            # Validate inputs
            if not user_message or not user_message.strip():
                raise MessageProcessingError("User message cannot be empty")

            if len(user_message) > 10000:  # From config settings
                raise MessageProcessingError("User message exceeds maximum length")

            # Get the conversation
            conversation = self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(f"Conversation {conversation_id} not found")

            # Classify the message
            message_type = self.message_classifier.classify_message(user_message)
            logger.info(f"Classified message as: {message_type}")

            # Generate response
            response_content = self.response_generator.generate_response_with_validation(
                user_message=user_message,
                message_type=message_type
            )

            if not response_content:
                raise ResponseGenerationError("Failed to generate response")

            # Save the user message
            conversation_id_int = int(conversation_id)
            user_msg = MessageModel(
                conversation_id=conversation_id_int,
                role=RoleType.user,  # Use enum value
                content=user_message,
                timestamp=datetime.utcnow()
            )
            self.db.add(user_msg)
            self.db.flush()  # Flush to get the ID assigned before creating the response

            # Save the AI response
            # Note: user_msg.id is the integer ID of the message from the task.py model
            ai_response = ResponseModel(
                message_id=user_msg.id,  # Link to the user message (integer ID)
                content=response_content,
                generated_at=datetime.utcnow(),
                response_type=self._map_message_type_to_response_type(message_type),
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                confidence_score=0.8  # Placeholder for now
            )
            self.db.add(ai_response)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            self.db.commit()

            # Log the interaction
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            log_chat_interaction(
                user_id=user_id,
                conversation_id=conversation_id,
                message_content=user_message,
                response_content=response_content,
                processing_time=processing_time
            )

            # Log performance
            log_performance("response_generation_time", processing_time, "ms")

            logger.info(f"Successfully processed message. Response generated in {processing_time:.2f}ms")
            return response_content

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            self.db.rollback()
            raise

    def _map_message_type_to_response_type(self, message_type: str) -> str:
        """
        Map the message type to the appropriate response type.

        Args:
            message_type (str): The type of the incoming message

        Returns:
            str: The corresponding response type
        """
        mapping = {
            "task_related": "task_guidance",
            "greeting": "greeting",
            "non_task": "boundary_setting"
        }
        return mapping.get(message_type, "general")

    async def get_conversation_history(self, conversation_id: str, limit: int = 50, offset: int = 0) -> list:
        """
        Get the message history for a conversation.

        Args:
            conversation_id (str): The ID of the conversation
            limit (int): Maximum number of messages to return
            offset (int): Number of messages to skip

        Returns:
            list: List of messages in the conversation
        """
        try:
            messages = self.conversation_service.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit,
                offset=offset
            )

            return [msg.to_dict() for msg in messages]
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            raise

    async def start_new_conversation(self, user_id: str, initial_message: Optional[str] = None) -> str:
        """
        Start a new conversation for a user.

        Args:
            user_id (str): The ID of the user
            initial_message (Optional[str]): An optional first message to start the conversation

        Returns:
            str: The ID of the new conversation
        """
        try:
            conversation = self.conversation_service.create_conversation(
                user_id=user_id,
                title="New Chat",  # Default title
                initial_message=initial_message
            )

            logger.info(f"Started new conversation: {conversation.conversation_id}")
            return str(conversation.conversation_id)
        except Exception as e:
            logger.error(f"Error starting new conversation: {str(e)}")
            raise

    async def classify_message_async(self, message: str) -> str:
        """
        Asynchronously classify a message.

        Args:
            message (str): The message to classify

        Returns:
            str: The classification result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.message_classifier.classify_message, message)

    async def generate_response_async(self, user_message: str, message_type: str) -> str:
        """
        Asynchronously generate a response.

        Args:
            user_message (str): The user's message
            message_type (str): The type of the message

        Returns:
            str: The generated response
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.response_generator.generate_response_with_validation,
            user_message,
            message_type
        )

    def get_message_analysis(self, message: str) -> Dict[str, Any]:
        """
        Get detailed analysis of a message including classification and confidence scores.

        Args:
            message (str): The message to analyze

        Returns:
            Dict[str, Any]: Analysis results including classification and confidence scores
        """
        classification = self.message_classifier.classify_message(message)
        confidence_scores = self.message_classifier.get_confidence_scores(message)

        return {
            "classification": classification,
            "confidence_scores": confidence_scores,
            "timestamp": datetime.utcnow().isoformat()
        }