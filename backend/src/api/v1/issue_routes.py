"""
Issue tracking API endpoints for the verification system.
This module provides endpoints for issue management and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ...database.database import get_db
from ...models.issue_tracker import IssueTracker, IssueSeverity, IssueStatus, IssueCategory
from ...models.user import User
from ...middleware.auth import get_current_user
from ...middleware.error_handler import BusinessLogicError, NotFoundError
from ...services.issue_service import IssueService
from ...utils.logging import get_logger


router = APIRouter(prefix="/issues", tags=["issues"])
logger = get_logger(__name__)


@router.get("", summary="Get Issues")
async def get_issues(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    component: Optional[str] = Query(None, description="Filter by affected component"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve list of issues with filtering options.

    Args:
        status: Filter by status
        severity: Filter by severity
        component: Filter by affected component
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of issues with filtering applied
    """
    try:
        # Build query with filters
        query = db.query(IssueTracker)

        if status:
            try:
                status_enum = IssueStatus(status.lower())
                query = query.filter(IssueTracker.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        if severity:
            try:
                severity_enum = IssueSeverity(severity.lower())
                query = query.filter(IssueTracker.severity == severity_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")

        if component:
            query = query.filter(IssueTracker.component.like(f"%{component}%"))

        # Apply pagination
        issues = query.order_by(IssueTracker.created_at.desc()).offset(skip).limit(limit).all()

        # Convert to dict format
        issues_list = [issue.to_dict() for issue in issues]

        logger.info(f"Retrieved {len(issues_list)} issues for user {current_user.id}")

        return {
            "issues": issues_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving issues: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("", summary="Create Issue")
async def create_issue(
    issue_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Create a new issue.

    Args:
        issue_data: Issue data including title, description, severity, etc.
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Created issue information
    """
    try:
        # Validate required fields
        required_fields = ["title", "description", "component"]
        for field in required_fields:
            if field not in issue_data or not issue_data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Validate severity
        severity = issue_data.get("severity", "medium").lower()
        try:
            severity_enum = IssueSeverity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}. Must be one of: critical, high, medium, low")

        # Validate category
        category = issue_data.get("category", "bug").lower()
        try:
            category_enum = IssueCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}. Must be one of: bug, enhancement, security, performance")

        # Validate component
        component = issue_data.get("component", "").strip()
        if not component:
            raise HTTPException(status_code=400, detail="Component is required")

        # Create new issue
        new_issue = IssueTracker(
            title=issue_data["title"][:200],  # Limit title length
            description=issue_data["description"],
            severity=severity_enum,
            status=IssueStatus.NEW,
            category=category_enum,
            component=component[:100],  # Limit component length
            reported_by=str(current_user.id) if hasattr(current_user, 'id') else "unknown"
        )

        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)

        logger.info(f"Created new issue {new_issue.id} by user {current_user.id}")

        return {
            "issue": new_issue.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating issue: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{issue_id}", summary="Update Issue")
async def update_issue(
    issue_id: str,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Update an existing issue.

    Args:
        issue_id: ID of the issue to update
        update_data: Update data including status, resolution_notes, assigned_to, etc.
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Updated issue information
    """
    try:
        # Validate issue_id format
        try:
            issue_uuid = uuid.UUID(issue_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue ID format")

        # Get the issue
        issue = db.query(IssueTracker).filter(IssueTracker.id == issue_uuid).first()
        if not issue:
            raise NotFoundError("Issue", issue_id)

        # Update fields if provided
        if "status" in update_data and update_data["status"]:
            try:
                status_value = update_data["status"].lower()
                status_enum = IssueStatus(status_value)

                # Handle status transitions
                old_status = issue.status
                issue.status = status_enum

                # Update resolved_at if transitioning to resolved/verified/closed
                if status_enum in [IssueStatus.RESOLVED, IssueStatus.VERIFIED, IssueStatus.CLOSED] and not issue.resolved_at:
                    issue.resolved_at = datetime.utcnow()

                # Handle reopening
                if old_status in [IssueStatus.RESOLVED, IssueStatus.VERIFIED, IssueStatus.CLOSED] and \
                   status_enum in [IssueStatus.NEW, IssueStatus.IN_PROGRESS]:
                    issue.is_reopened = True
                    issue.resolved_at = None  # Reset resolved time

            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {update_data['status']}")

        if "resolution_notes" in update_data:
            issue.resolution_notes = update_data["resolution_notes"]

        if "assigned_to" in update_data:
            issue.assigned_to = update_data["assigned_to"][:100]  # Limit length

        # Update timestamp
        issue.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(issue)

        logger.info(f"Updated issue {issue_id} by user {current_user.id}")

        return {
            "issue": issue.to_dict()
        }

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating issue: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{issue_id}", summary="Get Issue Details")
async def get_issue_details(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get detailed information for a specific issue.

    Args:
        issue_id: ID of the issue to retrieve
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Detailed issue information
    """
    try:
        # Validate issue_id format
        try:
            issue_uuid = uuid.UUID(issue_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue ID format")

        # Get the issue
        issue = db.query(IssueTracker).filter(IssueTracker.id == issue_uuid).first()
        if not issue:
            raise NotFoundError("Issue", issue_id)

        logger.info(f"Retrieved issue {issue_id} by user {current_user.id}")

        return {
            "issue": issue.to_dict()
        }

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving issue details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{issue_id}", summary="Delete Issue")
async def delete_issue(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Delete an issue (soft delete by marking as inactive).

    Args:
        issue_id: ID of the issue to delete
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Deletion confirmation
    """
    try:
        # Validate issue_id format
        try:
            issue_uuid = uuid.UUID(issue_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue ID format")

        # Get the issue
        issue = db.query(IssueTracker).filter(IssueTracker.id == issue_uuid).first()
        if not issue:
            raise NotFoundError("Issue", issue_id)

        # In a real implementation, you might want to implement soft delete
        # For now, we'll just mark as closed and add deletion note
        issue.status = IssueStatus.CLOSED
        issue.resolution_notes = f"Issue deleted by {current_user.id} at {datetime.utcnow().isoformat()}"
        issue.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Deleted issue {issue_id} by user {current_user.id}")

        return {
            "message": "Issue deleted successfully",
            "issue_id": issue_id
        }

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting issue: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")