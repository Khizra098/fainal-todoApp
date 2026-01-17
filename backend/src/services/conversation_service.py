"""Conversation service for managing conversation threads with database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..models.task import Conversation, Message, RoleType, ConversationStatus
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

    def create_conversation(self, user_id: int, title: str = "New Conversation") -> Conversation:
        """
        Create a new conversation thread.

        Args:
            user_id: ID of the user starting the conversation
            title: Title for the conversation (default: "New Conversation")

        Returns:
            The newly created Conversation object

        Raises:
            ValueError: If title is empty or None
        """
        if not title or not title.strip():
            raise ValueError("Conversation title cannot be empty")

        conversation = Conversation(
            user_id=user_id,
            title=title.strip(),
            status=ConversationStatus.active
        )

        try:
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to create conversation for user {user_id}")

    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """
        Get a specific conversation by its ID for a specific user.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the user who owns the conversation

        Returns:
            Conversation object if found and belongs to user, None otherwise
        """
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_user_conversations(self, user_id: int, status: Optional[ConversationStatus] = None) -> List[Conversation]:
        """
        Get all conversations for a specific user with optional status filtering.

        Args:
            user_id: ID of the user whose conversations to retrieve
            status: Optional status to filter conversations by

        Returns:
            List of Conversation objects for the user
        """
        query = self.db.query(Conversation).filter(Conversation.user_id == user_id)

        if status:
            query = query.filter(Conversation.status == status)

        return query.all()

    def update_conversation_status(self, conversation_id: int, user_id: int, status: ConversationStatus) -> bool:
        """
        Update the status of a conversation.

        Args:
            conversation_id: ID of the conversation to update
            user_id: ID of the user who owns the conversation
            status: New status for the conversation

        Returns:
            True if the conversation was updated, False if not found or not owned by user
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            conversation.status = status
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(conversation)
            return True
        return False

    def archive_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Archive a conversation.

        Args:
            conversation_id: ID of the conversation to archive
            user_id: ID of the user who owns the conversation

        Returns:
            True if the conversation was archived, False if not found or not owned by user
        """
        return self.update_conversation_status(conversation_id, user_id, ConversationStatus.archived)

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Delete a conversation by its ID for a specific user.

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user who owns the conversation

        Returns:
            True if the conversation was deleted, False if not found or not owned by user
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    def add_message_to_conversation(self, conversation_id: int, user_id: int, role: RoleType, content: str) -> Optional[Message]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation to add message to
            user_id: ID of the user who owns the conversation
            role: Role of the message sender (user, assistant, system)
            content: Content of the message

        Returns:
            The newly created Message object, or None if conversation not found
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = Message(
            conversation_id=conversation_id,
            role=role,
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

    def get_messages_for_conversation(self, conversation_id: int, user_id: int) -> List[Message]:
        """
        Get all messages for a specific conversation.

        Args:
            conversation_id: ID of the conversation to get messages for
            user_id: ID of the user who owns the conversation

        Returns:
            List of Message objects for the conversation
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []

        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()