"""
Security Assessment model for the verification system.
This module defines the SecurityAssessment entity for tracking security scan results.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base
from enum import Enum as PyEnum


class SecurityScanType(PyEnum):
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"
    STATIC_ANALYSIS = "static_analysis"
    CONTAINER_SECURITY = "container_security"
    PENETRATION_TEST = "penetration_test"
    CONFIGURATION_AUDIT = "configuration_audit"


class SecurityScanStatus(PyEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class SecurityAssessment(Base):
    """
    SecurityAssessment model representing security scan results and assessments.
    """
    __tablename__ = "security_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(String(100), nullable=False, index=True)  # Unique identifier for the scan
    scan_type = Column(String(50), nullable=False)  # Type of security scan
    status = Column(String(20), default="in_progress")  # Current status of the scan
    critical_vulnerabilities = Column(Integer, default=0)  # Count of critical vulnerabilities
    high_vulnerabilities = Column(Integer, default=0)  # Count of high vulnerabilities
    medium_vulnerabilities = Column(Integer, default=0)  # Count of medium vulnerabilities
    low_vulnerabilities = Column(Integer, default=0)  # Count of low vulnerabilities
    findings = Column(Text)  # Detailed findings from the scan
    recommendations = Column(Text)  # Recommendations for addressing issues
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # When the scan was completed
    report_url = Column(String(500))  # URL to the detailed report
    is_automated = Column(Boolean, default=True)  # Whether this was an automated scan

    def __repr__(self):
        return f"<SecurityAssessment(id={self.id}, scan_id='{self.scan_id}', scan_type='{self.scan_type}', status='{self.status}')>"

    def to_dict(self):
        """
        Convert the security assessment to a dictionary representation
        """
        return {
            "id": str(self.id),
            "scan_id": self.scan_id,
            "scan_type": self.scan_type,
            "status": self.status,
            "critical_vulnerabilities": self.critical_vulnerabilities,
            "high_vulnerabilities": self.high_vulnerabilities,
            "medium_vulnerabilities": self.medium_vulnerabilities,
            "low_vulnerabilities": self.low_vulnerabilities,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "report_url": self.report_url,
            "is_automated": self.is_automated
        }