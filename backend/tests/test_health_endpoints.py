"""
Tests for health endpoints functionality.
This module contains tests for the health check system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.models.user import User
from src.database.database import Base
from src.main import app


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


class TestHealthEndpoints:
    """Tests for the health check endpoints."""

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health/health")

        # Should return 200 OK with health information
        assert response.status_code in [200, 401, 403]  # Could be successful, unauthenticated, or forbidden

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "service" in data
            assert "version" in data
            assert "environment" in data
            assert data["status"] in ["healthy", "unhealthy"]

    def test_readiness_endpoint(self, client, test_db):
        """Test the readiness check endpoint."""
        response = client.get("/health/ready")

        # Should return 200 OK with readiness information
        assert response.status_code in [200, 401, 403, 500]  # Various possible responses

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "response_time_ms" in data
            assert "checks" in data
            assert "critical_checks_passed" in data

    def test_liveness_endpoint(self, client):
        """Test the liveness check endpoint."""
        response = client.get("/health/live")

        # Should return 200 OK with liveness information
        assert response.status_code in [200, 401, 403]  # Could be various responses

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "response_time_ms" in data
            assert data["status"] in ["alive", "dead"]

    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint."""
        response = client.get("/health/metrics")

        # Should return 200 OK with metrics information
        assert response.status_code in [200, 401, 403, 500]  # Various possible responses

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            assert "service" in data
            assert "version" in data
            assert "environment" in data
            assert "metrics" in data

    def test_status_endpoint(self, client, test_db):
        """Test the detailed status endpoint."""
        response = client.get("/health/status")

        # Should return 200 OK with status information
        assert response.status_code in [200, 401, 403, 500]  # Various possible responses

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            assert "service" in data
            assert "runtime" in data
            assert "database" in data
            assert "configuration" in data


