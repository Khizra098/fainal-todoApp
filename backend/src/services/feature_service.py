"""
Feature Service Module

This module provides the FeatureService class which handles business logic for feature management,
including CRUD operations for features and their verification status.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..models.feature import Feature
from ..models.verification_report import VerificationReport, VerificationStatus


class FeatureService:
    """
    Service class for managing features and their verification status.
    """

    def __init__(self, db: Session):
        """
        Initialize the FeatureService with a database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def create_feature(self, name: str, description: str, specification_reference: str) -> Feature:
        """
        Create a new feature in the database.

        Args:
            name (str): Name of the feature
            description (str): Description of the feature
            specification_reference (str): Reference to the original specification

        Returns:
            Feature: The created feature object

        Raises:
            IntegrityError: If a feature with the same name already exists
        """
        feature = Feature(
            name=name,
            description=description,
            specification_reference=specification_reference
        )

        try:
            self.db.add(feature)
            self.db.commit()
            self.db.refresh(feature)
            return feature
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def get_feature_by_id(self, feature_id: int) -> Optional[Feature]:
        """
        Retrieve a feature by its ID.

        Args:
            feature_id (int): ID of the feature to retrieve

        Returns:
            Optional[Feature]: The feature object if found, None otherwise
        """
        return self.db.query(Feature).filter(Feature.id == feature_id).first()

    def get_feature_by_name(self, name: str) -> Optional[Feature]:
        """
        Retrieve a feature by its name.

        Args:
            name (str): Name of the feature to retrieve

        Returns:
            Optional[Feature]: The feature object if found, None otherwise
        """
        return self.db.query(Feature).filter(Feature.name == name).first()

    def get_all_features(self, skip: int = 0, limit: int = 100) -> List[Feature]:
        """
        Retrieve all features with pagination.

        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Feature]: List of feature objects
        """
        return self.db.query(Feature).offset(skip).limit(limit).all()

    def update_feature(self, feature_id: int, name: Optional[str] = None,
                      description: Optional[str] = None,
                      specification_reference: Optional[str] = None) -> Optional[Feature]:
        """
        Update an existing feature.

        Args:
            feature_id (int): ID of the feature to update
            name (Optional[str]): New name for the feature (if provided)
            description (Optional[str]): New description for the feature (if provided)
            specification_reference (Optional[str]): New spec reference for the feature (if provided)

        Returns:
            Optional[Feature]: The updated feature object if successful, None if feature not found
        """
        feature = self.get_feature_by_id(feature_id)
        if not feature:
            return None

        if name is not None:
            feature.name = name
        if description is not None:
            feature.description = description
        if specification_reference is not None:
            feature.specification_reference = specification_reference

        try:
            self.db.commit()
            self.db.refresh(feature)
            return feature
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def delete_feature(self, feature_id: int) -> bool:
        """
        Delete a feature by its ID.

        Args:
            feature_id (int): ID of the feature to delete

        Returns:
            bool: True if deletion was successful, False if feature was not found
        """
        feature = self.get_feature_by_id(feature_id)
        if not feature:
            return False

        self.db.delete(feature)
        self.db.commit()
        return True

    def get_verification_report_for_feature(self, feature_id: int) -> Optional[VerificationReport]:
        """
        Get the latest verification report for a specific feature.

        Args:
            feature_id (int): ID of the feature

        Returns:
            Optional[VerificationReport]: The latest verification report if found, None otherwise
        """
        return (
            self.db.query(VerificationReport)
            .filter(VerificationReport.feature_id == feature_id)
            .order_by(VerificationReport.created_at.desc())
            .first()
        )

    def get_all_verification_reports(self, feature_id: int) -> List[VerificationReport]:
        """
        Get all verification reports for a specific feature.

        Args:
            feature_id (int): ID of the feature

        Returns:
            List[VerificationReport]: List of all verification reports for the feature
        """
        return (
            self.db.query(VerificationReport)
            .filter(VerificationReport.feature_id == feature_id)
            .order_by(VerificationReport.created_at.desc())
            .all()
        )

    def initiate_verification(self, feature_id: int) -> VerificationReport:
        """
        Initiate a new verification process for a feature.

        Args:
            feature_id (int): ID of the feature to verify

        Returns:
            VerificationReport: A new verification report in 'in_progress' status
        """
        feature = self.get_feature_by_id(feature_id)
        if not feature:
            raise ValueError(f"Feature with ID {feature_id} not found")

        verification_report = VerificationReport(
            feature_id=feature_id,
            status=VerificationStatus.IN_PROGRESS,
            details="Verification process initiated",
            expected_behavior=f"Feature '{feature.name}' should behave according to specification: {feature.specification_reference}"
        )

        self.db.add(verification_report)
        self.db.commit()
        self.db.refresh(verification_report)

        return verification_report

    def complete_verification(self, feature_id: int, status: VerificationStatus,
                            details: str = "", actual_behavior: Optional[str] = None,
                            issues_found: Optional[List[str]] = None) -> Optional[VerificationReport]:
        """
        Complete a verification process for a feature.

        Args:
            feature_id (int): ID of the feature to verify
            status (VerificationStatus): Final verification status
            details (str): Additional details about the verification
            actual_behavior (Optional[str]): Actual behavior observed during verification
            issues_found (Optional[List[str]]): List of issues found during verification

        Returns:
            Optional[VerificationReport]: Updated verification report if successful, None if no in-progress report found
        """
        # Get the most recent in-progress verification report
        in_progress_report = (
            self.db.query(VerificationReport)
            .filter(
                VerificationReport.feature_id == feature_id,
                VerificationReport.status == VerificationStatus.IN_PROGRESS
            )
            .order_by(VerificationReport.created_at.desc())
            .first()
        )

        if not in_progress_report:
            # If there's no in-progress report, create a new one
            feature = self.get_feature_by_id(feature_id)
            if not feature:
                raise ValueError(f"Feature with ID {feature_id} not found")

            in_progress_report = VerificationReport(
                feature_id=feature_id,
                status=VerificationStatus.IN_PROGRESS,
                details="Verification process initiated",
                expected_behavior=f"Feature '{feature.name}' should behave according to specification: {feature.specification_reference}"
            )
            self.db.add(in_progress_report)
            self.db.commit()
            self.db.refresh(in_progress_report)

        # Update the report with completion details
        in_progress_report.status = status
        in_progress_report.details = details
        in_progress_report.actual_behavior = actual_behavior
        in_progress_report.issues_found = issues_found or []
        in_progress_report.completed_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(in_progress_report)
            return in_progress_report
        except Exception as e:
            self.db.rollback()
            raise e

    def get_verification_summary(self) -> dict:
        """
        Get a summary of all feature verifications.

        Returns:
            dict: Summary containing counts of features by verification status
        """
        # Count total features
        total_features = self.db.query(Feature).count()

        # Get the latest verification report for each feature
        latest_reports_subquery = (
            self.db.query(
                VerificationReport.feature_id,
                VerificationReport.status,
                VerificationReport.created_at
            )
            .distinct(VerificationReport.feature_id)
            .order_by(VerificationReport.feature_id, VerificationReport.created_at.desc())
            .subquery()
        )

        # Count verification statuses
        verification_counts = {}
        for status in VerificationStatus:
            count = (
                self.db.query(latest_reports_subquery.c.status)
                .filter(latest_reports_subquery.c.status == status.value)
                .count()
            )
            verification_counts[status.value] = count

        # Calculate percentage of verified features
        verified_count = verification_counts.get(VerificationStatus.VERIFIED.value, 0)
        verification_percentage = (verified_count / total_features * 100) if total_features > 0 else 0

        return {
            "total_features": total_features,
            "verification_counts": verification_counts,
            "verification_percentage": round(verification_percentage, 2),
            "last_updated": datetime.utcnow().isoformat()
        }