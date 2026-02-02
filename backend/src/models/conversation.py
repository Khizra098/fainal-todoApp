"""
Conversation model for the AI Assistant Chat feature.
This module defines the Conversation entity and its relationships.
"""

from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base


class Conversation(Base):
    """
    Conversation model representing a single conversation thread
    between a user and the AI assistant.
    """
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String, nullable=False)  # Reference to the user who initiated the conversation
    title = Column(String(200), nullable=False)  # Auto-generated from first message, max 200 chars
    status = Column(SQLEnum("active", "archived", "suspended", name="conversation_status"), default="active", nullable=False)
    extra_data = Column(Text)  # JSON-formatted string for additional conversation properties

    def __repr__(self):
        return f"<Conversation(conversation_id={self.conversation_id}, user_id='{self.user_id}', title='{self.title}', status='{self.status}')>"

    def to_dict(self):
        """
        Convert the conversation to a dictionary representation
        """
        return {
            "conversation_id": str(self.conversation_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "extra_data": self.extra_data
        }