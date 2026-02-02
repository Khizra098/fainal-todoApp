"""
Unit tests for the VerificationReport model.

This module contains unit tests for the VerificationReport model including validation,
creation, and property access.
"""

import pytest
from datetime import datetime
from src.models.verification_report import VerificationReport, VerificationStatus


class TestVerificationReportModel:
    """Unit tests for the VerificationReport model."""

    def test_verification_report_creation(self, test_db, sample_feature):
        """Test creating a verification report with valid data."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.PENDING,
            details="Initial verification pending",
            expected_behavior="Feature should work as specified",
            actual_behavior="Feature is working as expected"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.id is not None
        assert report.feature_id == sample_feature.id
        assert report.status == VerificationStatus.PENDING
        assert report.details == "Initial verification pending"
        assert report.expected_behavior == "Feature should work as specified"
        assert report.actual_behavior == "Feature is working as expected"
        assert report.created_at is not None

    def test_verification_report_with_issues(self, test_db, sample_feature):
        """Test creating a verification report with issues found."""
        issues = ["Issue 1", "Issue 2", "Critical bug"]
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.FAILED,
            details="Verification failed due to issues",
            expected_behavior="Feature should work",
            actual_behavior="Feature has problems",
            issues_found=issues
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.issues_found == issues
        assert report.status == VerificationStatus.FAILED

    def test_verification_report_default_values(self, test_db, sample_feature):
        """Test default values for optional fields."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.IN_PROGRESS
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.status == VerificationStatus.IN_PROGRESS
        assert report.issues_found == []  # Default to empty list
        assert report.details == ""  # Default to empty string

    def test_verification_report_status_enum(self, test_db, sample_feature):
        """Test that status enum values are properly handled."""
        for status in VerificationStatus:
            report = VerificationReport(
                feature_id=sample_feature.id,
                status=status,
                details=f"Test with status {status.value}"
            )

            test_db.add(report)
            test_db.commit()
            test_db.refresh(report)

            assert report.status == status

    def test_verification_report_completed_at_field(self, test_db, sample_feature):
        """Test the completed_at field behavior."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.IN_PROGRESS,
            details="In progress"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        # Initially completed_at should be None
        assert report.completed_at is None

        # Update status to completed
        report.status = VerificationStatus.VERIFIED
        report.completed_at = datetime.utcnow()
        test_db.commit()
        test_db.refresh(report)

        assert report.completed_at is not None

    def test_verification_report_to_dict(self, test_db, sample_feature):
        """Test the to_dict method of the VerificationReport model."""
        issues = ["Some issue"]
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.VERIFIED,
            details="Verification completed",
            expected_behavior="Should work correctly",
            actual_behavior="Works correctly",
            issues_found=issues
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        report_dict = report.to_dict()

        assert "id" in report_dict
        assert report_dict["feature_id"] == sample_feature.id
        assert report_dict["status"] == VerificationStatus.VERIFIED.value
        assert report_dict["details"] == "Verification completed"
        assert report_dict["expected_behavior"] == "Should work correctly"
        assert report_dict["actual_behavior"] == "Works correctly"
        assert report_dict["issues_found"] == issues
        assert "created_at" in report_dict