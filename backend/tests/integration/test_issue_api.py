"""
Integration tests for the issue tracking API endpoints.

This module contains integration tests for the issue tracking API endpoints,
testing the full request/response cycle including authentication, services,
and database operations.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.database import Base
from src.main import app
from src.models.user import User
from src.models.issue_tracker import IssueTracker, IssueSeverity, IssueStatus, IssueCategory


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


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
        email="admin@example.com",
        username="admin",
        hashed_password="hashed_password_123",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


class TestIssueAPI:
    """Integration tests for the issue tracking API endpoints."""

    def test_create_issue_unauthorized(self, client):
        """Test that creating an issue requires authentication."""
        issue_data = {
            "title": "Test Issue",
            "description": "A test issue description",
            "severity": "high",
            "category": "bug",
            "priority": 1
        }

        response = client.post("/api/v1/issues", json=issue_data)

        # Should return 401 or 403 because of authentication requirement
        assert response.status_code in [401, 403]

    def test_get_issues_unauthorized(self, client):
        """Test that getting issues requires authentication."""
        response = client.get("/api/v1/issues")

        # Should return 401 or 403 because of authentication requirement
        assert response.status_code in [401, 403]

    def test_get_single_issue_unauthorized(self, client):
        """Test that getting a single issue requires authentication."""
        response = client.get("/api/v1/issues/1")

        # Should return 401 or 403 because of authentication requirement
        assert response.status_code in [401, 403]

    def test_update_issue_unauthorized(self, client):
        """Test that updating an issue requires authentication."""
        update_data = {
            "status": "in_progress",
            "assignee_id": 1
        }

        response = client.put("/api/v1/issues/1", json=update_data)

        # Should return 401 or 403 because of authentication requirement
        assert response.status_code in [401, 403]

    def test_issue_lifecycle_integration(self, test_db, sample_user):
        """Test the complete issue lifecycle through the service layer."""
        from src.services.issue_service import IssueService

        service = IssueService(test_db)

        # 1. Create an issue
        created_issue = service.create_issue(
            title="Integration Test Issue",
            description="An issue created during integration testing",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.BUG,
            reported_by_id=sample_user.id,
            priority=1
        )

        assert created_issue is not None
        assert created_issue.title == "Integration Test Issue"
        assert created_issue.description == "An issue created during integration testing"
        assert created_issue.severity == IssueSeverity.HIGH
        assert created_issue.category == IssueCategory.BUG
        assert created_issue.status == IssueStatus.OPEN
        assert created_issue.reported_by_id == sample_user.id

        # 2. Get the issue by ID
        retrieved_issue = service.get_issue_by_id(created_issue.id)
        assert retrieved_issue is not None
        assert retrieved_issue.id == created_issue.id
        assert retrieved_issue.title == created_issue.title

        # 3. Update the issue status
        updated_issue = service.update_issue_status(
            issue_id=created_issue.id,
            new_status=IssueStatus.IN_PROGRESS,
            updated_by_id=sample_user.id
        )

        assert updated_issue is not None
        assert updated_issue.status == IssueStatus.IN_PROGRESS

        # 4. Add a comment to the issue
        commented_issue = service.add_comment_to_issue(
            issue_id=created_issue.id,
            comment="This issue is being worked on",
            author_id=sample_user.id
        )

        assert commented_issue is not None
        assert len(commented_issue.comments) == 1
        assert commented_issue.comments[0]["content"] == "This issue is being worked on"

        # 5. Close the issue
        closed_issue = service.update_issue_status(
            issue_id=created_issue.id,
            new_status=IssueStatus.CLOSED,
            updated_by_id=sample_user.id,
            resolution_note="Issue resolved successfully"
        )

        assert closed_issue is not None
        assert closed_issue.status == IssueStatus.CLOSED
        assert closed_issue.resolution_note == "Issue resolved successfully"

    def test_issue_filtering(self, test_db, sample_user):
        """Test filtering issues by various criteria."""
        from src.services.issue_service import IssueService

        service = IssueService(test_db)

        # Create multiple issues with different attributes
        issue1 = service.create_issue(
            title="High Priority Bug",
            description="A critical bug",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.BUG,
            reported_by_id=sample_user.id,
            priority=1
        )

        issue2 = service.create_issue(
            title="Low Priority Enhancement",
            description="A nice-to-have feature",
            severity=IssueSeverity.LOW,
            category=IssueCategory.ENHANCEMENT,
            reported_by_id=sample_user.id,
            priority=3
        )

        issue3 = service.create_issue(
            title="Medium Priority Task",
            description="A routine task",
            severity=IssueSeverity.MEDIUM,
            category=IssueCategory.TASK,
            reported_by_id=sample_user.id,
            priority=2
        )

        # Test filtering by severity
        high_severity_issues = service.get_issues_by_severity(IssueSeverity.HIGH)
        assert len(high_severity_issues) >= 1
        for issue in high_severity_issues:
            assert issue.severity == IssueSeverity.HIGH

        # Test filtering by status
        open_issues = service.get_issues_by_status(IssueStatus.OPEN)
        assert len(open_issues) >= 3  # All issues should be open initially

        # Test filtering by category
        bug_issues = service.get_issues_by_category(IssueCategory.BUG)
        assert len(bug_issues) >= 1
        for issue in bug_issues:
            assert issue.category == IssueCategory.BUG

        # Test getting all issues
        all_issues = service.get_all_issues()
        assert len(all_issues) >= 3

    def test_issue_search(self, test_db, sample_user):
        """Test searching issues by title or description."""
        from src.services.issue_service import IssueService

        service = IssueService(test_db)

        # Create issues with searchable content
        issue1 = service.create_issue(
            title="Database Connection Timeout",
            description="The database connection is timing out frequently",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.BUG,
            reported_by_id=sample_user.id
        )

        issue2 = service.create_issue(
            title="UI Button Alignment",
            description="The submit button is not aligned properly",
            severity=IssueSeverity.LOW,
            category=IssueCategory.TASK,
            reported_by_id=sample_user.id
        )

        # Test searching for issues containing "database"
        database_issues = service.search_issues("database")
        assert len(database_issues) >= 1
        for issue in database_issues:
            assert "database" in issue.title.lower() or "database" in issue.description.lower()

        # Test searching for issues containing "button"
        button_issues = service.search_issues("button")
        assert len(button_issues) >= 1
        for issue in button_issues:
            assert "button" in issue.title.lower() or "button" in issue.description.lower()

    def test_issue_statistics(self, test_db, sample_user):
        """Test getting issue statistics."""
        from src.services.issue_service import IssueService

        service = IssueService(test_db)

        # Create issues with different statuses and severities
        service.create_issue(
            title="Critical Bug",
            description="A critical issue",
            severity=IssueSeverity.CRITICAL,
            category=IssueCategory.BUG,
            reported_by_id=sample_user.id
        )

        service.create_issue(
            title="High Priority Task",
            description="Important task",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.TASK,
            reported_by_id=sample_user.id
        )

        service.create_issue(
            title="Low Priority Enhancement",
            description="Nice to have",
            severity=IssueSeverity.LOW,
            category=IssueCategory.ENHANCEMENT,
            reported_by_id=sample_user.id
        )

        # Update one issue to closed status
        all_issues = service.get_all_issues()
        if all_issues:
            service.update_issue_status(
                issue_id=all_issues[0].id,
                new_status=IssueStatus.CLOSED,
                updated_by_id=sample_user.id
            )

        # Get statistics
        stats = service.get_issue_statistics()

        assert "total_issues" in stats
        assert "open_issues" in stats
        assert "closed_issues" in stats
        assert "by_severity" in stats
        assert "by_category" in stats

        assert stats["total_issues"] >= 3
        assert stats["by_severity"][IssueSeverity.CRITICAL.value] >= 1
        assert stats["by_category"][IssueCategory.BUG.value] >= 1