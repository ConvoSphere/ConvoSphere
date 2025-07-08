"""
Configuration management for the AI Assistant Platform.

This module provides centralized configuration management using Pydantic settings
for type-safe environment variable handling and validation.
"""

from typing import List, Optional
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="AI Assistant Platform", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Host")
    port: int = Field(default=8000, description="Port")
    frontend_port: int = Field(default=3000, description="Frontend port")
    
    # Database
    database_url: str = Field(..., description="Database URL")
    database_pool_size: int = Field(default=20, description="Database pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    redis_db: int = Field(default=0, description="Redis database")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-for-development-only-change-in-production", description="Secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=30, description="JWT access token expire minutes")
    jwt_refresh_token_expire_days: int = Field(default=7, description="JWT refresh token expire days")
    
    # AI Providers
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    # LiteLLM Configuration
    litellm_model: str = Field(default="gpt-4", description="LiteLLM model")
    litellm_max_tokens: int = Field(default=4096, description="LiteLLM max tokens")
    litellm_temperature: float = Field(default=0.7, description="LiteLLM temperature")
    
    # Weaviate Configuration
    weaviate_url: str = Field(default="http://localhost:8080", description="Weaviate URL")
    weaviate_api_key: Optional[str] = Field(default=None, description="Weaviate API key")
    
    # Knowledge Base Configuration
    default_embedding_model: str = Field(default="text-embedding-ada-002", description="Default embedding model")
    default_chunk_size: int = Field(default=500, description="Default chunk size")
    default_chunk_overlap: int = Field(default=50, description="Default chunk overlap")
    max_chunk_size: int = Field(default=2000, description="Max chunk size")
    min_chunk_size: int = Field(default=100, description="Min chunk size")
    
    # Document Processing
    chunk_size: int = Field(default=500, description="Chunk size")
    chunk_overlap: int = Field(default=50, description="Chunk overlap")
    max_file_size: int = Field(default=10485760, description="Max file size")  # 10MB
    supported_file_types: List[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/markdown",
            "text/html",
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/tiff"
        ],
        description="Supported file types"
    )
    
    # File Storage
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="./logs/app.log", description="Log file")
    
    # Internationalization
    default_language: str = Field(default="en", description="Default language")
    supported_languages: List[str] = Field(
        default=["en", "de", "fr", "es", "ar", "ja"], 
        description="Supported languages"
    )
    
    # Email Configuration
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP user")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    
    # External Services
    serper_api_key: Optional[str] = Field(default=None, description="Serper API key")
    wolfram_alpha_api_key: Optional[str] = Field(default=None, description="Wolfram Alpha API key")
    
    @field_validator("supported_languages", mode="before")
    @classmethod
    def parse_supported_languages(cls, v):
        """Parse supported languages from comma-separated string."""
        if isinstance(v, str):
            try:
                return [lang.strip() for lang in v.split(",") if lang.strip()]
            except Exception:
                return ["de", "en", "fr", "es"]
        return v
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Validate secret key length."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @field_validator("litellm_temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings 