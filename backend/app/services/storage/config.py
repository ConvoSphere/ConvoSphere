"""
Storage configuration management.

This module defines the configuration structure for different storage providers
including local filesystem, S3, MinIO, GCS, and Azure Blob Storage.
"""


from pydantic import BaseModel, Field, field_validator


class StorageConfig(BaseModel):
    """Storage configuration for different providers."""

    # General settings
    provider: str = Field(default="local", description="Storage provider (local, s3, minio, gcs, azure)")
    bucket_name: str = Field(default="knowledge-base", description="Storage bucket/container name")

    # Connection settings
    use_ssl: bool = Field(default=True, description="Use SSL for connections")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Connection timeout in seconds")

    # S3 Configuration
    s3_endpoint_url: str | None = Field(default=None, description="S3 endpoint URL")
    s3_access_key_id: str | None = Field(default=None, description="S3 access key ID")
    s3_secret_access_key: str | None = Field(default=None, description="S3 secret access key")
    s3_region: str | None = Field(default=None, description="S3 region")

    # MinIO Configuration (S3-compatible)
    minio_endpoint: str | None = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str | None = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str | None = Field(default="minioadmin", description="MinIO secret key")
    minio_secure: bool = Field(default=False, description="Use secure connection for MinIO")

    # GCS Configuration
    gcs_project_id: str | None = Field(default=None, description="Google Cloud project ID")
    gcs_credentials_file: str | None = Field(default=None, description="GCS credentials file path")
    gcs_credentials_json: str | None = Field(default=None, description="GCS credentials as JSON string")

    # Azure Configuration
    azure_account_name: str | None = Field(default=None, description="Azure storage account name")
    azure_account_key: str | None = Field(default=None, description="Azure storage account key")
    azure_connection_string: str | None = Field(default=None, description="Azure connection string")
    azure_sas_token: str | None = Field(default=None, description="Azure SAS token")

    # Local storage settings
    local_base_path: str | None = Field(default="./uploads", description="Local storage base path")

    # Performance settings
    chunk_size: int = Field(default=8192, description="Upload/download chunk size in bytes")
    max_concurrent_uploads: int = Field(default=10, description="Maximum concurrent uploads")

    # Security settings
    encryption_enabled: bool = Field(default=False, description="Enable client-side encryption")
    encryption_key: str | None = Field(default=None, description="Encryption key for client-side encryption")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        """Validate storage provider."""
        valid_providers = ["local", "s3", "minio", "gcs", "azure"]
        if v.lower() not in valid_providers:
            raise ValueError(f"Invalid storage provider. Must be one of: {valid_providers}")
        return v.lower()

    @field_validator("bucket_name")
    @classmethod
    def validate_bucket_name(cls, v):
        """Validate bucket name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Bucket name cannot be empty")

        # Remove leading/trailing whitespace
        v = v.strip()

        # Check for invalid characters
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"Bucket name cannot contain character: {char}")

        # Check length (most providers have limits)
        if len(v) > 63:
            raise ValueError("Bucket name cannot exceed 63 characters")

        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v):
        """Validate max retries value."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        if v > 10:
            raise ValueError("Max retries cannot exceed 10")
        return v

    def get_provider_config(self) -> dict:
        """Get provider-specific configuration."""
        if self.provider == "local":
            return {
                "base_path": self.local_base_path,
                "bucket_name": self.bucket_name
            }
        if self.provider == "s3":
            return {
                "endpoint_url": self.s3_endpoint_url,
                "access_key_id": self.s3_access_key_id,
                "secret_access_key": self.s3_secret_access_key,
                "region": self.s3_region,
                "bucket_name": self.bucket_name,
                "use_ssl": self.use_ssl,
                "max_retries": self.max_retries,
                "timeout": self.timeout
            }
        if self.provider == "minio":
            return {
                "endpoint": self.minio_endpoint,
                "access_key": self.minio_access_key,
                "secret_key": self.minio_secret_key,
                "secure": self.minio_secure,
                "bucket_name": self.bucket_name,
                "region": self.s3_region,
                "max_retries": self.max_retries,
                "timeout": self.timeout
            }
        if self.provider == "gcs":
            return {
                "project_id": self.gcs_project_id,
                "credentials_file": self.gcs_credentials_file,
                "credentials_json": self.gcs_credentials_json,
                "bucket_name": self.bucket_name,
                "timeout": self.timeout
            }
        if self.provider == "azure":
            return {
                "account_name": self.azure_account_name,
                "account_key": self.azure_account_key,
                "connection_string": self.azure_connection_string,
                "sas_token": self.azure_sas_token,
                "container_name": self.bucket_name,
                "timeout": self.timeout
            }
        raise ValueError(f"Unsupported provider: {self.provider}")

    def validate_provider_config(self) -> bool:
        """Validate that all required fields for the selected provider are set."""
        config = self.get_provider_config()

        if self.provider == "s3":
            required_fields = ["access_key_id", "secret_access_key"]
            if not all(config.get(field) for field in required_fields):
                raise ValueError("S3 provider requires access_key_id and secret_access_key")

        elif self.provider == "minio":
            required_fields = ["access_key", "secret_key"]
            if not all(config.get(field) for field in required_fields):
                raise ValueError("MinIO provider requires access_key and secret_key")

        elif self.provider == "gcs":
            if not (config.get("credentials_file") or config.get("credentials_json")):
                raise ValueError("GCS provider requires either credentials_file or credentials_json")

        elif self.provider == "azure":
            if not (config.get("connection_string") or (config.get("account_name") and config.get("account_key"))):
                raise ValueError("Azure provider requires either connection_string or account_name + account_key")

        return True
