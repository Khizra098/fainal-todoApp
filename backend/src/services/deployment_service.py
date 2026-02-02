"""
Deployment configuration service for the verification system.
This module provides business logic for deployment configuration management.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import json
from enum import Enum

from ..models.deployment_config import DeploymentConfig, EnvironmentType
from ..models.user import User
from ..database.database import get_db
from ..utils.logging import get_logger


class DeploymentServiceError(Exception):
    """
    Custom exception for deployment service-related errors
    """
    pass


class DeploymentService:
    """
    Service class for handling deployment configuration logic
    """
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def get_deployment_config(self, environment: str = None) -> Optional[DeploymentConfig]:
        """
        Retrieve the active deployment configuration for an environment.

        Args:
            environment: Environment to get config for (optional)

        Returns:
            DeploymentConfig: The active configuration if found, None otherwise
        """
        try:
            query = self.db.query(DeploymentConfig).filter(DeploymentConfig.is_active == True)

            if environment:
                query = query.filter(DeploymentConfig.environment == environment)

            config = query.order_by(DeploymentConfig.created_at.desc()).first()

            if config:
                self.logger.info(f"Retrieved deployment config for environment {config.environment}")
            else:
                self.logger.info(f"No active deployment config found for environment {environment or 'any'}")

            return config
        except Exception as e:
            self.logger.error(f"Error retrieving deployment config: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve deployment config: {str(e)}")

    def get_all_deployment_configs(self) -> List[DeploymentConfig]:
        """
        Retrieve all deployment configurations.

        Returns:
            List[DeploymentConfig]: List of all deployment configurations
        """
        try:
            configs = self.db.query(DeploymentConfig).order_by(DeploymentConfig.created_at.desc()).all()
            self.logger.info(f"Retrieved {len(configs)} deployment configs")
            return configs
        except Exception as e:
            self.logger.error(f"Error retrieving deployment configs: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve deployment configs: {str(e)}")

    def get_configs_by_environment(self, environment: str) -> List[DeploymentConfig]:
        """
        Retrieve all configurations for a specific environment.

        Args:
            environment: Environment to filter by

        Returns:
            List[DeploymentConfig]: List of configurations for the environment
        """
        try:
            configs = self.db.query(DeploymentConfig)\
                .filter(DeploymentConfig.environment == environment)\
                .order_by(DeploymentConfig.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(configs)} configs for environment {environment}")
            return configs
        except Exception as e:
            self.logger.error(f"Error retrieving configs for environment {environment}: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve configs for environment: {str(e)}")

    def create_deployment_config(
        self,
        environment: str,
        database_url: str = None,
        api_endpoints: List[str] = None,
        resource_limits_cpu: str = "500m",
        resource_limits_memory: str = "512Mi",
        replica_counts_backend: int = 1,
        replica_counts_frontend: int = 1,
        liveness_path: str = "/health/live",
        readiness_path: str = "/health/ready",
        probe_interval_seconds: int = 30
    ) -> DeploymentConfig:
        """
        Create a new deployment configuration.

        Args:
            environment: Environment type
            database_url: Database connection URL
            api_endpoints: List of API endpoints
            resource_limits_cpu: CPU resource limit
            resource_limits_memory: Memory resource limit
            replica_counts_backend: Number of backend replicas
            replica_counts_frontend: Number of frontend replicas
            liveness_path: Path for liveness probe
            readiness_path: Path for readiness probe
            probe_interval_seconds: Interval for health checks

        Returns:
            DeploymentConfig: The created configuration
        """
        try:
            # First deactivate any existing active config for this environment
            existing_active = self.db.query(DeploymentConfig)\
                .filter(
                    DeploymentConfig.environment == environment,
                    DeploymentConfig.is_active == True
                ).first()

            if existing_active:
                existing_active.is_active = False
                self.db.commit()

            # Prepare API endpoints as JSON string
            api_endpoints_json = json.dumps(api_endpoints) if api_endpoints else "[]"

            # Create the new configuration
            new_config = DeploymentConfig(
                environment=environment,
                database_url=database_url or "",
                api_endpoints=api_endpoints_json,
                resource_limits_cpu=resource_limits_cpu,
                resource_limits_memory=resource_limits_memory,
                replica_counts_backend=replica_counts_backend,
                replica_counts_frontend=replica_counts_frontend,
                liveness_path=liveness_path,
                readiness_path=readiness_path,
                probe_interval_seconds=probe_interval_seconds
            )

            self.db.add(new_config)
            self.db.commit()
            self.db.refresh(new_config)

            self.logger.info(f"Created deployment config for environment {environment}")
            return new_config
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating deployment config: {str(e)}")
            raise DeploymentServiceError(f"Failed to create deployment config: {str(e)}")

    def update_deployment_config(
        self,
        config_id: uuid.UUID,
        database_url: str = None,
        api_endpoints: List[str] = None,
        resource_limits_cpu: str = None,
        resource_limits_memory: str = None,
        replica_counts_backend: int = None,
        replica_counts_frontend: int = None,
        liveness_path: str = None,
        readiness_path: str = None,
        probe_interval_seconds: int = None
    ) -> DeploymentConfig:
        """
        Update an existing deployment configuration.

        Args:
            config_id: ID of the configuration to update
            database_url: New database connection URL
            api_endpoints: New list of API endpoints
            resource_limits_cpu: New CPU resource limit
            resource_limits_memory: New Memory resource limit
            replica_counts_backend: New number of backend replicas
            replica_counts_frontend: New number of frontend replicas
            liveness_path: New path for liveness probe
            readiness_path: New path for readiness probe
            probe_interval_seconds: New interval for health checks

        Returns:
            DeploymentConfig: The updated configuration
        """
        try:
            # Get the configuration
            config = self.db.query(DeploymentConfig).filter(DeploymentConfig.id == config_id).first()
            if not config:
                raise DeploymentServiceError(f"Deployment config with ID {config_id} not found")

            # Update fields if provided
            if database_url is not None:
                config.database_url = database_url
            if api_endpoints is not None:
                config.api_endpoints = json.dumps(api_endpoints)
            if resource_limits_cpu is not None:
                config.resource_limits_cpu = resource_limits_cpu
            if resource_limits_memory is not None:
                config.resource_limits_memory = resource_limits_memory
            if replica_counts_backend is not None:
                config.replica_counts_backend = replica_counts_backend
            if replica_counts_frontend is not None:
                config.replica_counts_frontend = replica_counts_frontend
            if liveness_path is not None:
                config.liveness_path = liveness_path
            if readiness_path is not None:
                config.readiness_path = readiness_path
            if probe_interval_seconds is not None:
                config.probe_interval_seconds = probe_interval_seconds

            # Update timestamp
            config.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(config)

            self.logger.info(f"Updated deployment config {config_id}")
            return config
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating deployment config {config_id}: {str(e)}")
            raise DeploymentServiceError(f"Failed to update deployment config: {str(e)}")

    def activate_config(self, config_id: uuid.UUID) -> bool:
        """
        Activate a specific deployment configuration.

        Args:
            config_id: ID of the configuration to activate

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the configuration
            config = self.db.query(DeploymentConfig).filter(DeploymentConfig.id == config_id).first()
            if not config:
                raise DeploymentServiceError(f"Deployment config with ID {config_id} not found")

            # Deactivate all other configs for this environment
            self.db.query(DeploymentConfig)\
                .filter(
                    DeploymentConfig.environment == config.environment,
                    DeploymentConfig.id != config_id
                ).update({"is_active": False})

            # Activate this config
            config.is_active = True
            config.updated_at = datetime.utcnow()

            self.db.commit()

            self.logger.info(f"Activated config {config_id} for environment {config.environment}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error activating config {config_id}: {str(e)}")
            raise DeploymentServiceError(f"Failed to activate config: {str(e)}")

    def deactivate_config(self, config_id: uuid.UUID) -> bool:
        """
        Deactivate a specific deployment configuration.

        Args:
            config_id: ID of the configuration to deactivate

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the configuration
            config = self.db.query(DeploymentConfig).filter(DeploymentConfig.id == config_id).first()
            if not config:
                raise DeploymentServiceError(f"Deployment config with ID {config_id} not found")

            # Deactivate the config
            config.is_active = False
            config.updated_at = datetime.utcnow()

            self.db.commit()

            self.logger.info(f"Deactivated config {config_id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deactivating config {config_id}: {str(e)}")
            raise DeploymentServiceError(f"Failed to deactivate config: {str(e)}")

    def get_environment_list(self) -> List[str]:
        """
        Get list of all environments that have configurations.

        Returns:
            List[str]: List of environment names
        """
        try:
            # Get all unique environments
            environments = self.db.query(DeploymentConfig.environment).distinct().all()
            env_list = [env[0] for env in environments if env[0]]

            self.logger.info(f"Retrieved list of {len(env_list)} environments")
            return env_list
        except Exception as e:
            self.logger.error(f"Error retrieving environment list: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve environment list: {str(e)}")

    def validate_config(self, config_data: dict) -> dict:
        """
        Validate a deployment configuration without saving it.

        Args:
            config_data: Configuration data to validate

        Returns:
            dict: Validation results with errors and warnings
        """
        errors = []
        warnings = []

        try:
            # Check environment
            if "environment" not in config_data or not config_data["environment"]:
                errors.append("Environment is required")
            else:
                try:
                    EnvironmentType(config_data["environment"].lower())
                except ValueError:
                    errors.append(f"Invalid environment: {config_data['environment']}")

            # Check database URL
            if "database_url" in config_data and config_data["database_url"]:
                db_url = config_data["database_url"]
                if not db_url.startswith(("postgresql://", "postgres://", "sqlite://")):
                    errors.append("Database URL must use postgresql, postgres, or sqlite protocol")

            # Check resource limits
            if "resource_limits" in config_data:
                limits = config_data["resource_limits"]

                if "cpu" in limits:
                    cpu_val = limits["cpu"]
                    if not isinstance(cpu_val, str):
                        errors.append("CPU limit must be a string")
                    elif not (cpu_val.endswith("m") and cpu_val[:-1].isdigit()) or (cpu_val.isdigit()):
                        warnings.append("CPU limit should be in format like '500m' or '1'")

                if "memory" in limits:
                    mem_val = limits["memory"]
                    if not isinstance(mem_val, str):
                        errors.append("Memory limit must be a string")
                    elif not mem_val.endswith(("Mi", "Gi")):
                        warnings.append("Memory limit should be in format like '512Mi' or '1Gi'")

            # Check replica counts
            if "replica_counts" in config_data:
                counts = config_data["replica_counts"]

                if "backend" in counts and counts["backend"] < 1:
                    errors.append("Backend replica count must be at least 1")
                if "frontend" in counts and counts["frontend"] < 1:
                    errors.append("Frontend replica count must be at least 1")

            # Check health check paths
            if "health_check_config" in config_data:
                health_config = config_data["health_check_config"]

                if "liveness_path" in health_config and not health_config["liveness_path"].startswith("/"):
                    errors.append("Liveness path must start with '/'")

                if "readiness_path" in health_config and not health_config["readiness_path"].startswith("/"):
                    errors.append("Readiness path must start with '/'")

            is_valid = len(errors) == 0

            result = {
                "valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "config_data": config_data
            }

            self.logger.info(f"Validated configuration - Valid: {is_valid}, Errors: {len(errors)}, Warnings: {len(warnings)}")
            return result

        except Exception as e:
            self.logger.error(f"Error validating configuration: {str(e)}")
            raise DeploymentServiceError(f"Failed to validate configuration: {str(e)}")

    def get_config_history(self, environment: str = None, limit: int = 50) -> List[DeploymentConfig]:
        """
        Get configuration history.

        Args:
            environment: Filter by environment (optional)
            limit: Maximum number of records to return

        Returns:
            List[DeploymentConfig]: List of configuration history
        """
        try:
            query = self.db.query(DeploymentConfig)

            if environment:
                query = query.filter(DeploymentConfig.environment == environment)

            history = query.order_by(DeploymentConfig.created_at.desc()).limit(limit).all()

            self.logger.info(f"Retrieved config history (limit: {limit}) for environment {environment or 'all'}")
            return history
        except Exception as e:
            self.logger.error(f"Error retrieving config history: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve config history: {str(e)}")

    def get_active_configs_count(self) -> int:
        """
        Get the count of active configurations.

        Returns:
            int: Count of active configurations
        """
        try:
            count = self.db.query(DeploymentConfig).filter(DeploymentConfig.is_active == True).count()
            self.logger.info(f"Retrieved count of active configs: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Error retrieving active configs count: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve active configs count: {str(e)}")

    def get_config_by_environment_and_active_status(self, environment: str, is_active: bool = True) -> List[DeploymentConfig]:
        """
        Get configurations by environment and active status.

        Args:
            environment: Environment to filter by
            is_active: Whether to filter by active status

        Returns:
            List[DeploymentConfig]: List of configurations matching criteria
        """
        try:
            configs = self.db.query(DeploymentConfig)\
                .filter(
                    DeploymentConfig.environment == environment,
                    DeploymentConfig.is_active == is_active
                )\
                .order_by(DeploymentConfig.created_at.desc()).all()

            self.logger.info(f"Retrieved {len(configs)} configs for environment {environment} with active={is_active}")
            return configs
        except Exception as e:
            self.logger.error(f"Error retrieving configs for environment {environment} with active={is_active}: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve configs: {str(e)}")

    def get_deployment_statistics(self) -> dict:
        """
        Get statistics about deployment configurations in the system.

        Returns:
            dict: Statistics about deployment configurations
        """
        try:
            # Count total configs
            total_configs = self.db.query(DeploymentConfig).count()

            # Count active configs
            active_configs = self.db.query(DeploymentConfig).filter(DeploymentConfig.is_active == True).count()

            # Count by environment
            environment_counts = {}
            for env in EnvironmentType:
                count = self.db.query(DeploymentConfig)\
                    .filter(DeploymentConfig.environment == env.value).count()
                environment_counts[env.value] = count

            # Count inactive configs
            inactive_configs = total_configs - active_configs

            stats = {
                "total_configs": total_configs,
                "active_configs": active_configs,
                "inactive_configs": inactive_configs,
                "environment_distribution": environment_counts,
                "activation_rate": round((active_configs / total_configs) * 100, 2) if total_configs > 0 else 0
            }

            self.logger.info("Retrieved deployment configuration statistics")
            return stats
        except Exception as e:
            self.logger.error(f"Error retrieving deployment statistics: {str(e)}")
            raise DeploymentServiceError(f"Failed to retrieve deployment statistics: {str(e)}")

    def cleanup_old_configs(self, keep_last_n: int = 10) -> int:
        """
        Clean up old configurations, keeping only the most recent N for each environment.

        Args:
            keep_last_n: Number of most recent configs to keep per environment

        Returns:
            int: Number of configurations deleted
        """
        try:
            deleted_count = 0

            # Get all unique environments
            environments = self.get_environment_list()

            for env in environments:
                # Get all configs for this environment, ordered by creation date (oldest first)
                all_configs = self.db.query(DeploymentConfig)\
                    .filter(DeploymentConfig.environment == env)\
                    .order_by(DeploymentConfig.created_at.asc()).all()

                # Keep only the last N configs, delete the rest
                configs_to_delete = all_configs[:-keep_last_n] if len(all_configs) > keep_last_n else []

                for config in configs_to_delete:
                    # Don't delete active configs
                    if not config.is_active:
                        self.db.delete(config)
                        deleted_count += 1

            self.db.commit()

            self.logger.info(f"Cleaned up {deleted_count} old configurations, keeping last {keep_last_n} per environment")
            return deleted_count
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error cleaning up old configs: {str(e)}")
            raise DeploymentServiceError(f"Failed to clean up old configs: {str(e)}")