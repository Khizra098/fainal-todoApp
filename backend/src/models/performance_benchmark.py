"""
Performance Benchmark model for the verification system.
This module defines the PerformanceBenchmark entity for tracking performance metrics.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database.database import Base
from enum import Enum as PyEnum


class PerformanceMetricType(PyEnum):
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_HIT_RATE = "cache_hit_rate"


class PerformanceStatus(PyEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class PerformanceBenchmark(Base):
    """
    PerformanceBenchmark model representing performance metrics and benchmarks.
    """
    __tablename__ = "performance_benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_name = Column(String(200), nullable=False)  # Name of the performance test
    metric_type = Column(String(50), nullable=False)  # Type of metric being measured
    current_value = Column(Float, nullable=False)  # Current measured value
    target_value = Column(Float, nullable=False)  # Target value for this metric
    unit = Column(String(20))  # Unit of measurement (e.g., ms, requests_per_second, MB)
    status = Column(String(10), default="pass")  # Current status (pass, warn, fail)
    description = Column(Text)  # Description of what this benchmark measures
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)  # When this benchmark was last run
    is_active = Column(Boolean, default=True)  # Whether this benchmark is currently active

    def __repr__(self):
        return f"<PerformanceBenchmark(id={self.id}, test_name='{self.test_name}', metric_type='{self.metric_type}', status='{self.status}')>"

    def to_dict(self):
        """
        Convert the performance benchmark to a dictionary representation
        """
        return {
            "id": str(self.id),
            "test_name": self.test_name,
            "metric_type": self.metric_type,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "unit": self.unit,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "is_active": self.is_active
        }