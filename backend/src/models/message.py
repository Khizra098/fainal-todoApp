"""
Message model for the AI Assistant Chat feature.
This module defines the Message entity and its relationships.
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base


class Message(Base):
    """
    Message model representing a single message in a conversation,
    either from the user or the AI assistant.
    """
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    sender_type = Column(String, nullable=False)  # 'user' or 'ai_assistant'
    content = Column(Text, nullable=False)  # The actual message content
    timestamp = Column(DateTime, default=datetime.utcnow)  # When the message was sent
    message_type = Column(String)  # 'task_related', 'greeting', 'non_task', 'response'
    sentiment_score = Column(String)  # Sentiment analysis score as string (-1.0 to 1.0)

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, conversation_id={self.conversation_id}, sender_type='{self.sender_type}')>"

    def to_dict(self):
        """
        Convert the message to a dictionary representation
        """
        return {
            "message_id": str(self.message_id),
            "conversation_id": str(self.conversation_id),
            "sender_type": self.sender_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message_type": self.message_type,
            "sentiment_score": self.sentiment_score
        }