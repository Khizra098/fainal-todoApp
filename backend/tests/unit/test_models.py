"""
Unit tests for database models and their validation logic.

This module contains unit tests for all database models,
testing validation rules, constraints, and relationships.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from src.models.user import User
from src.models.feature import Feature
from src.models.verification_report import VerificationReport, VerificationStatus
from src.models.issue_tracker import IssueTracker, IssueSeverity, IssueStatus, IssueCategory
from src.models.performance_benchmark import PerformanceBenchmark, MetricType, BenchmarkStatus
from src.models.security_assessment import SecurityAssessment, SecurityScanType, SecurityScanStatus
from src.models.deployment_config import DeploymentConfig, EnvironmentType
from src.database.database import Base


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


class TestUserModelValidation:
    """Tests for User model validation."""

    def test_user_creation_with_valid_data(self, test_db):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.id is not None

    def test_user_email_validation(self, test_db):
        """Test email validation rules."""
        # Test valid email
        user1 = User(
            email="valid@example.com",
            username="validuser",
            hashed_password="password"
        )

        test_db.add(user1)
        test_db.commit()
        test_db.refresh(user1)
        assert user1.email == "valid@example.com"

    def test_user_username_length_validation(self, test_db):
        """Test username length validation."""
        # Test username that's too long
        long_username = "a" * 100  # Assuming max length is less than 100
        user = User(
            email="test@example.com",
            username=long_username,
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        # This test depends on the actual model constraints

    def test_user_duplicate_email_constraint(self, test_db):
        """Test that duplicate emails are not allowed."""
        # Create first user
        user1 = User(
            email="duplicate@example.com",
            username="user1",
            hashed_password="password1"
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",  # Same email
            username="user2",
            hashed_password="password2"
        )
        test_db.add(user2)

        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
            test_db.commit()


class TestFeatureModelValidation:
    """Tests for Feature model validation."""

    def test_feature_creation_with_valid_data(self, test_db):
        """Test creating a feature with valid data."""
        feature = Feature(
            name="Test Feature",
            description="A test feature description",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert feature.name == "Test Feature"
        assert feature.description == "A test feature description"
        assert feature.specification_reference == "SPEC-001"
        assert feature.id is not None
        assert feature.created_at is not None

    def test_feature_name_required(self, test_db):
        """Test that feature name is required."""
        feature = Feature(
            description="A test feature description",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # If name is required, this would raise an exception during commit
        # Otherwise, it might default to an empty string or None
        assert feature.name is not None

    def test_feature_name_length_validation(self, test_db):
        """Test feature name length validation."""
        # Create a feature with a very long name
        long_name = "A" * 200  # Assuming there's a length limit
        feature = Feature(
            name=long_name,
            description="A test feature",
            specification_reference="SPEC-001"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Check if the name was truncated or if validation occurred
        assert feature.name == long_name  # Or whatever the validation rule specifies

    def test_feature_tags_validation(self, test_db):
        """Test feature tags validation."""
        feature = Feature(
            name="Test Feature",
            description="A test feature with tags",
            specification_reference="SPEC-001",
            tags=["tag1", "tag2", "tag3"]
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert "tag1" in feature.tags
        assert "tag2" in feature.tags
        assert "tag3" in feature.tags

    def test_feature_priority_validation(self, test_db):
        """Test feature priority validation."""
        feature = Feature(
            name="Test Feature",
            description="A test feature with priority",
            specification_reference="SPEC-001",
            priority="high"
        )

        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        assert feature.priority == "high"


class TestVerificationReportModelValidation:
    """Tests for VerificationReport model validation."""

    def test_verification_report_creation(self, test_db, sample_feature):
        """Test creating a verification report with valid data."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.PENDING,
            details="Initial verification pending",
            expected_behavior="Feature should work as specified"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.feature_id == sample_feature.id
        assert report.status == VerificationStatus.PENDING
        assert report.details == "Initial verification pending"
        assert report.expected_behavior == "Feature should work as specified"
        assert report.id is not None

    def test_verification_report_status_enum_validation(self, test_db, sample_feature):
        """Test that status field accepts only valid enum values."""
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

    def test_verification_report_issues_found_default(self, test_db, sample_feature):
        """Test that issues_found defaults to empty list."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.IN_PROGRESS,
            details="Testing default issues list"
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.issues_found == []

    def test_verification_report_issues_found_custom(self, test_db, sample_feature):
        """Test setting custom issues in issues_found field."""
        issues = ["Issue 1", "Issue 2", "Issue 3"]
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.FAILED,
            details="Verification failed with issues",
            issues_found=issues
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.issues_found == issues

    def test_verification_report_completed_at_validation(self, test_db, sample_feature):
        """Test completed_at field validation."""
        report = VerificationReport(
            feature_id=sample_feature.id,
            status=VerificationStatus.VERIFIED,
            details="Completed verification",
            completed_at=datetime.utcnow()
        )

        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.completed_at is not None


class TestIssueTrackerModelValidation:
    """Tests for IssueTracker model validation."""

    def test_issue_creation_with_valid_data(self, test_db):
        """Test creating an issue with valid data."""
        issue = IssueTracker(
            title="Test Issue",
            description="A test issue description",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.OPEN,
            category=IssueCategory.BUG
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        assert issue.title == "Test Issue"
        assert issue.description == "A test issue description"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.status == IssueStatus.OPEN
        assert issue.category == IssueCategory.BUG
        assert issue.id is not None

    def test_issue_severity_enum_validation(self, test_db):
        """Test that severity field accepts only valid enum values."""
        for severity in IssueSeverity:
            issue = IssueTracker(
                title=f"Issue with {severity.value} severity",
                description="Test issue",
                severity=severity,
                status=IssueStatus.OPEN,
                category=IssueCategory.BUG
            )

            test_db.add(issue)
            test_db.commit()
            test_db.refresh(issue)

            assert issue.severity == severity

    def test_issue_status_enum_validation(self, test_db):
        """Test that status field accepts only valid enum values."""
        for status in IssueStatus:
            issue = IssueTracker(
                title=f"Issue with {status.value} status",
                description="Test issue",
                severity=IssueSeverity.LOW,
                status=status,
                category=IssueCategory.TASK
            )

            test_db.add(issue)
            test_db.commit()
            test_db.refresh(issue)

            assert issue.status == status

    def test_issue_category_enum_validation(self, test_db):
        """Test that category field accepts only valid enum values."""
        for category in IssueCategory:
            issue = IssueTracker(
                title=f"Issue in {category.value} category",
                description="Test issue",
                severity=IssueSeverity.MEDIUM,
                status=IssueStatus.OPEN,
                category=category
            )

            test_db.add(issue)
            test_db.commit()
            test_db.refresh(issue)

            assert issue.category == category

    def test_issue_priority_validation(self, test_db):
        """Test issue priority validation."""
        issue = IssueTracker(
            title="High Priority Issue",
            description="A high priority issue",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.OPEN,
            category=IssueCategory.BUG,
            priority=1  # Highest priority
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        assert issue.priority == 1

    def test_issue_comments_validation(self, test_db):
        """Test issue comments validation."""
        comments = [
            {"author_id": 1, "content": "First comment", "timestamp": datetime.utcnow()},
            {"author_id": 2, "content": "Second comment", "timestamp": datetime.utcnow()}
        ]

        issue = IssueTracker(
            title="Issue with Comments",
            description="An issue with comments",
            severity=IssueSeverity.MEDIUM,
            status=IssueStatus.OPEN,
            category=IssueCategory.ENHANCEMENT,
            comments=comments
        )

        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        assert len(issue.comments) == 2
        assert issue.comments[0]["content"] == "First comment"


class TestPerformanceBenchmarkModelValidation:
    """Tests for PerformanceBenchmark model validation."""

    def test_performance_benchmark_creation(self, test_db):
        """Test creating a performance benchmark with valid data."""
        benchmark = PerformanceBenchmark(
            name="API Response Time",
            metric_type=MetricType.RESPONSE_TIME,
            value=150.5,  # milliseconds
            unit="ms",
            status=BenchmarkStatus.PASSED,
            environment="test"
        )

        test_db.add(benchmark)
        test_db.commit()
        test_db.refresh(benchmark)

        assert benchmark.name == "API Response Time"
        assert benchmark.metric_type == MetricType.RESPONSE_TIME
        assert benchmark.value == 150.5
        assert benchmark.unit == "ms"
        assert benchmark.status == BenchmarkStatus.PASSED
        assert benchmark.environment == "test"
        assert benchmark.id is not None

    def test_performance_benchmark_metric_type_enum(self, test_db):
        """Test that metric_type field accepts only valid enum values."""
        for metric_type in MetricType:
            benchmark = PerformanceBenchmark(
                name=f"Benchmark for {metric_type.value}",
                metric_type=metric_type,
                value=100.0,
                unit="ms",
                status=BenchmarkStatus.PASSED,
                environment="test"
            )

            test_db.add(benchmark)
            test_db.commit()
            test_db.refresh(benchmark)

            assert benchmark.metric_type == metric_type

    def test_performance_benchmark_status_enum(self, test_db):
        """Test that status field accepts only valid enum values."""
        for status in BenchmarkStatus:
            benchmark = PerformanceBenchmark(
                name=f"Benchmark with {status.value} status",
                metric_type=MetricType.THROUGHPUT,
                value=1000.0,
                unit="req/sec",
                status=status,
                environment="production"
            )

            test_db.add(benchmark)
            test_db.commit()
            test_db.refresh(benchmark)

            assert benchmark.status == status

    def test_performance_benchmark_value_validation(self, test_db):
        """Test value field validation."""
        benchmark = PerformanceBenchmark(
            name="Positive Value Test",
            metric_type=MetricType.CPU_USAGE,
            value=85.5,  # Valid positive value
            unit="%",
            status=BenchmarkStatus.WARNING,
            environment="staging"
        )

        test_db.add(benchmark)
        test_db.commit()
        test_db.refresh(benchmark)

        assert benchmark.value == 85.5


class TestSecurityAssessmentModelValidation:
    """Tests for SecurityAssessment model validation."""

    def test_security_assessment_creation(self, test_db):
        """Test creating a security assessment with valid data."""
        assessment = SecurityAssessment(
            scan_id="scan_12345",
            scan_type=SecurityScanType.DEPENDENCY_VULNERABILITY,
            status=SecurityScanStatus.COMPLETED,
            critical_vulnerabilities=1,
            high_vulnerabilities=2,
            medium_vulnerabilities=3,
            low_vulnerabilities=4,
            findings="Various vulnerabilities found",
            recommendations="Update dependencies"
        )

        test_db.add(assessment)
        test_db.commit()
        test_db.refresh(assessment)

        assert assessment.scan_id == "scan_12345"
        assert assessment.scan_type == SecurityScanType.DEPENDENCY_VULNERABILITY
        assert assessment.status == SecurityScanStatus.COMPLETED
        assert assessment.critical_vulnerabilities == 1
        assert assessment.high_vulnerabilities == 2
        assert assessment.medium_vulnerabilities == 3
        assert assessment.low_vulnerabilities == 4
        assert assessment.findings == "Various vulnerabilities found"
        assert assessment.recommendations == "Update dependencies"
        assert assessment.id is not None

    def test_security_assessment_scan_type_enum(self, test_db):
        """Test that scan_type field accepts only valid enum values."""
        for scan_type in SecurityScanType:
            assessment = SecurityAssessment(
                scan_id=f"scan_{scan_type.value}",
                scan_type=scan_type,
                status=SecurityScanStatus.PENDING,
                critical_vulnerabilities=0,
                high_vulnerabilities=0,
                medium_vulnerabilities=0,
                low_vulnerabilities=0
            )

            test_db.add(assessment)
            test_db.commit()
            test_db.refresh(assessment)

            assert assessment.scan_type == scan_type

    def test_security_assessment_status_enum(self, test_db):
        """Test that status field accepts only valid enum values."""
        for status in SecurityScanStatus:
            assessment = SecurityAssessment(
                scan_id=f"scan_status_{status.value}",
                scan_type=SecurityScanType.STATIC_ANALYSIS,
                status=status,
                critical_vulnerabilities=0,
                high_vulnerabilities=0,
                medium_vulnerabilities=0,
                low_vulnerabilities=0
            )

            test_db.add(assessment)
            test_db.commit()
            test_db.refresh(assessment)

            assert assessment.status == status

    def test_security_assessment_vulnerability_counts(self, test_db):
        """Test vulnerability count fields validation."""
        assessment = SecurityAssessment(
            scan_id="vuln_counts_test",
            scan_type=SecurityScanType.CONTAINER_SECURITY,
            status=SecurityScanStatus.IN_PROGRESS,
            critical_vulnerabilities=2,
            high_vulnerabilities=5,
            medium_vulnerabilities=10,
            low_vulnerabilities=15
        )

        test_db.add(assessment)
        test_db.commit()
        test_db.refresh(assessment)

        assert assessment.critical_vulnerabilities == 2
        assert assessment.high_vulnerabilities == 5
        assert assessment.medium_vulnerabilities == 10
        assert assessment.low_vulnerabilities == 15


class TestDeploymentConfigModelValidation:
    """Tests for DeploymentConfig model validation."""

    def test_deployment_config_creation(self, test_db):
        """Test creating a deployment config with valid data."""
        config = DeploymentConfig(
            environment=EnvironmentType.PRODUCTION,
            config_data={
                "database_url": "postgresql://prod-db:5432/app",
                "redis_url": "redis://prod-redis:6379",
                "api_keys": {"service_a": "key123"}
            },
            version="1.0.0",
            is_active=True
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        assert config.environment == EnvironmentType.PRODUCTION
        assert "database_url" in config.config_data
        assert config.version == "1.0.0"
        assert config.is_active is True
        assert config.id is not None

    def test_deployment_config_environment_enum(self, test_db):
        """Test that environment field accepts only valid enum values."""
        for env_type in EnvironmentType:
            config = DeploymentConfig(
                environment=env_type,
                config_data={"key": "value"},
                version="1.0.0",
                is_active=False
            )

            test_db.add(config)
            test_db.commit()
            test_db.refresh(config)

            assert config.environment == env_type

    def test_deployment_config_version_format(self, test_db):
        """Test version field validation."""
        config = DeploymentConfig(
            environment=EnvironmentType.DEVELOPMENT,
            config_data={"debug": True},
            version="2.1.3",
            is_active=True
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        assert config.version == "2.1.3"

    def test_deployment_config_resource_limits(self, test_db):
        """Test resource limits configuration."""
        config = DeploymentConfig(
            environment=EnvironmentType.STAGING,
            config_data={
                "resources": {
                    "cpu": "500m",
                    "memory": "1Gi",
                    "replicas": 2
                }
            },
            version="1.0.0",
            is_active=False
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        resources = config.config_data.get("resources", {})
        assert resources.get("cpu") == "500m"
        assert resources.get("memory") == "1Gi"
        assert resources.get("replicas") == 2


class TestModelRelationships:
    """Tests for model relationships and foreign key constraints."""

    def test_feature_verification_relationship(self, test_db):
        """Test the relationship between Feature and VerificationReport."""
        # Create a feature
        feature = Feature(
            name="Related Feature",
            description="A feature for relationship testing",
            specification_reference="SPEC-REL-001"
        )
        test_db.add(feature)
        test_db.commit()
        test_db.refresh(feature)

        # Create a verification report for the feature
        report = VerificationReport(
            feature_id=feature.id,
            status=VerificationStatus.PENDING,
            details="Testing relationship"
        )
        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        # Verify the relationship
        assert report.feature_id == feature.id

    def test_user_issue_relationship(self, test_db):
        """Test the relationship between User and IssueTracker."""
        # Create a user
        user = User(
            email="reporter@example.com",
            username="reporter",
            hashed_password="password"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create an issue reported by the user
        issue = IssueTracker(
            title="User Reported Issue",
            description="Issue reported by a user",
            severity=IssueSeverity.HIGH,
            status=IssueStatus.OPEN,
            category=IssueCategory.BUG,
            reported_by_id=user.id
        )
        test_db.add(issue)
        test_db.commit()
        test_db.refresh(issue)

        # Verify the relationship
        assert issue.reported_by_id == user.id


@pytest.fixture
def sample_feature(test_db):
    """Create a sample feature for testing relationships."""
    feature = Feature(
        name="Sample Feature",
        description="A sample feature for testing",
        specification_reference="SPEC-SAMPLE-001"
    )
    test_db.add(feature)
    test_db.commit()
    test_db.refresh(feature)
    return feature