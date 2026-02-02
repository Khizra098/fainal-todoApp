"""
Unit tests for the Feature model.

This module contains unit tests for the Feature model including validation,
creation, and property access.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.models.feature import Feature


class TestFeatureModel:
    """Unit tests for the Feature model."""

    def test_feature_creation(self, test_db):
        """Test creating a feature with valid data."""
        feature = Feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert feature.id is not None
        assert feature.name == "Test Feature"
        assert feature.description == "A test feature"
        assert feature.specification_reference == "SPEC-001"
        assert feature.created_at is not None
        assert feature.updated_at is not None

    def test_feature_required_fields(self, test_db):
        """Test that required fields are validated."""
        feature = Feature(name="Test Feature")

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Name should be set
        assert feature.name == "Test Feature"
        # Description and specification_reference should have defaults
        assert feature.description is not None
        assert feature.specification_reference is not None

    def test_feature_optional_fields(self, test_db):
        """Test optional fields in Feature model."""
        feature = Feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001",
            tags=["tag1", "tag2"],
            priority="high",
            estimated_complexity=5
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert feature.tags == ["tag1", "tag2"]
        assert feature.priority == "high"
        assert feature.estimated_complexity == 5

    def test_feature_str_representation(self, test_db):
        """Test the string representation of the Feature model."""
        feature = Feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert str(feature) == f"Feature(id={feature.id}, name='Test Feature')"

    def test_feature_to_dict(self, test_db):
        """Test the to_dict method of the Feature model."""
        feature = Feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        feature_dict = feature.to_dict()

        assert "id" in feature_dict
        assert feature_dict["name"] == "Test Feature"
        assert feature_dict["description"] == "A test feature"
        assert feature_dict["specification_reference"] == "SPEC-001"
        assert "created_at" in feature_dict
        assert "updated_at" in feature_dict

    def test_feature_updated_at_changes(self, test_db):
        """Test that updated_at changes when the feature is modified."""
        feature = Feature(
            name="Test Feature",
            description="A test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        original_updated_at = feature.updated_at

        # Modify the feature
        feature.description = "Updated description"
        test_db.commit()
        test_db.refresh(feature)

        # updated_at should be different
        assert feature.updated_at > original_updated_at
        assert feature.description == "Updated description"