"""
Deployment Configuration model for the verification system.
This module defines the DeploymentConfig entity for tracking deployment settings.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base
from enum import Enum as PyEnum


class EnvironmentType(PyEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentConfig(Base):
    """
    DeploymentConfig model representing deployment configuration settings.
    """
    __tablename__ = "deployment_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment = Column(String(20), default="development")  # Environment type
    database_url = Column(String(500))  # Database connection string
    api_endpoints = Column(Text)  # JSON string of API endpoints
    resource_limits_cpu = Column(String(20))  # CPU resource limit (e.g., "500m")
    resource_limits_memory = Column(String(20))  # Memory resource limit (e.g., "512Mi")
    replica_counts_backend = Column(Integer, default=1)  # Number of backend replicas
    replica_counts_frontend = Column(Integer, default=1)  # Number of frontend replicas
    liveness_path = Column(String(200))  # Path for liveness probe
    readiness_path = Column(String(200))  # Path for readiness probe
    probe_interval_seconds = Column(Integer, default=30)  # Interval for health checks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Whether this config is currently active

    def __repr__(self):
        return f"<DeploymentConfig(id={self.id}, environment='{self.environment}', is_active={self.is_active})>"

    def to_dict(self):
        """
        Convert the deployment configuration to a dictionary representation
        """
        return {
            "id": str(self.id),
            "environment": self.environment,
            "database_url": self.database_url,
            "api_endpoints": self.api_endpoints,
            "resource_limits": {
                "cpu": self.resource_limits_cpu,
                "memory": self.resource_limits_memory
            },
            "replica_counts": {
                "backend": self.replica_counts_backend,
                "frontend": self.replica_counts_frontend
            },
            "health_check_config": {
                "liveness_path": self.liveness_path,
                "readiness_path": self.readiness_path,
                "interval_seconds": self.probe_interval_seconds
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }