"""
Issue service for the verification system.
This module provides business logic for issue tracking and management.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

from ..models.issue_tracker import IssueTracker, IssueSeverity, IssueStatus, IssueCategory
from ..models.user import User
from ..database.database import get_db
from ..utils.logging import get_logger


class IssueServiceError(Exception):
    """
    Custom exception for issue service-related errors
    """
    pass


class IssueService:
    """
    Service class for handling issue tracking logic
    """
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def get_all_issues(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        component: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[IssueTracker]:
        """
        Retrieve all issues with optional filters.

        Args:
            status: Filter by status
            severity: Filter by severity
            category: Filter by category
            component: Filter by component
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[IssueTracker]: List of issues matching the filters
        """
        try:
            query = self.db.query(IssueTracker)

            if status:
                query = query.filter(IssueTracker.status == IssueStatus(status.lower()))

            if severity:
                query = query.filter(IssueTracker.severity == IssueSeverity(severity.lower()))

            if category:
                query = query.filter(IssueTracker.category == IssueCategory(category.lower()))

            if component:
                query = query.filter(IssueTracker.component.like(f"%{component}%"))

            issues = query.order_by(IssueTracker.created_at.desc()).offset(skip).limit(limit).all()

            self.logger.info(f"Retrieved {len(issues)} issues with filters: status={status}, severity={severity}, category={category}, component={component}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues: {str(e)}")

    def get_issue_by_id(self, issue_id: uuid.UUID) -> Optional[IssueTracker]:
        """
        Retrieve a specific issue by ID.

        Args:
            issue_id: ID of the issue to retrieve

        Returns:
            IssueTracker: The issue if found, None otherwise
        """
        try:
            issue = self.db.query(IssueTracker).filter(IssueTracker.id == issue_id).first()

            if issue:
                self.logger.info(f"Retrieved issue {issue_id}")
            else:
                self.logger.info(f"Issue {issue_id} not found")

            return issue
        except Exception as e:
            self.logger.error(f"Error retrieving issue {issue_id}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issue: {str(e)}")

    def create_issue(
        self,
        title: str,
        description: str,
        severity: IssueSeverity,
        category: IssueCategory,
        component: str,
        reported_by: str = None,
        assigned_to: str = None
    ) -> IssueTracker:
        """
        Create a new issue.

        Args:
            title: Title of the issue
            description: Description of the issue
            severity: Severity level of the issue
            category: Category of the issue
            component: Component affected by the issue
            reported_by: User who reported the issue
            assigned_to: User to whom the issue is assigned

        Returns:
            IssueTracker: The created issue
        """
        try:
            # Create the issue
            new_issue = IssueTracker(
                title=title[:200],  # Limit title length
                description=description,
                severity=severity,
                status=IssueStatus.NEW,
                category=category,
                component=component[:100],  # Limit component length
                reported_by=reported_by,
                assigned_to=assigned_to
            )

            self.db.add(new_issue)
            self.db.commit()
            self.db.refresh(new_issue)

            self.logger.info(f"Created new issue {new_issue.id}")
            return new_issue
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating issue: {str(e)}")
            raise IssueServiceError(f"Failed to create issue: {str(e)}")

    def update_issue(
        self,
        issue_id: uuid.UUID,
        status: Optional[IssueStatus] = None,
        resolution_notes: Optional[str] = None,
        assigned_to: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        severity: Optional[IssueSeverity] = None,
        category: Optional[IssueCategory] = None,
        component: Optional[str] = None
    ) -> IssueTracker:
        """
        Update an existing issue.

        Args:
            issue_id: ID of the issue to update
            status: New status for the issue
            resolution_notes: Resolution notes
            assigned_to: New assignee
            title: New title
            description: New description
            severity: New severity
            category: New category
            component: New component

        Returns:
            IssueTracker: The updated issue
        """
        try:
            # Get the issue
            issue = self.db.query(IssueTracker).filter(IssueTracker.id == issue_id).first()
            if not issue:
                raise IssueServiceError(f"Issue with ID {issue_id} not found")

            # Store old status for transition handling
            old_status = issue.status

            # Update fields if provided
            if title is not None:
                issue.title = title[:200]
            if description is not None:
                issue.description = description
            if severity is not None:
                issue.severity = severity
            if category is not None:
                issue.category = category
            if component is not None:
                issue.component = component[:100]
            if status is not None:
                issue.status = status

                # Handle status transitions
                if status in [IssueStatus.RESOLVED, IssueStatus.VERIFIED, IssueStatus.CLOSED] and not issue.resolved_at:
                    issue.resolved_at = datetime.utcnow()

                # Handle reopening
                if old_status in [IssueStatus.RESOLVED, IssueStatus.VERIFIED, IssueStatus.CLOSED] and \
                   status in [IssueStatus.NEW, IssueStatus.IN_PROGRESS]:
                    issue.is_reopened = True
                    issue.resolved_at = None  # Reset resolved time

            if resolution_notes is not None:
                issue.resolution_notes = resolution_notes
            if assigned_to is not None:
                issue.assigned_to = assigned_to[:100]

            # Update timestamp
            issue.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(issue)

            self.logger.info(f"Updated issue {issue_id}")
            return issue
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating issue {issue_id}: {str(e)}")
            raise IssueServiceError(f"Failed to update issue: {str(e)}")

    def delete_issue(self, issue_id: uuid.UUID) -> bool:
        """
        Delete an issue (soft delete by marking as closed).

        Args:
            issue_id: ID of the issue to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the issue
            issue = self.db.query(IssueTracker).filter(IssueTracker.id == issue_id).first()
            if not issue:
                raise IssueServiceError(f"Issue with ID {issue_id} not found")

            # In a real implementation, you might want to implement soft delete
            # For now, we'll just mark as closed and add deletion note
            issue.status = IssueStatus.CLOSED
            issue.resolution_notes = f"Issue deleted at {datetime.utcnow().isoformat()}"
            issue.updated_at = datetime.utcnow()

            self.db.commit()

            self.logger.info(f"Deleted issue {issue_id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting issue {issue_id}: {str(e)}")
            raise IssueServiceError(f"Failed to delete issue: {str(e)}")

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[IssueTracker]:
        """
        Get all issues with a specific severity.

        Args:
            severity: The severity to filter by

        Returns:
            List[IssueTracker]: List of issues with the specified severity
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.severity == severity)\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues with severity {severity.value}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues by severity {severity.value}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues by severity: {str(e)}")

    def get_issues_by_status(self, status: IssueStatus) -> List[IssueTracker]:
        """
        Get all issues with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List[IssueTracker]: List of issues with the specified status
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.status == status)\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues with status {status.value}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues by status {status.value}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues by status: {str(e)}")

    def get_issues_by_category(self, category: IssueCategory) -> List[IssueTracker]:
        """
        Get all issues with a specific category.

        Args:
            category: The category to filter by

        Returns:
            List[IssueTracker]: List of issues with the specified category
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.category == category)\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues with category {category.value}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues by category {category.value}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues by category: {str(e)}")

    def get_issues_by_component(self, component: str) -> List[IssueTracker]:
        """
        Get all issues affecting a specific component.

        Args:
            component: The component to filter by

        Returns:
            List[IssueTracker]: List of issues affecting the specified component
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.component.like(f"%{component}%"))\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues affecting component {component}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues by component {component}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues by component: {str(e)}")

    def get_open_issues_count(self) -> int:
        """
        Get the count of open issues (not closed or duplicate).

        Returns:
            int: Count of open issues
        """
        try:
            open_statuses = [IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED, IssueStatus.VERIFIED]
            count = self.db.query(IssueTracker)\
                .filter(IssueTracker.status.in_(open_statuses)).count()

            self.logger.info(f"Retrieved count of open issues: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Error retrieving open issues count: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve open issues count: {str(e)}")

    def get_urgent_issues(self, max_age_days: int = 30) -> List[IssueTracker]:
        """
        Get urgent issues (critical/high severity that are open and older than max_age_days).

        Args:
            max_age_days: Maximum age in days for issues to be considered urgent

        Returns:
            List[IssueTracker]: List of urgent issues
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

            urgent_severities = [IssueSeverity.CRITICAL, IssueSeverity.HIGH]
            open_statuses = [IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED, IssueStatus.VERIFIED]

            issues = self.db.query(IssueTracker)\
                .filter(
                    IssueTracker.severity.in_(urgent_severities),
                    IssueTracker.status.in_(open_statuses),
                    IssueTracker.created_at < cutoff_date
                )\
                .order_by(IssueTracker.created_at.asc()).all()

            self.logger.info(f"Retrieved {len(issues)} urgent issues (older than {max_age_days} days)")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving urgent issues: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve urgent issues: {str(e)}")

    def get_issues_assigned_to(self, user_id: str) -> List[IssueTracker]:
        """
        Get all issues assigned to a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[IssueTracker]: List of issues assigned to the user
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.assigned_to == user_id)\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues assigned to user {user_id}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues assigned to user {user_id}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues assigned to user: {str(e)}")

    def get_issues_reported_by(self, user_id: str) -> List[IssueTracker]:
        """
        Get all issues reported by a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[IssueTracker]: List of issues reported by the user
        """
        try:
            issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.reported_by == user_id)\
                .order_by(IssueTracker.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(issues)} issues reported by user {user_id}")
            return issues
        except Exception as e:
            self.logger.error(f"Error retrieving issues reported by user {user_id}: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issues reported by user: {str(e)}")

    def get_issue_statistics(self) -> dict:
        """
        Get statistics about issues in the system.

        Returns:
            dict: Statistics about issues
        """
        try:
            # Count by severity
            severity_counts = {}
            for severity in IssueSeverity:
                count = self.db.query(IssueTracker)\
                    .filter(IssueTracker.severity == severity).count()
                severity_counts[severity.value] = count

            # Count by status
            status_counts = {}
            for status in IssueStatus:
                count = self.db.query(IssueTracker)\
                    .filter(IssueTracker.status == status).count()
                status_counts[status.value] = count

            # Count by category
            category_counts = {}
            for category in IssueCategory:
                count = self.db.query(IssueTracker)\
                    .filter(IssueTracker.category == category).count()
                category_counts[category.value] = count

            # Count total issues
            total_issues = sum(severity_counts.values())

            # Count open issues
            open_statuses = [IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED, IssueStatus.VERIFIED]
            open_issues = self.db.query(IssueTracker)\
                .filter(IssueTracker.status.in_(open_statuses)).count()

            stats = {
                "total_issues": total_issues,
                "open_issues": open_issues,
                "closed_issues": total_issues - open_issues,
                "severity_distribution": severity_counts,
                "status_distribution": status_counts,
                "category_distribution": category_counts,
                "average_resolution_time_hours": self._calculate_avg_resolution_time()
            }

            self.logger.info("Retrieved issue statistics")
            return stats
        except Exception as e:
            self.logger.error(f"Error retrieving issue statistics: {str(e)}")
            raise IssueServiceError(f"Failed to retrieve issue statistics: {str(e)}")

    def _calculate_avg_resolution_time(self) -> float:
        """
        Calculate the average resolution time for resolved issues.

        Returns:
            float: Average resolution time in hours
        """
        try:
            from sqlalchemy import func

            # Calculate average difference between created_at and resolved_at for resolved issues
            avg_duration = self.db.query(
                func.avg(func.extract('epoch', IssueTracker.resolved_at - IssueTracker.created_at))
            ).filter(
                IssueTracker.resolved_at.isnot(None)
            ).scalar()

            if avg_duration is not None:
                return round(avg_duration / 3600, 2)  # Convert seconds to hours
            else:
                return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating average resolution time: {str(e)}")
            return 0.0

    def close_stale_issues(self, days_threshold: int = 90) -> int:
        """
        Close issues that have been open for more than the specified number of days.

        Args:
            days_threshold: Number of days after which to close issues

        Returns:
            int: Number of issues closed
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

            # Find issues that are open and older than the threshold
            open_statuses = [IssueStatus.NEW, IssueStatus.IN_PROGRESS]
            stale_issues = self.db.query(IssueTracker)\
                .filter(
                    IssueTracker.status.in_(open_statuses),
                    IssueTracker.created_at < cutoff_date
                ).all()

            closed_count = 0
            for issue in stale_issues:
                issue.status = IssueStatus.CLOSED
                issue.resolution_notes = f"Auto-closed due to inactivity (older than {days_threshold} days)"
                issue.updated_at = datetime.utcnow()
                closed_count += 1

            self.db.commit()

            self.logger.info(f"Auto-closed {closed_count} stale issues (older than {days_threshold} days)")
            return closed_count
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error closing stale issues: {str(e)}")
            raise IssueServiceError(f"Failed to close stale issues: {str(e)}")