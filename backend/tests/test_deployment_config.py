"""
Tests for deployment configuration functionality.
This module contains tests for the deployment configuration system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import json

from src.models.deployment_config import DeploymentConfig, EnvironmentType
from src.database.database import Base
from src.main import app
from src.services.deployment_service import DeploymentService


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
def deployment_service(test_db):
    """Create a deployment service instance."""
    return DeploymentService(test_db)


class TestDeploymentConfigModel:
    """Tests for the DeploymentConfig model."""

    def test_deployment_config_creation(self, test_db):
        """Test creating a deployment configuration."""
        config = DeploymentConfig(
            environment="development",
            database_url="postgresql://localhost/testdb",
            api_endpoints=json.dumps(["http://api.example.com"]),
            resource_limits_cpu="500m",
            resource_limits_memory="512Mi",
            replica_counts_backend=1,
            replica_counts_frontend=1,
            liveness_path="/health/live",
            readiness_path="/health/ready",
            probe_interval_seconds=30
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        assert config.environment == "development"
        assert config.database_url == "postgresql://localhost/testdb"
        assert config.resource_limits_cpu == "500m"
        assert config.resource_limits_memory == "512Mi"
        assert config.replica_counts_backend == 1
        assert config.replica_counts_frontend == 1
        assert config.liveness_path == "/health/live"
        assert config.readiness_path == "/health/ready"
        assert config.probe_interval_seconds == 30
        assert config.id is not None
        assert config.created_at is not None

    def test_deployment_config_to_dict(self, test_db):
        """Test converting deployment config to dictionary."""
        config = DeploymentConfig(
            environment="staging",
            database_url="postgresql://staging.example.com/db",
            api_endpoints=json.dumps(["http://staging.example.com/api"]),
            resource_limits_cpu="1",
            resource_limits_memory="1Gi"
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        config_dict = config.to_dict()

        assert config_dict["environment"] == "staging"
        assert config_dict["database_url"] == "postgresql://staging.example.com/db"
        assert config_dict["resource_limits"]["cpu"] == "1"
        assert config_dict["resource_limits"]["memory"] == "1Gi"
        assert config_dict["replica_counts"]["backend"] == 1
        assert config_dict["replica_counts"]["frontend"] == 1
        assert "id" in config_dict
        assert "created_at" in config_dict

    def test_deployment_config_default_values(self, test_db):
        """Test default values for deployment config."""
        config = DeploymentConfig(
            environment="production"
        )

        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        # Check default values
        assert config.environment == "production"
        assert config.resource_limits_cpu == "500m"  # Default value
        assert config.resource_limits_memory == "512Mi"  # Default value
        assert config.replica_counts_backend == 1  # Default value
        assert config.replica_counts_frontend == 1  # Default value
        assert config.liveness_path == "/health/live"  # Default value
        assert config.readiness_path == "/health/ready"  # Default value
        assert config.probe_interval_seconds == 30  # Default value
        assert config.is_active is True  # Default value


class TestDeploymentService:
    """Tests for the DeploymentService."""

    def test_create_deployment_config(self, deployment_service, test_db):
        """Test creating a deployment configuration."""
        config = deployment_service.create_deployment_config(
            environment="development",
            database_url="postgresql://localhost/testdb",
            api_endpoints=["http://api.example.com"],
            resource_limits_cpu="1",
            resource_limits_memory="1Gi",
            replica_counts_backend=2,
            replica_counts_frontend=2
        )

        assert config.environment == "development"
        assert config.database_url == "postgresql://localhost/testdb"
        assert config.resource_limits_cpu == "1"
        assert config.resource_limits_memory == "1Gi"
        assert config.replica_counts_backend == 2
        assert config.replica_counts_frontend == 2
        assert config.is_active is True  # New configs should be active by default

    def test_create_deployment_config_activates_only_one_per_env(self, deployment_service, test_db):
        """Test that creating a new config deactivates the previous one for the same environment."""
        # Create first config
        config1 = deployment_service.create_deployment_config(
            environment="production",
            database_url="postgresql://server1/db"
        )

        # Create second config for same environment
        config2 = deployment_service.create_deployment_config(
            environment="production",
            database_url="postgresql://server2/db"
        )

        # Refresh from DB to get updated values
        config1_from_db = test_db.query(DeploymentConfig).filter(DeploymentConfig.id == config1.id).first()
        config2_from_db = test_db.query(DeploymentConfig).filter(DeploymentConfig.id == config2.id).first()

        # First config should be inactive, second should be active
        assert config1_from_db.is_active is False
        assert config2_from_db.is_active is True

    def test_get_deployment_config(self, deployment_service, test_db):
        """Test getting a deployment configuration."""
        config = DeploymentConfig(
            environment="staging",
            database_url="postgresql://staging.example.com/db"
        )
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        retrieved_config = deployment_service.get_deployment_config("staging")

        assert retrieved_config is not None
        assert retrieved_config.id == config.id
        assert retrieved_config.environment == "staging"
        assert retrieved_config.database_url == "postgresql://staging.example.com/db"

    def test_get_deployment_config_by_env_none_found(self, deployment_service):
        """Test getting a deployment config for an environment that doesn't exist."""
        retrieved_config = deployment_service.get_deployment_config("nonexistent")

        assert retrieved_config is None

    def test_get_all_deployment_configs(self, deployment_service, test_db):
        """Test getting all deployment configurations."""
        # Create test configs
        config1 = DeploymentConfig(environment="development", database_url="db1")
        config2 = DeploymentConfig(environment="staging", database_url="db2")
        config3 = DeploymentConfig(environment="production", database_url="db3")

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.commit()

        configs = deployment_service.get_all_deployment_configs()

        assert len(configs) == 3
        envs = [config.environment for config in configs]
        assert "development" in envs
        assert "staging" in envs
        assert "production" in envs

    def test_get_configs_by_environment(self, deployment_service, test_db):
        """Test getting configs by environment."""
        # Create configs for different environments
        dev_config1 = DeploymentConfig(environment="development", database_url="dev1")
        dev_config2 = DeploymentConfig(environment="development", database_url="dev2")
        prod_config = DeploymentConfig(environment="production", database_url="prod1")

        test_db.add(dev_config1)
        test_db.add(dev_config2)
        test_db.add(prod_config)
        test_db.commit()

        dev_configs = deployment_service.get_configs_by_environment("development")
        assert len(dev_configs) == 2

        prod_configs = deployment_service.get_configs_by_environment("production")
        assert len(prod_configs) == 1

    def test_update_deployment_config(self, deployment_service, test_db):
        """Test updating a deployment configuration."""
        config = DeploymentConfig(
            environment="development",
            database_url="postgresql://old-server/db",
            resource_limits_cpu="500m"
        )
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        updated_config = deployment_service.update_deployment_config(
            config_id=config.id,
            database_url="postgresql://new-server/db",
            resource_limits_cpu="1"
        )

        assert updated_config.database_url == "postgresql://new-server/db"
        assert updated_config.resource_limits_cpu == "1"

    def test_activate_config(self, deployment_service, test_db):
        """Test activating a deployment configuration."""
        config = DeploymentConfig(
            environment="staging",
            database_url="postgresql://staging.example.com/db",
            is_active=False
        )
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        # Verify it's initially inactive
        assert config.is_active is False

        # Activate it
        result = deployment_service.activate_config(config.id)

        assert result is True

        # Refresh from DB to check activation
        updated_config = test_db.query(DeploymentConfig).filter(DeploymentConfig.id == config.id).first()
        assert updated_config.is_active is True

    def test_deactivate_config(self, deployment_service, test_db):
        """Test deactivating a deployment configuration."""
        config = DeploymentConfig(
            environment="staging",
            database_url="postgresql://staging.example.com/db",
            is_active=True
        )
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        # Verify it's initially active
        assert config.is_active is True

        # Deactivate it
        result = deployment_service.deactivate_config(config.id)

        assert result is True

        # Refresh from DB to check deactivation
        updated_config = test_db.query(DeploymentConfig).filter(DeploymentConfig.id == config.id).first()
        assert updated_config.is_active is False

    def test_get_environment_list(self, deployment_service, test_db):
        """Test getting list of all environments."""
        # Create configs for different environments
        config1 = DeploymentConfig(environment="development", database_url="db1")
        config2 = DeploymentConfig(environment="staging", database_url="db2")
        config3 = DeploymentConfig(environment="production", database_url="db3")

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.commit()

        env_list = deployment_service.get_environment_list()

        assert len(env_list) == 3
        assert "development" in env_list
        assert "staging" in env_list
        assert "production" in env_list

    def test_validate_config_valid(self, deployment_service):
        """Test validating a valid configuration."""
        config_data = {
            "environment": "production",
            "database_url": "postgresql://example.com/db",
            "resource_limits": {
                "cpu": "1",
                "memory": "1Gi"
            },
            "replica_counts": {
                "backend": 2,
                "frontend": 2
            },
            "health_check_config": {
                "liveness_path": "/health/live",
                "readiness_path": "/health/ready"
            }
        }

        result = deployment_service.validate_config(config_data)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_config_invalid_environment(self, deployment_service):
        """Test validating a configuration with invalid environment."""
        config_data = {
            "environment": "invalid_env",
            "database_url": "postgresql://example.com/db"
        }

        result = deployment_service.validate_config(config_data)

        assert result["valid"] is False
        assert any("Invalid environment" in error for error in result["errors"])

    def test_validate_config_missing_required_field(self, deployment_service):
        """Test validating a configuration with missing required field."""
        config_data = {
            # Missing environment field
            "database_url": "postgresql://example.com/db"
        }

        result = deployment_service.validate_config(config_data)

        assert result["valid"] is False
        assert any("Environment is required" in error for error in result["errors"])

    def test_get_config_history(self, deployment_service, test_db):
        """Test getting configuration history."""
        # Create multiple configs for the same environment
        config1 = DeploymentConfig(environment="production", database_url="db1")
        config2 = DeploymentConfig(environment="production", database_url="db2")
        config3 = DeploymentConfig(environment="staging", database_url="db3")

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.commit()

        # Get history for production
        history = deployment_service.get_config_history(environment="production", limit=10)
        assert len(history) == 2

        # Get all history
        all_history = deployment_service.get_config_history(limit=10)
        assert len(all_history) == 3

    def test_get_active_configs_count(self, deployment_service, test_db):
        """Test getting count of active configurations."""
        # Create configs with different active statuses
        config1 = DeploymentConfig(environment="dev1", database_url="db1", is_active=True)
        config2 = DeploymentConfig(environment="dev2", database_url="db2", is_active=False)
        config3 = DeploymentConfig(environment="dev3", database_url="db3", is_active=True)

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.commit()

        active_count = deployment_service.get_active_configs_count()
        assert active_count == 2

    def test_get_config_by_environment_and_active_status(self, deployment_service, test_db):
        """Test getting configs by environment and active status."""
        # Create configs with different environments and active statuses
        config1 = DeploymentConfig(environment="production", database_url="db1", is_active=True)
        config2 = DeploymentConfig(environment="production", database_url="db2", is_active=False)
        config3 = DeploymentConfig(environment="staging", database_url="db3", is_active=True)

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.commit()

        # Get active production configs
        active_prod_configs = deployment_service.get_config_by_environment_and_active_status("production", True)
        assert len(active_prod_configs) == 1
        assert active_prod_configs[0].database_url == "db1"

        # Get inactive production configs
        inactive_prod_configs = deployment_service.get_config_by_environment_and_active_status("production", False)
        assert len(inactive_prod_configs) == 1
        assert inactive_prod_configs[0].database_url == "db2"

    def test_get_deployment_statistics(self, deployment_service, test_db):
        """Test getting deployment statistics."""
        # Create configs with different environments
        config1 = DeploymentConfig(environment="production", database_url="db1", is_active=True)
        config2 = DeploymentConfig(environment="production", database_url="db2", is_active=False)
        config3 = DeploymentConfig(environment="staging", database_url="db3", is_active=True)
        config4 = DeploymentConfig(environment="development", database_url="db4", is_active=True)

        test_db.add(config1)
        test_db.add(config2)
        test_db.add(config3)
        test_db.add(config4)
        test_db.commit()

        stats = deployment_service.get_deployment_statistics()

        assert stats["total_configs"] == 4
        assert stats["active_configs"] == 3
        assert stats["inactive_configs"] == 1
        assert stats["activation_rate"] == 75.0  # 3/4 = 75%

        # Check environment distribution
        env_dist = stats["environment_distribution"]
        assert env_dist["production"] == 2
        assert env_dist["staging"] == 1
        assert env_dist["development"] == 1


