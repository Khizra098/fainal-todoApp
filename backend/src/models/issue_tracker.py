"""
Issue Tracker model for the verification system.
This module defines the IssueTracker entity for tracking bugs and issues.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base
from enum import Enum as PyEnum


class IssueSeverity(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(PyEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"
    DUPLICATE = "duplicate"


class IssueCategory(PyEnum):
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    SECURITY = "security"
    PERFORMANCE = "performance"


class IssueTracker(Base):
    """
    IssueTracker model representing an issue, bug, or task that needs attention.
    """
    __tablename__ = "issue_tracker"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)  # Brief title of the issue
    description = Column(Text)  # Detailed description of the issue
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.MEDIUM, nullable=False)
    status = Column(Enum(IssueStatus), default=IssueStatus.NEW, nullable=False)
    category = Column(Enum(IssueCategory), default=IssueCategory.BUG, nullable=False)
    component = Column(String(100))  # Which component is affected (e.g., frontend, backend, auth)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)  # When the issue was resolved
    reported_by = Column(String(100))  # Who reported the issue
    assigned_to = Column(String(100))  # Who is assigned to fix the issue
    resolution_notes = Column(Text)  # Notes about how the issue was resolved
    is_reopened = Column(Boolean, default=False)  # Whether the issue was reopened after resolution

    def __repr__(self):
        return f"<IssueTracker(id={self.id}, title='{self.title}', severity='{self.severity}', status='{self.status}')>"

    def to_dict(self):
        """
        Convert the issue tracker entry to a dictionary representation
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "category": self.category.value if self.category else None,
            "component": self.component,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "reported_by": self.reported_by,
            "assigned_to": self.assigned_to,
            "resolution_notes": self.resolution_notes,
            "is_reopened": self.is_reopened
        }