"""
Configuration management for the AI Assistant Platform.

This module provides centralized configuration management using Pydantic settings
for type-safe environment variable handling and validation.
"""

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    database_url: str = Field(default="sqlite:///./test.db", description="Database URL")
    database_pool_size: int = Field(default=20, description="Database pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    redis_db: int = Field(default=0, description="Redis database")


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(
        default="dev-secret-key-for-development-only-change-in-production",
        description="Secret key - must be set in production",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        description="JWT access token expire minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="JWT refresh token expire days",
    )
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Validate secret key."""
        if not v:
            raise ValueError("Secret key must be set")

        # Allow development secret key only in debug mode
        if v == "dev-secret-key-for-development-only-change-in-production":
            # Check if we're in production mode
            import os

            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("Secret key must be properly configured in production")
            return v

        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")

        # Additional security checks for production
        import os

        if len(v) < 64 and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError(
                "Production secret key should be at least 64 characters long"
            )

        return v


class AISettings(BaseSettings):
    """AI service configuration settings."""
    
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    google_api_key: str | None = Field(default=None, description="Google API key")
    
    # LiteLLM Configuration
    litellm_model: str = Field(default="gpt-4", description="LiteLLM model")
    litellm_max_tokens: int = Field(default=4096, description="LiteLLM max tokens")
    litellm_temperature: float = Field(default=0.7, description="LiteLLM temperature")
    litellm_proxy_host: str | None = Field(
        default=None,
        description="LiteLLM proxy host",
    )
    
    @field_validator("litellm_temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class WeaviateSettings(BaseSettings):
    """Weaviate configuration settings."""
    
    weaviate_url: str = Field(
        default="http://localhost:8080",
        description="Weaviate URL",
    )
    weaviate_api_key: str | None = Field(default=None, description="Weaviate API key")


class KnowledgeBaseSettings(BaseSettings):
    """Knowledge base configuration settings."""
    
    default_embedding_model: str = Field(
        default="text-embedding-ada-002",
        description="Default embedding model",
    )
    default_chunk_size: int = Field(default=500, description="Default chunk size")
    default_chunk_overlap: int = Field(default=50, description="Default chunk overlap")
    max_chunk_size: int = Field(default=2000, description="Max chunk size")
    min_chunk_size: int = Field(default=100, description="Min chunk size")
    
    # Document Processing
    chunk_size: int = Field(default=500, description="Chunk size")
    chunk_overlap: int = Field(default=50, description="Chunk overlap")
    max_file_size: int = Field(default=10485760, description="Max file size")  # 10MB
    supported_file_types: list[str] = Field(
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
            "image/tiff",
        ],
        description="Supported file types",
    )


class StorageSettings(BaseSettings):
    """Storage configuration settings."""
    
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    backup_dir: str = Field(default="./backups", description="Backup directory")
    
    # Storage Configuration
    storage_provider: str = Field(default="local", description="Storage provider (local, minio, s3, gcs, azure)")
    storage_bucket_name: str = Field(default="knowledge-base", description="Storage bucket/container name")
    
    # MinIO Configuration (default cloud storage)
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    minio_secure: bool = Field(default=False, description="Use secure connection for MinIO")
    
    # S3 Configuration
    s3_endpoint_url: str | None = Field(default=None, description="S3 endpoint URL")
    s3_access_key_id: str | None = Field(default=None, description="S3 access key ID")
    s3_secret_access_key: str | None = Field(default=None, description="S3 secret access key")
    s3_region: str | None = Field(default=None, description="S3 region")
    
    # GCS Configuration
    gcs_project_id: str | None = Field(default=None, description="Google Cloud project ID")
    gcs_credentials_file: str | None = Field(default=None, description="GCS credentials file path")
    
    # Azure Configuration
    azure_account_name: str | None = Field(default=None, description="Azure storage account name")
    azure_account_key: str | None = Field(default=None, description="Azure storage account key")
    azure_connection_string: str | None = Field(default=None, description="Azure connection string")


class CORSSettings(BaseSettings):
    """CORS configuration settings."""
    
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost:8081",
        description="Comma-separated list of allowed CORS origins - restrict in production",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods for CORS",
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="Allowed headers for CORS",
    )
    cors_max_age: int = Field(
        default=86400,
        description="CORS preflight cache time in seconds",
    )


class SSOSettings(BaseSettings):
    """SSO configuration settings."""
    
    # Google OAuth2
    sso_google_enabled: bool = Field(default=False, description="Enable Google SSO")
    sso_google_client_id: str | None = Field(
        default=None,
        description="Google OAuth2 client ID",
    )
    sso_google_client_secret: str | None = Field(
        default=None,
        description="Google OAuth2 client secret",
    )
    sso_google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/sso/callback/google",
        description="Google OAuth2 redirect URI",
    )

    # Microsoft OAuth2
    sso_microsoft_enabled: bool = Field(
        default=False,
        description="Enable Microsoft SSO",
    )
    sso_microsoft_client_id: str | None = Field(
        default=None,
        description="Microsoft OAuth2 client ID",
    )
    sso_microsoft_client_secret: str | None = Field(
        default=None,
        description="Microsoft OAuth2 client secret",
    )
    sso_microsoft_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/sso/callback/microsoft",
        description="Microsoft OAuth2 redirect URI",
    )
    sso_microsoft_tenant_id: str | None = Field(
        default=None,
        description="Microsoft tenant ID",
    )

    # GitHub OAuth2
    sso_github_enabled: bool = Field(default=False, description="Enable GitHub SSO")
    sso_github_client_id: str | None = Field(
        default=None,
        description="GitHub OAuth2 client ID",
    )
    sso_github_client_secret: str | None = Field(
        default=None,
        description="GitHub OAuth2 client secret",
    )
    sso_github_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/sso/callback/github",
        description="GitHub OAuth2 redirect URI",
    )

    # SAML Configuration
    sso_saml_enabled: bool = Field(default=False, description="Enable SAML SSO")
    sso_saml_metadata_url: str | None = Field(
        default=None,
        description="SAML metadata URL",
    )
    sso_saml_entity_id: str = Field(
        default="http://localhost:8000",
        description="SAML entity ID",
    )
    sso_saml_acs_url: str = Field(
        default="http://localhost:8000/api/v1/auth/sso/callback/saml",
        description="SAML assertion consumer service URL",
    )
    sso_saml_cert_file: str | None = Field(
        default=None,
        description="SAML certificate file path",
    )
    sso_saml_key_file: str | None = Field(
        default=None,
        description="SAML private key file path",
    )

    # OIDC Configuration
    sso_oidc_enabled: bool = Field(default=False, description="Enable OIDC SSO")
    sso_oidc_issuer_url: str | None = Field(default=None, description="OIDC issuer URL")
    sso_oidc_client_id: str | None = Field(default=None, description="OIDC client ID")
    sso_oidc_client_secret: str | None = Field(
        default=None,
        description="OIDC client secret",
    )
    sso_oidc_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/sso/callback/oidc",
        description="OIDC redirect URI",
    )


class EmailSettings(BaseSettings):
    """Email configuration settings."""
    
    smtp_host: str | None = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: str | None = Field(default=None, description="SMTP user")
    smtp_password: str | None = Field(default=None, description="SMTP password")
    email_from_address: str | None = Field(
        default=None, description="From email address for notifications"
    )


class SecurityFeatureSettings(BaseSettings):
    """Security feature configuration settings."""
    
    # Password Reset Configuration
    password_reset_token_expire_minutes: int = Field(
        default=60, description="Password reset token expiration time in minutes"
    )
    password_reset_base_url: str = Field(
        default="http://localhost:3000", description="Base URL for password reset links"
    )

    # Rate Limiting Configuration
    password_reset_rate_limit_ip_max: int = Field(
        default=5, description="Maximum password reset requests per IP per hour"
    )
    password_reset_rate_limit_email_max: int = Field(
        default=3, description="Maximum password reset requests per email per hour"
    )
    password_reset_rate_limit_window: int = Field(
        default=3600, description="Rate limiting window in seconds (1 hour)"
    )

    # CSRF Protection Configuration
    csrf_token_expire_minutes: int = Field(
        default=30, description="CSRF token expiration time in minutes"
    )
    csrf_protection_enabled: bool = Field(
        default=True, description="Enable CSRF protection for sensitive operations"
    )


class MonitoringSettings(BaseSettings):
    """Monitoring and performance configuration settings."""
    
    performance_monitoring_enabled: bool = Field(
        default=True,
        json_schema_extra={"env": "PERFORMANCE_MONITORING_ENABLED"},
    )
    performance_monitoring_interval: int = Field(
        default=60,
        json_schema_extra={"env": "PERFORMANCE_MONITORING_INTERVAL"},
    )
    monitoring_max_metrics: int = Field(
        default=10000,
        json_schema_extra={"env": "MONITORING_MAX_METRICS"},
    )
    monitoring_retention_hours: int = Field(
        default=24,
        json_schema_extra={"env": "MONITORING_RETENTION_HOURS"},
    )
    monitoring_collection_interval: int = Field(
        default=60,
        json_schema_extra={"env": "MONITORING_COLLECTION_INTERVAL"},
    )
    performance_alert_thresholds: dict = Field(default_factory=dict)


class Settings(BaseSettings):
    """Main application settings combining all configuration sections."""

    # Application
    app_name: str = Field(
        default="AI Assistant Platform",
        description="Application name",
    )
    app_version: str = Field(default="0.1.0-beta", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment")

    # Server
    host: str = Field(default="0.0.0.0", description="Host")  # nosec B104 - 0.0.0.0 is correct for server binding
    port: int = Field(default=8000, description="Port")
    frontend_port: int = Field(default=3000, description="Frontend port")

    # Frontend-Backend Communication
    backend_url: str = Field(
        default="http://localhost:8000",
        description="Backend URL for frontend communication",
    )
    ws_url: str = Field(
        default="ws://localhost:8000",
        description="WebSocket URL for frontend communication",
    )
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for CORS configuration",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="./logs/app.log", description="Log file")

    # Internationalization
    default_language: str = Field(default="de", description="Default language")
    languages: list[str] = Field(
        default=["de", "en", "fr", "es"],
        description="Supported languages",
    )

    # External Services
    serper_api_key: str | None = Field(default=None, description="Serper API key")
    wolfram_alpha_api_key: str | None = Field(
        default=None,
        description="Wolfram Alpha API key",
    )

    # Registration
    registration_enabled: bool = Field(
        default=True,
        json_schema_extra={"env": "REGISTRATION_ENABLED"},
    )

    default_ai_model: str = Field(
        default="gpt-4",
        json_schema_extra={"env": "DEFAULT_AI_MODEL"},
    )

    # Include specialized settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ai: AISettings = Field(default_factory=AISettings)
    weaviate: WeaviateSettings = Field(default_factory=WeaviateSettings)
    knowledge_base: KnowledgeBaseSettings = Field(default_factory=KnowledgeBaseSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    sso: SSOSettings = Field(default_factory=SSOSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    security_features: SecurityFeatureSettings = Field(default_factory=SecurityFeatureSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
