"""
Verification Report model for the verification system.
This module defines the VerificationReport entity for tracking verification results.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base
from enum import Enum as PyEnum


class VerificationStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class VerificationResult(PyEnum):
    PASS = "pass"
    FAIL = "fail"
    NEEDS_WORK = "needs_work"


class VerificationReport(Base):
    """
    VerificationReport model representing the results of a feature verification process.
    """
    __tablename__ = "verification_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(UUID(as_uuid=True), ForeignKey("features.id"), nullable=False)
    verification_type = Column(String(50), default="automated")  # automated, manual, or both
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    result = Column(Enum(VerificationResult), nullable=True)  # Result after completion
    findings = Column(Text)  # Detailed findings from the verification
    recommendations = Column(Text)  # Recommendations for improvements
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # When the verification was completed

    def __repr__(self):
        return f"<VerificationReport(id={self.id}, feature_id={self.feature_id}, status='{self.status}', result='{self.result}')>"

    def to_dict(self):
        """
        Convert the verification report to a dictionary representation
        """
        return {
            "id": str(self.id),
            "feature_id": str(self.feature_id),
            "verification_type": self.verification_type,
            "status": self.status.value if self.status else None,
            "result": self.result.value if self.result else None,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }