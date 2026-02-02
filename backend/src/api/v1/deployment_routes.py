"""
Deployment configuration API endpoints for the verification system.
This module provides endpoints for deployment settings management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import json

from ...database.database import get_db
from ...models.deployment_config import DeploymentConfig, EnvironmentType
from ...models.user import User
from ...middleware.auth import get_current_user
from ...middleware.error_handler import BusinessLogicError, NotFoundError
from ...utils.logging import get_logger


router = APIRouter(prefix="/deployment", tags=["deployment"])
logger = get_logger(__name__)


@router.get("/config", summary="Get Deployment Configuration")
async def get_deployment_config(
    environment: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve current deployment configuration.

    Args:
        environment: Filter by specific environment (optional)
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Deployment configuration
    """
    try:
        query = db.query(DeploymentConfig).filter(DeploymentConfig.is_active == True)

        if environment:
            query = query.filter(DeploymentConfig.environment == environment)

        configs = query.order_by(DeploymentConfig.created_at.desc()).all()

        if not configs:
            # Return default configuration if none found
            return {
                "configuration": {
                    "environment": environment or "development",
                    "database_url": "",
                    "api_endpoints": "[]",
                    "resource_limits": {
                        "cpu": "500m",
                        "memory": "512Mi"
                    },
                    "replica_counts": {
                        "backend": 1,
                        "frontend": 1
                    },
                    "health_check_config": {
                        "liveness_path": "/health/live",
                        "readiness_path": "/health/ready",
                        "interval_seconds": 30
                    },
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "is_active": True
                },
                "message": "Using default configuration - no active deployment config found"
            }

        # Return the most recent configuration
        config = configs[0]
        config_dict = config.to_dict()

        # Parse the api_endpoints JSON string if it exists
        if config.api_endpoints:
            try:
                config_dict["api_endpoints"] = json.loads(config.api_endpoints)
            except json.JSONDecodeError:
                config_dict["api_endpoints"] = []

        logger.info(f"Retrieved deployment config for environment {config.environment} by user {current_user.id}")

        return {
            "configuration": config_dict
        }

    except Exception as e:
        logger.error(f"Error retrieving deployment configuration: {str(e)}")
        raise


@router.put("/config", summary="Update Deployment Configuration")
async def update_deployment_config(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Update deployment configuration.

    Args:
        config_data: Configuration data to update
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Updated deployment configuration
    """
    try:
        # Validate required fields
        required_fields = ["environment"]
        for field in required_fields:
            if field not in config_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Validate environment
        environment = config_data["environment"].lower()
        try:
            env_type = EnvironmentType(environment)
        except ValueError:
            valid_envs = [env.value for env in EnvironmentType]
            raise HTTPException(status_code=400, detail=f"Invalid environment: {environment}. Valid values: {valid_envs}")

        # Check if an active config for this environment already exists
        existing_config = db.query(DeploymentConfig)\
            .filter(
                DeploymentConfig.environment == environment,
                DeploymentConfig.is_active == True
            ).first()

        if existing_config:
            # Deactivate the existing configuration
            existing_config.is_active = False
            db.commit()

        # Prepare API endpoints as JSON string
        api_endpoints = config_data.get("api_endpoints", [])
        if isinstance(api_endpoints, list):
            api_endpoints_json = json.dumps(api_endpoints)
        else:
            api_endpoints_json = "[]"

        # Create new configuration
        new_config = DeploymentConfig(
            environment=environment,
            database_url=config_data.get("database_url", ""),
            api_endpoints=api_endpoints_json,
            resource_limits_cpu=config_data.get("resource_limits", {}).get("cpu", "500m"),
            resource_limits_memory=config_data.get("resource_limits", {}).get("memory", "512Mi"),
            replica_counts_backend=config_data.get("replica_counts", {}).get("backend", 1),
            replica_counts_frontend=config_data.get("replica_counts", {}).get("frontend", 1),
            liveness_path=config_data.get("health_check_config", {}).get("liveness_path", "/health/live"),
            readiness_path=config_data.get("health_check_config", {}).get("readiness_path", "/health/ready"),
            probe_interval_seconds=config_data.get("health_check_config", {}).get("interval_seconds", 30)
        )

        db.add(new_config)
        db.commit()
        db.refresh(new_config)

        config_dict = new_config.to_dict()

        # Parse the api_endpoints JSON string
        if new_config.api_endpoints:
            try:
                config_dict["api_endpoints"] = json.loads(new_config.api_endpoints)
            except json.JSONDecodeError:
                config_dict["api_endpoints"] = []

        logger.info(f"Updated deployment config for environment {environment} by user {current_user.id}")

        return {
            "configuration": config_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deployment configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/environments", summary="Get Available Environments")
async def get_environments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get list of available deployment environments.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of available environments
    """
    try:
        # Get all unique environments
        environments = db.query(DeploymentConfig.environment).distinct().all()

        env_list = [env[0] for env in environments if env[0]]

        # Include all possible environment types
        all_env_types = [env.value for env in EnvironmentType]

        # Return both configured and possible environments
        response = {
            "configured_environments": env_list,
            "available_environments": all_env_types,
            "total_configured": len(env_list)
        }

        logger.info(f"Retrieved environments list by user {current_user.id}")

        return response

    except Exception as e:
        logger.error(f"Error retrieving environments: {str(e)}")
        raise


@router.get("/config/history", summary="Get Configuration History")
async def get_config_history(
    environment: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get deployment configuration history.

    Args:
        environment: Filter by specific environment (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Configuration history
    """
    try:
        query = db.query(DeploymentConfig)

        if environment:
            query = query.filter(DeploymentConfig.environment == environment)

        configs = query.order_by(DeploymentConfig.created_at.desc()).offset(skip).limit(limit).all()

        config_history = []
        for config in configs:
            config_dict = config.to_dict()

            # Parse the api_endpoints JSON string
            if config.api_endpoints:
                try:
                    config_dict["api_endpoints"] = json.loads(config.api_endpoints)
                except json.JSONDecodeError:
                    config_dict["api_endpoints"] = []

            # Add activation status
            config_dict["is_active"] = config.is_active

            config_history.append(config_dict)

        logger.info(f"Retrieved config history (limit: {limit}) by user {current_user.id}")

        return {
            "history": config_history,
            "total": len(config_history),
            "skip": skip,
            "limit": limit,
            "environment_filter": environment
        }

    except Exception as e:
        logger.error(f"Error retrieving config history: {str(e)}")
        raise


@router.post("/config/activate/{config_id}", summary="Activate Configuration")
async def activate_configuration(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Activate a specific deployment configuration.

    Args:
        config_id: ID of the configuration to activate
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Activation result
    """
    try:
        # Validate config_id format
        try:
            config_uuid = uuid.UUID(config_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid configuration ID format")

        # Get the configuration
        config = db.query(DeploymentConfig).filter(DeploymentConfig.id == config_uuid).first()
        if not config:
            raise NotFoundError("Configuration", config_id)

        # Deactivate all other configs for this environment
        db.query(DeploymentConfig)\
            .filter(
                DeploymentConfig.environment == config.environment,
                DeploymentConfig.id != config_uuid
            ).update({"is_active": False})

        # Activate this config
        config.is_active = True
        config.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Activated config {config_id} for environment {config.environment} by user {current_user.id}")

        return {
            "message": "Configuration activated successfully",
            "activated_config": config.to_dict()
        }

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/config/validate", summary="Validate Configuration")
async def validate_configuration(
    config_data: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Validate a deployment configuration without saving it.

    Args:
        config_data: Configuration data to validate (uses current if not provided)
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Validation results
    """
    try:
        if not config_data:
            # Get the current active config to validate
            current_config = db.query(DeploymentConfig)\
                .filter(DeploymentConfig.is_active == True)\
                .order_by(DeploymentConfig.created_at.desc())\
                .first()

            if not current_config:
                return {
                    "valid": False,
                    "errors": ["No active configuration found"],
                    "warnings": []
                }

            config_data = current_config.to_dict()
            config_data["api_endpoints"] = json.loads(current_config.api_endpoints) if current_config.api_endpoints else []

        # Perform validation checks
        errors = []
        warnings = []

        # Check environment
        if "environment" not in config_data or not config_data["environment"]:
            errors.append("Environment is required")
        else:
            try:
                EnvironmentType(config_data["environment"].lower())
            except ValueError:
                errors.append(f"Invalid environment: {config_data['environment']}")

        # Check database URL
        if "database_url" not in config_data or not config_data["database_url"]:
            warnings.append("Database URL is not set")
        elif not config_data["database_url"].startswith(("postgresql://", "postgres://", "sqlite://")):
            errors.append("Database URL must use postgresql, postgres, or sqlite protocol")

        # Check resource limits
        if "resource_limits" in config_data:
            if "cpu" in config_data["resource_limits"]:
                cpu_val = config_data["resource_limits"]["cpu"]
                if not isinstance(cpu_val, str) or not cpu_val.endswith(("m", "")) or not cpu_val.replace("m", "").isdigit():
                    warnings.append("CPU limit should be in format like '500m' or '1'")

            if "memory" in config_data["resource_limits"]:
                mem_val = config_data["resource_limits"]["memory"]
                if not isinstance(mem_val, str) or not mem_val.endswith(("Mi", "Gi")):
                    warnings.append("Memory limit should be in format like '512Mi' or '1Gi'")

        # Check replica counts
        if "replica_counts" in config_data:
            if "backend" in config_data["replica_counts"] and config_data["replica_counts"]["backend"] < 1:
                errors.append("Backend replica count must be at least 1")
            if "frontend" in config_data["replica_counts"] and config_data["replica_counts"]["frontend"] < 1:
                errors.append("Frontend replica count must be at least 1")

        is_valid = len(errors) == 0

        logger.info(f"Validated configuration for user {current_user.id} - Valid: {is_valid}")

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "config_data": config_data
        }

    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        raise