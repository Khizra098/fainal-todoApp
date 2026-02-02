"""
Unit tests for the FeatureService.

This module contains unit tests for the FeatureService class including
CRUD operations and verification functionality.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.services.feature_service import FeatureService
from src.models.feature import Feature
from src.models.verification_report import VerificationReport, VerificationStatus


class TestFeatureService:
    """Unit tests for the FeatureService."""

    def test_create_feature(self, test_db):
        """Test creating a feature through the service."""
        service = FeatureService(test_db)

        feature = service.create_feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        assert feature.id is not None
        assert feature.name == "Test Feature"
        assert feature.description == "A test feature"
        assert feature.specification_reference == "SPEC-001"

    def test_get_feature_by_id(self, test_db, sample_feature):
        """Test retrieving a feature by ID."""
        service = FeatureService(test_db)

        retrieved_feature = service.get_feature_by_id(sample_feature.id)

        assert retrieved_feature is not None
        assert retrieved_feature.id == sample_feature.id
        assert retrieved_feature.name == sample_feature.name

    def test_get_feature_by_name(self, test_db, sample_feature):
        """Test retrieving a feature by name."""
        service = FeatureService(test_db)

        retrieved_feature = service.get_feature_by_name(sample_feature.name)

        assert retrieved_feature is not None
        assert retrieved_feature.id == sample_feature.id
        assert retrieved_feature.name == sample_feature.name

    def test_get_all_features(self, test_db):
        """Test retrieving all features."""
        service = FeatureService(test_db)

        # Create multiple features
        feature1 = service.create_feature(
            name="Feature 1",
            description="First feature",
            specification_reference="SPEC-001"
        )
        feature2 = service.create_feature(
            name="Feature 2",
            description="Second feature",
            specification_reference="SPEC-002"
        )

        features = service.get_all_features()

        assert len(features) >= 2
        feature_names = [f.name for f in features]
        assert feature1.name in feature_names
        assert feature2.name in feature_names

    def test_update_feature(self, test_db, sample_feature):
        """Test updating a feature."""
        service = FeatureService(test_db)

        updated_feature = service.update_feature(
            feature_id=sample_feature.id,
            name="Updated Feature",
            description="Updated description"
        )

        assert updated_feature is not None
        assert updated_feature.name == "Updated Feature"
        assert updated_feature.description == "Updated description"

    def test_update_feature_partial(self, test_db, sample_feature):
        """Test partially updating a feature."""
        original_name = sample_feature.name
        service = FeatureService(test_db)

        updated_feature = service.update_feature(
            feature_id=sample_feature.id,
            description="Only updating description"
        )

        assert updated_feature is not None
        assert updated_feature.name == original_name  # Should remain unchanged
        assert updated_feature.description == "Only updating description"

    def test_delete_feature(self, test_db, sample_feature):
        """Test deleting a feature."""
        service = FeatureService(test_db)

        result = service.delete_feature(sample_feature.id)

        assert result is True

        # Verify the feature is no longer retrievable
        deleted_feature = service.get_feature_by_id(sample_feature.id)
        assert deleted_feature is None

    def test_delete_nonexistent_feature(self, test_db):
        """Test attempting to delete a non-existent feature."""
        service = FeatureService(test_db)

        result = service.delete_feature(99999)

        assert result is False

    def test_initiate_verification(self, test_db, sample_feature):
        """Test initiating a verification for a feature."""
        service = FeatureService(test_db)

        verification_report = service.initiate_verification(sample_feature.id)

        assert verification_report is not None
        assert verification_report.feature_id == sample_feature.id
        assert verification_report.status == VerificationStatus.IN_PROGRESS
        assert verification_report.expected_behavior is not None
        assert "Test Feature" in verification_report.expected_behavior

    def test_complete_verification_success(self, test_db, sample_feature):
        """Test completing a verification with success status."""
        service = FeatureService(test_db)

        # First initiate verification
        init_report = service.initiate_verification(sample_feature.id)

        # Then complete it
        completed_report = service.complete_verification(
            feature_id=sample_feature.id,
            status=VerificationStatus.VERIFIED,
            details="Verification completed successfully",
            actual_behavior="Feature behaves as expected",
            issues_found=["Minor UI inconsistency"]
        )

        assert completed_report is not None
        assert completed_report.status == VerificationStatus.VERIFIED
        assert completed_report.details == "Verification completed successfully"
        assert completed_report.actual_behavior == "Feature behaves as expected"
        assert completed_report.issues_found == ["Minor UI inconsistency"]
        assert completed_report.completed_at is not None

    def test_complete_verification_failure(self, test_db, sample_feature):
        """Test completing a verification with failure status."""
        service = FeatureService(test_db)

        completed_report = service.complete_verification(
            feature_id=sample_feature.id,
            status=VerificationStatus.FAILED,
            details="Verification failed due to critical issues",
            actual_behavior="Feature does not match specification",
            issues_found=["Missing functionality", "Incorrect behavior"]
        )

        assert completed_report is not None
        assert completed_report.status == VerificationStatus.FAILED
        assert "critical issues" in completed_report.details
        assert "does not match specification" in completed_report.actual_behavior
        assert len(completed_report.issues_found) == 2

    def test_get_verification_report_for_feature(self, test_db, sample_feature):
        """Test getting the latest verification report for a feature."""
        service = FeatureService(test_db)

        # Initiate and complete a verification
        service.initiate_verification(sample_feature.id)
        completed_report = service.complete_verification(
            feature_id=sample_feature.id,
            status=VerificationStatus.VERIFIED,
            details="Verification completed"
        )

        report = service.get_verification_report_for_feature(sample_feature.id)

        assert report is not None
        assert report.id == completed_report.id
        assert report.status == VerificationStatus.VERIFIED

    def test_get_all_verification_reports(self, test_db, sample_feature):
        """Test getting all verification reports for a feature."""
        service = FeatureService(test_db)

        # Create multiple verification reports
        service.initiate_verification(sample_feature.id)
        service.complete_verification(
            feature_id=sample_feature.id,
            status=VerificationStatus.VERIFIED,
            details="First verification"
        )

        service.initiate_verification(sample_feature.id)
        service.complete_verification(
            feature_id=sample_feature.id,
            status=VerificationStatus.FAILED,
            details="Second verification"
        )

        reports = service.get_all_verification_reports(sample_feature.id)

        assert len(reports) >= 2
        # Reports should be ordered by creation date (newest first)
        assert reports[0].status == VerificationStatus.FAILED
        assert reports[1].status == VerificationStatus.VERIFIED

    def test_get_verification_summary(self, test_db):
        """Test getting a verification summary."""
        service = FeatureService(test_db)

        # Create a feature
        feature = service.create_feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        # Initiate and complete a verification
        service.initiate_verification(feature.id)
        service.complete_verification(
            feature_id=feature.id,
            status=VerificationStatus.VERIFIED,
            details="Verification completed"
        )

        summary = service.get_verification_summary()

        assert "total_features" in summary
        assert "verification_counts" in summary
        assert "verification_percentage" in summary
        assert "last_updated" in summary

        assert summary["total_features"] >= 1
        assert summary["verification_percentage"] >= 0
        assert isinstance(summary["verification_counts"], dict)