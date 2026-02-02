"""
Feature model for the verification system.
This module defines the Feature entity for tracking feature verification status.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base


class Feature(Base):
    """
    Feature model representing a feature that needs to be verified against specifications.
    """
    __tablename__ = "features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)  # Feature name
    description = Column(Text)  # Detailed description of the feature
    specification_reference = Column(String(200))  # Reference to the original specification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Whether the feature is active in the system

    def __repr__(self):
        return f"<Feature(id={self.id}, name='{self.name}', specification_reference='{self.specification_reference}')>"

    def to_dict(self):
        """
        Convert the feature to a dictionary representation
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "specification_reference": self.specification_reference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }