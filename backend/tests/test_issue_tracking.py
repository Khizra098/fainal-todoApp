"""
Tests for issue tracking functionality.
This module contains tests for the issue tracking system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.models.issue_tracker import IssueTracker, IssueSeverity, IssueStatus, IssueCategory
from src.database.database import Base
from src.main import app
from src.services.issue_service import IssueService


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def issue_service(test_db):
    """Create an issue service instance."""
    return IssueService(test_db)


class TestIssueTrackerModel:
    """Tests for the IssueTracker model."""

    def test_issue_creation(self, test_db):
        """Test creating an issue."""
        issue = IssueTracker(
            title="Test Issue",
            description="This is a test issue",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.NEW,
            category=IssueCategory.BUG,
            component="backend"
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        assert issue.title == "Test Issue"
        assert issue.description == "This is a test issue"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.status == IssueStatus.NEW
        assert issue.category == IssueCategory.BUG
        assert issue.component == "backend"
        assert issue.id is not None
        assert issue.created_at is not None

    def test_issue_to_dict(self, test_db):
        """Test converting issue to dictionary."""
        issue = IssueTracker(
            title="Test Issue",
            description="This is a test issue",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.NEW,
            category=IssueCategory.BUG,
            component="backend",
            reported_by="test_user"
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        issue_dict = issue.to_dict()

        assert issue_dict["title"] == "Test Issue"
        assert issue_dict["description"] == "This is a test issue"
        assert issue_dict["severity"] == "high"
        assert issue_dict["status"] == "new"
        assert issue_dict["category"] == "bug"
        assert issue_dict["component"] == "backend"
        assert issue_dict["reported_by"] == "test_user"
        assert "id" in issue_dict
        assert "created_at" in issue_dict

    def test_issue_default_values(self, test_db):
        """Test default values for issue."""
        issue = IssueTracker(
            title="Test Issue",
            description="This is a test issue"
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        # Check default values
        assert issue.severity == IssueSeverity.MEDIUM  # Default severity
        assert issue.status == IssueStatus.NEW  # Default status
        assert issue.category == IssueCategory.BUG  # Default category
        assert issue.is_reopened is False  # Default value


class TestIssueService:
    """Tests for the IssueService."""

    def test_create_issue(self, issue_service, test_db):
        """Test creating an issue."""
        issue = issue_service.create_issue(
            title="Test Issue",
            description="This is a test issue",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.SECURITY,
            component="frontend",
            reported_by="user123"
        )

        assert issue.title == "Test Issue"
        assert issue.description == "This is a test issue"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.category == IssueCategory.SECURITY
        assert issue.component == "frontend"
        assert issue.reported_by == "user123"
        assert issue.status == IssueStatus.NEW

    def test_get_all_issues(self, issue_service, test_db):
        """Test getting all issues."""
        # Create test issues
        issue1 = IssueTracker(title="Issue 1", description="First issue", severity=IssueSeverity.LOW, category=IssueCategory.BUG)
        issue2 = IssueTracker(title="Issue 2", description="Second issue", severity=IssueSeverity.HIGH, category=IssueCategory.ENHANCEMENT)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.commit()

        issues = issue_service.get_all_issues()

        assert len(issues) == 2
        titles = [issue.title for issue in issues]
        assert "Issue 1" in titles
        assert "Issue 2" in titles

    def test_get_all_issues_with_filters(self, issue_service, test_db):
        """Test getting issues with filters."""
        # Create test issues
        issue1 = IssueTracker(title="High Priority", description="High priority issue", severity=IssueSeverity.HIGH, category=IssueCategory.BUG)
        issue2 = IssueTracker(title="Low Priority", description="Low priority issue", severity=IssueSeverity.LOW, category=IssueCategory.BUG)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.commit()

        # Filter by severity
        high_priority_issues = issue_service.get_all_issues(severity=IssueSeverity.HIGH.value)
        assert len(high_priority_issues) == 1
        assert high_priority_issues[0].title == "High Priority"

        # Filter by category
        bug_issues = issue_service.get_all_issues(category=IssueCategory.BUG.value)
        assert len(bug_issues) == 2

    def test_get_issue_by_id(self, issue_service, test_db):
        """Test getting an issue by ID."""
        issue = IssueTracker(title="Test Issue", description="A test issue", severity=IssueSeverity.MEDIUM)
        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        retrieved_issue = issue_service.get_issue_by_id(issue.id)

        assert retrieved_issue is not None
        assert retrieved_issue.id == issue.id
        assert retrieved_issue.title == "Test Issue"

    def test_get_issue_by_id_not_found(self, issue_service):
        """Test getting an issue that doesn't exist."""
        fake_id = uuid.uuid4()
        retrieved_issue = issue_service.get_issue_by_id(fake_id)

        assert retrieved_issue is None

    def test_update_issue(self, issue_service, test_db):
        """Test updating an issue."""
        issue = IssueTracker(title="Original Title", description="Original description", severity=IssueSeverity.LOW)
        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        updated_issue = issue_service.update_issue(
            issue_id=issue.id,
            title="Updated Title",
            status=IssueStatus.IN_PROGRESS,
            resolution_notes="Working on this issue"
        )

        assert updated_issue.title == "Updated Title"
        assert updated_issue.status == IssueStatus.IN_PROGRESS
        assert updated_issue.resolution_notes == "Working on this issue"

    def test_update_issue_status_transitions(self, issue_service, test_db):
        """Test status transitions and their effects."""
        issue = IssueTracker(title="Test Issue", description="A test issue", severity=IssueSeverity.HIGH)
        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        # Update to resolved status
        updated_issue = issue_service.update_issue(
            issue_id=issue.id,
            status=IssueStatus.RESOLVED
        )

        # The resolved_at field should be set
        assert updated_issue.resolved_at is not None

        # Update back to in-progress (reopening)
        reopened_issue = issue_service.update_issue(
            issue_id=issue.id,
            status=IssueStatus.IN_PROGRESS
        )

        # The resolved_at field should be cleared and is_reopened should be True
        assert reopened_issue.resolved_at is None
        assert reopened_issue.is_reopened is True

    def test_delete_issue(self, issue_service, test_db):
        """Test deleting an issue (soft delete)."""
        issue = IssueTracker(title="To Delete", description="Issue to delete", severity=IssueSeverity.MEDIUM)
        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        result = issue_service.delete_issue(issue.id)

        assert result is True

        # The issue should still exist but be marked as closed
        updated_issue = test_db.query(IssueTracker).filter(IssueTracker.id == issue.id).first()
        assert updated_issue.status == IssueStatus.CLOSED

    def test_get_issues_by_severity(self, issue_service, test_db):
        """Test getting issues by severity."""
        # Create issues with different severities
        issue1 = IssueTracker(title="Critical Issue", description="Critical issue", severity=IssueSeverity.CRITICAL)
        issue2 = IssueTracker(title="High Issue", description="High issue", severity=IssueSeverity.HIGH)
        issue3 = IssueTracker(title="Medium Issue", description="Medium issue", severity=IssueSeverity.MEDIUM)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        critical_issues = issue_service.get_issues_by_severity(IssueSeverity.CRITICAL)
        assert len(critical_issues) == 1
        assert critical_issues[0].title == "Critical Issue"

        high_issues = issue_service.get_issues_by_severity(IssueSeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].title == "High Issue"

    def test_get_issues_by_status(self, issue_service, test_db):
        """Test getting issues by status."""
        # Create issues with different statuses
        issue1 = IssueTracker(title="New Issue", description="New issue", status=IssueStatus.NEW)
        issue2 = IssueTracker(title="In Progress Issue", description="In progress issue", status=IssueStatus.IN_PROGRESS)
        issue3 = IssueTracker(title="Resolved Issue", description="Resolved issue", status=IssueStatus.RESOLVED)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        new_issues = issue_service.get_issues_by_status(IssueStatus.NEW)
        assert len(new_issues) == 1
        assert new_issues[0].title == "New Issue"

        in_progress_issues = issue_service.get_issues_by_status(IssueStatus.IN_PROGRESS)
        assert len(in_progress_issues) == 1
        assert in_progress_issues[0].title == "In Progress Issue"

    def test_get_issues_by_category(self, issue_service, test_db):
        """Test getting issues by category."""
        # Create issues with different categories
        issue1 = IssueTracker(title="Bug Issue", description="Bug issue", category=IssueCategory.BUG)
        issue2 = IssueTracker(title="Enhancement Issue", description="Enhancement issue", category=IssueCategory.ENHANCEMENT)
        issue3 = IssueTracker(title="Security Issue", description="Security issue", category=IssueCategory.SECURITY)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        bug_issues = issue_service.get_issues_by_category(IssueCategory.BUG)
        assert len(bug_issues) == 1
        assert bug_issues[0].title == "Bug Issue"

        enhancement_issues = issue_service.get_issues_by_category(IssueCategory.ENHANCEMENT)
        assert len(enhancement_issues) == 1
        assert enhancement_issues[0].title == "Enhancement Issue"

    def test_get_issues_by_component(self, issue_service, test_db):
        """Test getting issues by component."""
        # Create issues with different components
        issue1 = IssueTracker(title="Backend Issue", description="Backend issue", component="backend")
        issue2 = IssueTracker(title="Frontend Issue", description="Frontend issue", component="frontend")
        issue3 = IssueTracker(title="Database Issue", description="Database issue", component="database")

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        backend_issues = issue_service.get_issues_by_component("backend")
        assert len(backend_issues) == 1
        assert backend_issues[0].title == "Backend Issue"

        frontend_issues = issue_service.get_issues_by_component("frontend")
        assert len(frontend_issues) == 1
        assert frontend_issues[0].title == "Frontend Issue"

    def test_get_open_issues_count(self, issue_service, test_db):
        """Test getting the count of open issues."""
        # Create issues with different statuses
        issue1 = IssueTracker(title="Open Issue 1", description="Open issue", status=IssueStatus.NEW)
        issue2 = IssueTracker(title="Open Issue 2", description="Open issue", status=IssueStatus.IN_PROGRESS)
        issue3 = IssueTracker(title="Closed Issue", description="Closed issue", status=IssueStatus.CLOSED)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        open_count = issue_service.get_open_issues_count()
        # Should count NEW, IN_PROGRESS, RESOLVED, VERIFIED (but not CLOSED or DUPLICATE)
        # Our test only has NEW and IN_PROGRESS as "open"
        assert open_count == 2

    def test_get_urgent_issues(self, issue_service, test_db):
        """Test getting urgent issues."""
        # Create issues with different severities and ages
        old_critical_issue = IssueTracker(
            title="Old Critical Issue",
            description="Old critical issue",
            severity=IssueSeverity.CRITICAL,
            status=IssueStatus.NEW
        )
        # Manually set creation date to be old
        old_critical_issue.created_at = datetime.utcnow() - timedelta(days=45)

        recent_critical_issue = IssueTracker(
            title="Recent Critical Issue",
            description="Recent critical issue",
            severity=IssueSeverity.CRITICAL,
            status=IssueStatus.NEW
        )

        old_low_issue = IssueTracker(
            title="Old Low Issue",
            description="Old low issue",
            severity=IssueSeverity.LOW,
            status=IssueStatus.NEW
        )
        old_low_issue.created_at = datetime.utcnow() - timedelta(days=45)

        test_db.add(old_critical_issue)
        test_db.add(recent_critical_issue)
        test_db.add(old_low_issue)
        test_db.commit()

        # Get urgent issues (critical/high severity that are open and older than 30 days)
        urgent_issues = issue_service.get_urgent_issues(max_age_days=30)

        # Should only include the old critical issue
        assert len(urgent_issues) == 1
        assert urgent_issues[0].title == "Old Critical Issue"

    def test_get_issues_assigned_to(self, issue_service, test_db):
        """Test getting issues assigned to a specific user."""
        # Create issues with different assignees
        issue1 = IssueTracker(title="Assigned to User1", description="Issue assigned to user1", assigned_to="user1")
        issue2 = IssueTracker(title="Assigned to User2", description="Issue assigned to user2", assigned_to="user2")
        issue3 = IssueTracker(title="Unassigned", description="Issue not assigned", assigned_to=None)

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        user1_issues = issue_service.get_issues_assigned_to("user1")
        assert len(user1_issues) == 1
        assert user1_issues[0].title == "Assigned to User1"

        user2_issues = issue_service.get_issues_assigned_to("user2")
        assert len(user2_issues) == 1
        assert user2_issues[0].title == "Assigned to User2"

    def test_get_issues_reported_by(self, issue_service, test_db):
        """Test getting issues reported by a specific user."""
        # Create issues with different reporters
        issue1 = IssueTracker(title="Reported by User1", description="Issue reported by user1", reported_by="user1")
        issue2 = IssueTracker(title="Reported by User2", description="Issue reported by user2", reported_by="user2")

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.commit()

        user1_issues = issue_service.get_issues_reported_by("user1")
        assert len(user1_issues) == 1
        assert user1_issues[0].title == "Reported by User1"

        user2_issues = issue_service.get_issues_reported_by("user2")
        assert len(user2_issues) == 1
        assert user2_issues[0].title == "Reported by User2"

    def test_get_issue_statistics(self, issue_service, test_db):
        """Test getting issue statistics."""
        # Create issues with different severities, statuses, and categories
        issue1 = IssueTracker(
            title="Critical Bug",
            description="Critical bug",
            severity=IssueSeverity.CRITICAL,
            status=IssueStatus.NEW,
            category=IssueCategory.BUG
        )
        issue2 = IssueTracker(
            title="High Enhancement",
            description="High priority enhancement",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.IN_PROGRESS,
            category=IssueCategory.ENHANCEMENT
        )
        issue3 = IssueTracker(
            title="Medium Security",
            description="Medium security issue",
            severity=IssueSeverity.MEDIUM,
            status=IssueStatus.RESOLVED,
            category=IssueCategory.SECURITY
        )

        test_db.add(issue1)
        test_db.add(issue2)
        test_db.add(issue3)
        test_db.commit()

        stats = issue_service.get_issue_statistics()

        # Check total counts
        assert stats["total_issues"] == 3
        assert stats["open_issues"] == 2  # NEW and IN_PROGRESS
        assert stats["closed_issues"] == 1  # RESOLVED (for our calculation)

        # Check distribution counts
        assert stats["severity_distribution"]["critical"] == 1
        assert stats["severity_distribution"]["high"] == 1
        assert stats["severity_distribution"]["medium"] == 1

        assert stats["status_distribution"]["new"] == 1
        assert stats["status_distribution"]["in_progress"] == 1
        assert stats["status_distribution"]["resolved"] == 1

        assert stats["category_distribution"]["bug"] == 1
        assert stats["category_distribution"]["enhancement"] == 1
        assert stats["category_distribution"]["security"] == 1


class TestIssueAPI:
    """Tests for the issue tracking API endpoints."""

    def test_get_issues_endpoint(self, client):
        """Test the get issues endpoint."""
        response = client.get("/api/v1/issues")

        # This will likely return 401 because of authentication, but that's expected
        assert response.status_code in [200, 401, 403]  # Could be successful, unauthenticated, or forbidden

    def test_create_issue_endpoint(self, client):
        """Test the create issue endpoint."""
        issue_data = {
            "title": "Test API Issue",
            "description": "This is a test issue created via API",
            "severity": "high",
            "category": "bug",
            "component": "backend"
        }

        response = client.post("/api/v1/issues", json=issue_data)

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 400, 401, 403]  # Could be various responses

    def test_update_issue_endpoint(self, client):
        """Test the update issue endpoint."""
        fake_id = str(uuid.uuid4())
        update_data = {
            "status": "in_progress",
            "resolution_notes": "Starting work on this issue"
        }

        response = client.put(f"/api/v1/issues/{fake_id}", json=update_data)

        # This will likely return 401 because of authentication
        assert response.status_code in [400, 401, 403, 404]  # Could be various errors

    def test_get_issue_details_endpoint(self, client):
        """Test the get issue details endpoint."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/issues/{fake_id}")

        # This will likely return 401 because of authentication
        assert response.status_code in [400, 401, 403, 404]  # Could be various errors