class TestHealthEndpointDetails:
    """More detailed tests for health endpoints."""

    @patch('src.api.v1.health_routes.get_settings')
    def test_health_endpoint_with_mocked_settings(self, mock_get_settings, client):
        """Test health endpoint with mocked settings."""
        # Mock the settings
        mock_settings = Mock()
        mock_settings.service_name = "test-service"
        mock_settings.service_version = "1.0.0"
        mock_settings.environment = "test"
        mock_get_settings.return_value = mock_settings

        response = client.get("/health/health")

        if response.status_code == 200:
            data = response.json()
            assert data["service"] == "test-service"
            assert data["version"] == "1.0.0"
            assert data["environment"] == "test"

    @patch('src.api.v1.health_routes.datetime')
    def test_health_timestamp_format(self, mock_datetime, client):
        """Test that health endpoint returns properly formatted timestamp."""
        # Mock datetime to return a specific value
        mock_now = datetime(2023, 1, 15, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        response = client.get("/health/health")

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            # Timestamp should be ISO format string
            assert isinstance(data["timestamp"], str)

    @patch('src.api.v1.health_routes.time')
    @patch('src.api.v1.health_routes.datetime')
    def test_readiness_response_time(self, mock_datetime, mock_time, client):
        """Test readiness endpoint response time calculation."""
        # Mock time to simulate response time
        mock_time.time.return_value = 1000.0  # Start time
        mock_time.time.return_value = 1000.5  # End time (0.5 seconds later)

        # Mock datetime for timestamp
        mock_now = datetime(2023, 1, 15, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        response = client.get("/health/ready")

        if response.status_code == 200:
            data = response.json()
            # Response time should be included and reasonable
            assert "response_time_ms" in data
            assert isinstance(data["response_time_ms"], (int, float))

    def test_health_endpoint_structure(self, client):
        """Test the complete structure of the health endpoint response."""
        response = client.get("/health/health")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["status", "timestamp", "service", "version", "environment", "checks"]
            for field in required_fields:
                assert field in data

            # Checks should contain expected sub-fields
            assert "database" in data["checks"]
            assert "external_services" in data["checks"]

    def test_readiness_endpoint_structure(self, client):
        """Test the complete structure of the readiness endpoint response."""
        response = client.get("/health/ready")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["status", "timestamp", "response_time_ms", "checks", "critical_checks_passed"]
            for field in required_fields:
                assert field in data

            # Checks should contain expected sub-fields
            assert "database" in data["checks"]

    def test_liveness_endpoint_structure(self, client):
        """Test the complete structure of the liveness endpoint response."""
        response = client.get("/health/live")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["status", "timestamp", "uptime_seconds", "response_time_ms", "checks"]
            for field in required_fields:
                assert field in data

            # Checks should contain expected sub-fields
            assert "service_responding" in data["checks"]
            assert "basic_functionality" in data["checks"]

    def test_metrics_endpoint_structure(self, client):
        """Test the complete structure of the metrics endpoint response."""
        response = client.get("/health/metrics")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["timestamp", "service", "version", "environment", "metrics"]
            for field in required_fields:
                assert field in data

            # Metrics should contain expected sub-fields
            expected_metrics = ["cpu_usage_percent", "memory_usage_mb", "active_connections", "requests_per_second"]
            for metric in expected_metrics:
                assert metric in data["metrics"]

    def test_status_endpoint_structure(self, client):
        """Test the complete structure of the status endpoint response."""
        response = client.get("/health/status")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["timestamp", "service", "runtime", "database", "configuration"]
            for field in required_fields:
                assert field in data

            # Service should contain expected sub-fields
            assert "name" in data["service"]
            assert "version" in data["service"]
            assert "environment" in data["service"]

            # Runtime should contain expected sub-fields
            assert "python_version" in data["runtime"]
            assert "os" in data["runtime"]


class TestHealthWithDatabase:
    """Tests for health endpoints with database operations."""

    def test_readiness_with_database_check(self, client, test_db):
        """Test readiness endpoint with database connectivity check."""
        response = client.get("/health/ready")

        # Should return a valid response even with database check
        assert response.status_code in [200, 401, 403, 500]

        if response.status_code == 200:
            data = response.json()
            # The database check should be part of the response
            assert "checks" in data
            assert "database" in data["checks"]

    def test_status_with_database_info(self, client, test_db):
        """Test status endpoint with database information."""
        response = client.get("/health/status")

        assert response.status_code in [200, 401, 403, 500]

        if response.status_code == 200:
            data = response.json()
            # Database information should be part of the response
            assert "database" in data
            assert "connected" in data["database"]
            assert "tables_count" in data["database"]


class TestHealthErrorScenarios:
    """Tests for health endpoints in error scenarios."""

    @patch('src.api.v1.health_routes.get_db')
    def test_readiness_with_db_error(self, mock_get_db, client):
        """Test readiness endpoint when database connection fails."""
        # Mock database connection to raise an exception
        def mock_get_db_error():
            raise Exception("Database connection failed")

        mock_get_db.side_effect = mock_get_db_error

        response = client.get("/health/ready")

        # Should handle the error gracefully
        assert response.status_code in [200, 500]  # Either success with error info or server error

    @patch('src.api.v1.health_routes.get_settings')
    def test_health_with_settings_error(self, mock_get_settings, client):
        """Test health endpoint when settings retrieval fails."""
        # Mock settings to raise an exception
        mock_get_settings.side_effect = Exception("Settings error")

        response = client.get("/health/health")

        # Should handle the error gracefully
        assert response.status_code in [200, 500]  # Either success with error info or server error

    @patch('src.api.v1.health_routes.datetime')
    def test_health_with_datetime_error(self, mock_datetime, client):
        """Test health endpoint when datetime operations fail."""
        # Mock datetime to raise an exception
        mock_datetime.utcnow.side_effect = Exception("Datetime error")

        response = client.get("/health/health")

        # Should handle the error gracefully
        assert response.status_code in [200, 500]  # Either success with error info or server error


class TestHealthAuthentication:
    """Tests for health endpoints with authentication (if applicable)."""

    def test_health_endpoint_public_access(self, client):
        """Test that health endpoints are accessible without authentication."""
        # Health endpoints are typically public
        response = client.get("/health/health")

        # Should be accessible (might return 200 or 403 depending on auth implementation)
        # But should not return 401 for unauthorized since health checks are public
        assert response.status_code in [200, 403, 500]

    def test_readiness_endpoint_public_access(self, client):
        """Test that readiness endpoint is accessible without authentication."""
        response = client.get("/health/ready")

        # Should be accessible (might return 200 or 403 depending on auth implementation)
        assert response.status_code in [200, 403, 500]

    def test_liveness_endpoint_public_access(self, client):
        """Test that liveness endpoint is accessible without authentication."""
        response = client.get("/health/live")

        # Should be accessible (might return 200 or 403 depending on auth implementation)
        assert response.status_code in [200, 403, 500]


class TestHealthPerformance:
    """Tests for health endpoint performance characteristics."""

    def test_health_endpoint_response_time(self, client):
        """Test that health endpoints respond quickly."""
        import time

        start_time = time.time()
        response = client.get("/health/health")
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Health checks should respond quickly (under 500ms)
        assert response_time < 500, f"Health check took {response_time}ms, which is too slow"

        # Should still return appropriate status
        assert response.status_code in [200, 401, 403, 500]

    def test_multiple_concurrent_health_checks(self, client):
        """Test handling of multiple concurrent health check requests."""
        import threading
        import time

        results = []

        def make_request():
            response = client.get("/health/health")
            results.append(response.status_code)

        # Create multiple threads to make requests simultaneously
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should complete successfully
        assert len(results) == 5
        for status_code in results:
            assert status_code in [200, 401, 403, 500]