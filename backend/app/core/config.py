"""
Configuration management for the AI Assistant Platform.

This module provides centralized configuration management using Pydantic settings
for type-safe environment variable handling and validation.
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="AI Assistant Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    frontend_port: int = Field(default=3000, env="FRONTEND_PORT")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # AI Providers
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # LiteLLM Configuration
    litellm_model: str = Field(default="gpt-4", env="LITELLM_MODEL")
    litellm_max_tokens: int = Field(default=4096, env="LITELLM_MAX_TOKENS")
    litellm_temperature: float = Field(default=0.7, env="LITELLM_TEMPERATURE")
    
    # Weaviate Configuration
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    # Knowledge Base Configuration
    default_embedding_model: str = Field(default="text-embedding-ada-002", env="DEFAULT_EMBEDDING_MODEL")
    default_chunk_size: int = Field(default=500, env="DEFAULT_CHUNK_SIZE")
    default_chunk_overlap: int = Field(default=50, env="DEFAULT_CHUNK_OVERLAP")
    max_chunk_size: int = Field(default=2000, env="MAX_CHUNK_SIZE")
    min_chunk_size: int = Field(default=100, env="MIN_CHUNK_SIZE")
    
    # Document Processing
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
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
        env="SUPPORTED_FILE_TYPES"
    )
    
    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # Internationalization
    default_language: str = Field(default="de", env="DEFAULT_LANGUAGE")
    supported_languages: List[str] = Field(default=["de", "en", "fr", "es"], env="SUPPORTED_LANGUAGES")
    
    # Email Configuration
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # External Services
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    wolfram_alpha_api_key: Optional[str] = Field(default=None, env="WOLFRAM_ALPHA_API_KEY")
    
    @validator("supported_languages", pre=True)
    def parse_supported_languages(cls, v):
        """Parse supported languages from comma-separated string."""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validate secret key length."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("litellm_temperature")
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings 