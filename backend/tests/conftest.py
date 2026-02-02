"""
Base test configuration and fixtures for unit tests.

This module provides common fixtures and configuration for all unit tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.database import Base
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.feature import Feature
from src.models.verification_report import VerificationReport
from src.models.issue_tracker import IssueTracker
from src.models.performance_benchmark import PerformanceBenchmark
from src.models.security_assessment import SecurityAssessment
from src.models.deployment_config import DeploymentConfig


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_feature(test_db):
    """Create a sample feature for testing."""
    feature = Feature(
        name="Test Feature",
        description="A test feature for verification",
        specification_reference="SPEC-001"
    )
    test_db.add(feature)
    test_db.commit()
    test_db.refresh(feature)
    return feature


@pytest.fixture
def sample_issue(test_db):
    """Create a sample issue for testing."""
    issue = IssueTracker(
        title="Sample Issue",
        description="A sample issue for testing",
        severity="high",
        status="open",
        category="bug"
    )
    test_db.add(issue)
    test_db.commit()
    test_db.refresh(issue)
    return issue