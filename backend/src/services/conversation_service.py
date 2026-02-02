"""Conversation service for managing conversation threads with database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..models.task import Conversation as ConversationModel, Message as MessageModel
from ..database import get_db


class ConversationService:
    """
    Service class for managing conversation operations (CRUD functionality) with database persistence.
    """

    def __init__(self, db: Session):
        """
        Initialize the ConversationService with a database session.

        Args:
            db: Database session for operations
        """
        self.db = db

    def create_conversation(self, user_id: str, title: str = "New Chat", initial_message: str = None) -> ConversationModel:
        """
        Create a new conversation thread.

        Args:
            user_id: ID of the user starting the conversation
            title: Title for the conversation (default: "New Chat")
            initial_message: Optional first message to generate title from

        Returns:
            The newly created Conversation object
        """
        if not title or not title.strip():
            if initial_message and initial_message.strip():
                # Generate title from first few words of the initial message
                words = initial_message.strip().split()[:5]  # Take first 5 words
                title = " ".join(words)
                if len(initial_message.strip().split()) > 5:
                    title += "..."
            else:
                title = "New Chat"

        # Convert user_id to integer for the task model
        user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id

        conversation = ConversationModel(
            user_id=user_id_int,
            title=title.strip(),
            status="active"
        )

        try:
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to create conversation for user {user_id}")

    def get_conversation(self, conversation_id: str) -> Optional[ConversationModel]:
        """
        Get a specific conversation by its ID.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Conversation object if found, None otherwise
        """
        try:
            conversation_id_int = int(conversation_id)
            return self.db.query(ConversationModel).filter(
                ConversationModel.id == conversation_id_int
            ).first()
        except ValueError:
            # If conversion to int fails, return None
            return None

    def get_conversation_by_user(self, conversation_id: str, user_id: str) -> Optional[ConversationModel]:
        """
        Get a specific conversation by its ID for a specific user.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the user who owns the conversation

        Returns:
            Conversation object if found and belongs to user, None otherwise
        """
        try:
            conversation_id_int = int(conversation_id)
            user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
            return self.db.query(ConversationModel).filter(
                ConversationModel.id == conversation_id_int,
                ConversationModel.user_id == user_id_int
            ).first()
        except ValueError:
            # If conversion to int fails, return None
            return None

    def get_user_conversations(self, user_id: str, status: Optional[str] = None) -> List[ConversationModel]:
        """
        Get all conversations for a specific user with optional status filtering.

        Args:
            user_id: ID of the user whose conversations to retrieve
            status: Optional status to filter conversations by

        Returns:
            List of Conversation objects for the user
        """
        user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
        query = self.db.query(ConversationModel).filter(ConversationModel.user_id == user_id_int)

        if status:
            query = query.filter(ConversationModel.status == status)

        return query.all()

    def update_conversation_status(self, conversation_id: str, user_id: str, status: str) -> bool:
        """
        Update the status of a conversation.

        Args:
            conversation_id: ID of the conversation to update
            user_id: ID of the user who owns the conversation
            status: New status for the conversation

        Returns:
            True if the conversation was updated, False if not found or not owned by user
        """
        conversation = self.get_conversation_by_user(conversation_id, user_id)
        if conversation:
            conversation.status = status
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(conversation)
            return True
        return False

    def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Archive a conversation.

        Args:
            conversation_id: ID of the conversation to archive
            user_id: ID of the user who owns the conversation

        Returns:
            True if the conversation was archived, False if not found or not owned by user
        """
        return self.update_conversation_status(conversation_id, user_id, "archived")

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation by its ID for a specific user.

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user who owns the conversation

        Returns:
            True if the conversation was deleted, False if not found or not owned by user
        """
        conversation = self.get_conversation_by_user(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    def add_message_to_conversation(self, conversation_id: str, user_id: str, sender_type: str, content: str) -> Optional[MessageModel]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation to add message to
            user_id: ID of the user who owns the conversation
            sender_type: Type of the message sender ('user' or 'ai_assistant')
            content: Content of the message

        Returns:
            The newly created Message object, or None if conversation not found
        """
        conversation = self.get_conversation_by_user(conversation_id, user_id)
        if not conversation:
            return None

        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        try:
            conversation_id_int = int(conversation_id)
        except ValueError:
            return None

        message = MessageModel(
            conversation_id=conversation_id_int,
            sender_type=sender_type,
            content=content.strip()
        )

        try:
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            self.db.commit()

            return message
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to add message to conversation {conversation_id}")

    def get_conversation_messages(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[MessageModel]:
        """
        Get messages for a specific conversation.

        Args:
            conversation_id: ID of the conversation to get messages for
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message objects for the conversation
        """
        try:
            conversation_id_int = int(conversation_id)
            return self.db.query(MessageModel).filter(
                MessageModel.conversation_id == conversation_id_int
            ).order_by(MessageModel.timestamp.desc()).offset(offset).limit(limit).all()
        except ValueError:
            # If conversion to int fails, return empty list
            return []