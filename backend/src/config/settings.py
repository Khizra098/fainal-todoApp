"""
Configuration settings for the AI Assistant Chat feature.
This module manages application settings and environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings class that loads from environment variables
    """
    app_name: str = "AI Assistant Chat API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    # Server configuration
    backend_host: str = os.getenv("BACKEND_HOST", "localhost")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot.db")
    neon_database_url: Optional[str] = os.getenv("NEON_DATABASE_URL")

    # OpenAI settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS settings - Add Vercel deployment domains
    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost,http://localhost:3000,http://127.0.0.1,http://127.0.0.1:3000,https://*.vercel.app"
    )

    # Performance settings
    max_message_length: int = int(os.getenv("MAX_MESSAGE_LENGTH", "10000"))  # Maximum length of a message
    response_timeout_seconds: int = int(os.getenv("RESPONSE_TIMEOUT_SECONDS", "5"))  # Timeout for generating responses
    min_confidence_score: float = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.5"))  # Minimum confidence for responses

    # MCP settings
    mcp_server_url: Optional[str] = os.getenv("MCP_SERVER_URL")
    mcp_tool_name: Optional[str] = os.getenv("MCP_TOOL_NAME")

    # Frontend configuration
    frontend_host: str = os.getenv("FRONTEND_HOST", "localhost")
    frontend_port: int = os.getenv("FRONTEND_PORT", "3000")
    backend_api_url: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    model_config = {"env_file": ".env"}


# Create a global settings instance
settings = Settings()


def get_allowed_origins_list():
    """
    Get the allowed origins as a list
    """
    return [origin.strip() for origin in settings.allowed_origins.split(",")]


def validate_settings():
    """
    Validate that required settings are present
    """
    errors = []

    # OPENAI_API_KEY is optional - if not provided, local response generation will be used
    # if not settings.openai_api_key:
    #     errors.append("OPENAI_API_KEY is required")

    if not settings.secret_key or settings.secret_key == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY should be changed from default value")

    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


# Validate settings on import
validate_settings()