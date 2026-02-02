"""
Configuration module for the verification system.
This module provides centralized configuration management.
"""

from typing import Optional
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://todo_user:password@localhost:5432/todo_app")
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    database_pool_timeout: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    # API settings
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-default-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # AI/ML settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ai_response_timeout: int = int(os.getenv("AI_RESPONSE_TIMEOUT", "30000"))  # in milliseconds

    # Performance settings
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # Rate limiting
    standard_requests_per_minute: int = int(os.getenv("STANDARD_REQUESTS_PER_MINUTE", "100"))
    heavy_compute_requests_per_minute: int = int(os.getenv("HEAVY_COMPUTE_REQUESTS_PER_MINUTE", "10"))

    # Verification settings
    verification_timeout_seconds: int = int(os.getenv("VERIFICATION_TIMEOUT_SECONDS", "300"))
    default_coverage_threshold: float = float(os.getenv("DEFAULT_COVERAGE_THRESHOLD", "0.80"))

    # Deployment settings
    environment: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    service_name: str = os.getenv("SERVICE_NAME", "todo-backend")
    service_version: str = os.getenv("SERVICE_VERSION", "1.0.0")

    # Health check settings
    health_check_path: str = os.getenv("HEALTH_CHECK_PATH", "/health")
    readiness_check_timeout: int = int(os.getenv("READINESS_CHECK_TIMEOUT", "10"))

    @field_validator('database_url')
    def validate_database_url(cls, v):
        """
        Validate database URL format
        """
        if not v:
            raise ValueError('DATABASE_URL cannot be empty')
        if not v.startswith(('postgresql://', 'postgres://', 'sqlite://')):
            raise ValueError('DATABASE_URL must use postgresql, postgres, or sqlite protocol')
        return v

    @field_validator('access_token_expire_minutes')
    def validate_token_expiry(cls, v):
        """
        Validate access token expiry is reasonable
        """
        if v < 1 or v > 10080:  # 1 week maximum
            raise ValueError('ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 10080 (1 week)')
        return v

    @field_validator('environment')
    def validate_environment(cls, v):
        """
        Validate environment value
        """
        allowed_environments = ['development', 'staging', 'production']
        if v.lower() not in allowed_environments:
            raise ValueError(f'ENVIRONMENT must be one of {allowed_environments}')
        return v.lower()

    model_config = {"env_file": ".env", "extra": "allow"}


# Create a single instance of settings
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings instance

    Returns:
        Settings: The application settings
    """
    return settings