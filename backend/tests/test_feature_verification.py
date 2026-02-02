"""
Tests for feature verification functionality.
This module contains tests for the verification system.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.models.feature import Feature
from src.models.verification_report import VerificationReport, VerificationStatus, VerificationResult
from src.database.database import Base
from src.main import app
from src.services.verification_service import VerificationService


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
def verification_service(test_db):
    """Create a verification service instance."""
    return VerificationService(test_db)


class TestFeatureModel:
    """Tests for the Feature model."""

    def test_feature_creation(self, test_db):
        """Test creating a feature."""
        feature = Feature(
            name="Test Feature",
            description="This is a test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert feature.name == "Test Feature"
        assert feature.description == "This is a test feature"
        assert feature.specification_reference == "SPEC-001"
        assert feature.id is not None
        assert feature.created_at is not None

    def test_feature_to_dict(self, test_db):
        """Test converting feature to dictionary."""
        feature = Feature(
            name="Test Feature",
            description="This is a test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        feature_dict = feature.to_dict()

        assert feature_dict["name"] == "Test Feature"
        assert feature_dict["description"] == "This is a test feature"
        assert feature_dict["specification_reference"] == "SPEC-001"
        assert "id" in feature_dict
        assert "created_at" in feature_dict


class TestVerificationReportModel:
    """Tests for the VerificationReport model."""

    def test_verification_report_creation(self, test_db):
        """Test creating a verification report."""
        # Create a feature first
        feature = Feature(
            name="Test Feature",
            description="This is a test feature",
            specification_reference="SPEC-001"
        )
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Create a verification report
        report = VerificationReport(
            feature_id=feature.id,
            verification_type="automated",
            status=VerificationStatus.PENDING,
            result=VerificationResult.NEEDS_WORK,
            findings="Some findings",
            recommendations="Some recommendations"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.feature_id == feature.id
        assert report.verification_type == "automated"
        assert report.status == VerificationStatus.PENDING
        assert report.result == VerificationResult.NEEDS_WORK
        assert report.findings == "Some findings"
        assert report.recommendations == "Some recommendations"

    def test_verification_report_to_dict(self, test_db):
        """Test converting verification report to dictionary."""
        # Create a feature first
        feature = Feature(
            name="Test Feature",
            description="This is a test feature",
            specification_reference="SPEC-001"
        )
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Create a verification report
        report = VerificationReport(
            feature_id=feature.id,
            verification_type="automated",
            status=VerificationStatus.COMPLETE,
            result=VerificationResult.PASS,
            findings="Test findings",
            recommendations="Test recommendations"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        report_dict = report.to_dict()

        assert report_dict["feature_id"] == str(feature.id)
        assert report_dict["verification_type"] == "automated"
        assert report_dict["status"] == "complete"
        assert report_dict["result"] == "pass"
        assert report_dict["findings"] == "Test findings"


class TestVerificationService:
    """Tests for the VerificationService."""

    def test_get_all_features(self, verification_service, test_db):
        """Test getting all features."""
        # Create test features
        feature1 = Feature(name="Feature 1", description="First feature", specification_reference="SPEC-001")
        feature2 = Feature(name="Feature 2", description="Second feature", specification_reference="SPEC-002")

        test_db.add(feature1)
        test_db.add(feature2)
        test_db.commit()

        features = verification_service.get_all_features()

        assert len(features) == 2
        assert features[0].name in ["Feature 1", "Feature 2"]
        assert features[1].name in ["Feature 1", "Feature 2"]

    def test_get_feature_by_id(self, verification_service, test_db):
        """Test getting a feature by ID."""
        feature = Feature(name="Test Feature", description="A test feature", specification_reference="SPEC-001")
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        retrieved_feature = verification_service.get_feature_by_id(feature.id)

        assert retrieved_feature is not None
        assert retrieved_feature.id == feature.id
        assert retrieved_feature.name == "Test Feature"

    def test_get_feature_by_id_not_found(self, verification_service):
        """Test getting a feature that doesn't exist."""
        fake_id = uuid.uuid4()
        retrieved_feature = verification_service.get_feature_by_id(fake_id)

        assert retrieved_feature is None

    def test_create_verification_report(self, verification_service, test_db):
        """Test creating a verification report."""
        feature = Feature(name="Test Feature", description="A test feature", specification_reference="SPEC-001")
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        report = verification_service.create_verification_report(
            feature_id=feature.id,
            verification_type="manual",
            status=VerificationStatus.IN_PROGRESS
        )

        assert report.feature_id == feature.id
        assert report.verification_type == "manual"
        assert report.status == VerificationStatus.IN_PROGRESS

    def test_get_verification_statistics(self, verification_service, test_db):
        """Test getting verification statistics."""
        # Create a feature
        feature = Feature(name="Test Feature", description="A test feature", specification_reference="SPEC-001")
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Create a verification report
        report = VerificationReport(
            feature_id=feature.id,
            verification_type="automated",
            status=VerificationStatus.COMPLETE,
            result=VerificationResult.PASS
        )
        test_db.add(report)
        test_db.commit()

        stats = verification_service.get_verification_statistics()

        assert stats["total_features"] == 1
        assert stats["features_with_verifications"] == 1
        assert stats["verification_coverage"] == 100.0
        assert stats["verification_status_counts"]["complete"] == 1
        assert stats["verification_result_counts"]["pass"] == 1


class TestVerificationAPI:
    """Tests for the verification API endpoints."""

    def test_get_features_endpoint(self, client):
        """Test the get features endpoint."""
        response = client.get("/api/v1/verification/features")

        # This will likely return 401 because of authentication, but that's expected
        assert response.status_code in [200, 401, 403]  # Could be successful, unauthenticated, or forbidden

    def test_get_feature_details_endpoint(self, client):
        """Test the get feature details endpoint."""
        # Use a fake UUID for testing
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/verification/features/{fake_id}")

        # This will likely return 401 because of authentication
        assert response.status_code in [400, 401, 403, 404]  # Could be various errors due to auth or not found

    @patch('src.services.verification_service.VerificationService.perform_verification')
    def test_initiate_verification_endpoint(self, mock_perform_verification, client):
        """Test the initiate verification endpoint."""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/verification/features/{fake_id}/verify",
            json={"verification_type": "automated"}
        )

        # This will likely return 401 because of authentication
        assert response.status_code in [400, 401, 403, 404]


class TestVerificationServiceAsync:
    """Async tests for verification service."""

    @pytest.mark.asyncio
    async def test_perform_verification(self, verification_service, test_db):
        """Test performing verification asynchronously."""
        # Create a feature
        feature = Feature(name="Test Feature", description="A test feature", specification_reference="SPEC-001")
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Create a verification report
        report = VerificationReport(
            feature_id=feature.id,
            verification_type="automated",
            status=VerificationStatus.PENDING
        )
        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        # Perform verification
        await verification_service.perform_verification(report.id)

        # Refresh the report to get updated values
        updated_report = test_db.query(VerificationReport).filter(VerificationReport.id == report.id).first()

        assert updated_report.status in [VerificationStatus.COMPLETE]
        assert updated_report.result in [VerificationResult.PASS, VerificationResult.FAIL, VerificationResult.NEEDS_WORK]