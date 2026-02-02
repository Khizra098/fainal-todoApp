"""
Response model for the AI Assistant Chat feature.
This module defines the Response entity and its relationships.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base


class Response(Base):
    """
    Response model representing the AI assistant's response to a user message,
    including the processing details.
    """
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, nullable=False)  # Reference to the user message being responded to (no FK constraint for now)
    content = Column(Text, nullable=False)  # The AI assistant's response content
    generated_at = Column(DateTime, default=datetime.utcnow)  # When the response was generated
    response_type = Column(String)  # 'task_guidance', 'greeting', 'boundary_setting'
    processing_time_ms = Column(Integer)  # Time taken to generate the response in milliseconds
    confidence_score = Column(Float)  # Confidence in the appropriateness of the response (0.0 to 1.0)

    def __repr__(self):
        return f"<Response(response_id={self.response_id}, message_id={self.message_id}, response_type='{self.response_type}')>"

    def to_dict(self):
        """
        Convert the response to a dictionary representation
        """
        return {
            "response_id": self.response_id,
            "message_id": self.message_id,
            "content": self.content,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "response_type": self.response_type,
            "processing_time_ms": self.processing_time_ms,
            "confidence_score": self.confidence_score
        }