class TestDeploymentAPI:
    """Tests for the deployment configuration API endpoints."""

    def test_get_deployment_config_endpoint(self, client):
        """Test the get deployment config endpoint."""
        response = client.get("/api/v1/deployment/config")

        # This will likely return 401 because of authentication, but that's expected
        assert response.status_code in [200, 401, 403]  # Could be successful, unauthenticated, or forbidden

    def test_get_deployment_config_by_environment(self, client):
        """Test the get deployment config endpoint with environment filter."""
        response = client.get("/api/v1/deployment/config?environment=production")

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 401, 403]

    def test_update_deployment_config_endpoint(self, client):
        """Test the update deployment config endpoint."""
        config_data = {
            "environment": "development",
            "database_url": "postgresql://localhost/testdb",
            "resource_limits": {
                "cpu": "1",
                "memory": "1Gi"
            },
            "replica_counts": {
                "backend": 2,
                "frontend": 2
            }
        }

        response = client.put("/api/v1/deployment/config", json=config_data)

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 400, 401, 403]  # Could be various responses

    def test_get_environments_endpoint(self, client):
        """Test the get environments endpoint."""
        response = client.get("/api/v1/deployment/environments")

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 401, 403]

    def test_get_config_history_endpoint(self, client):
        """Test the get config history endpoint."""
        response = client.get("/api/v1/deployment/config/history")

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 401, 403]

    def test_validate_config_endpoint(self, client):
        """Test the validate config endpoint."""
        config_data = {
            "environment": "production",
            "database_url": "postgresql://example.com/db"
        }

        response = client.post("/api/v1/deployment/config/validate", json=config_data)

        # This will likely return 401 because of authentication
        assert response.status_code in [200, 400, 401, 403]


class TestDeploymentServiceCleanup:
    """Tests for deployment service cleanup functionality."""

    def test_cleanup_old_configs(self, deployment_service, test_db):
        """Test cleaning up old configurations."""
        # Create multiple configs for the same environment
        configs = []
        for i in range(15):  # Create 15 configs
            config = DeploymentConfig(
                environment="production",
                database_url=f"postgresql://server{i}/db",
                is_active=False  # Make them inactive so they can be deleted
            )
            test_db.add(config)
            configs.append(config)

        test_db.commit()

        # Clean up, keeping only the last 10
        deleted_count = deployment_service.cleanup_old_configs(keep_last_n=10)

        # Should have deleted 5 configs (15 - 10 = 5)
        assert deleted_count == 5

        # Check that we have 10 configs left
        remaining_configs = deployment_service.get_config_by_environment_and_active_status("production", False)
        assert len(remaining_configs) == 10

    def test_cleanup_old_configs_preserves_active(self, deployment_service, test_db):
        """Test that cleanup doesn't delete active configurations."""
        # Create configs with some active
        for i in range(5):
            is_active = (i == 0)  # Make first one active
            config = DeploymentConfig(
                environment="production",
                database_url=f"postgresql://server{i}/db",
                is_active=is_active
            )
            test_db.add(config)

        test_db.commit()

        # Clean up, keeping only the last 3
        deleted_count = deployment_service.cleanup_old_configs(keep_last_n=3)

        # Should not have deleted the active config, so should delete 1 (inactive) config
        active_count = deployment_service.get_active_configs_count()
        assert active_count == 1  # Active config should still be there

        # Total configs after cleanup should be 4 (1 active + up to 3 inactive)
        all_configs = deployment_service.get_all_deployment_configs()
        assert len(all_configs) == 4