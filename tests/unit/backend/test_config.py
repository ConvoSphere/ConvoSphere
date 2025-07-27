from backend.app.core.config import settings


def test_settings_loading():
    """Test that settings load correctly."""
    assert settings.app_name == "AI Assistant Platform"  # noqa: S101
    assert settings.app_version == "1.0.0"  # noqa: S101
    assert isinstance(settings.debug, bool)  # noqa: S101
    assert isinstance(settings.port, int)  # noqa: S101
    assert settings.port == 8000  # noqa: S101


def test_database_settings():
    """Test database-related settings."""
    assert hasattr(settings, "database_url")  # noqa: S101
    assert hasattr(settings, "database_pool_size")  # noqa: S101
    assert hasattr(settings, "database_max_overflow")  # noqa: S101
    assert isinstance(settings.database_pool_size, int)  # noqa: S101
    assert isinstance(settings.database_max_overflow, int)  # noqa: S101


def test_redis_settings():
    """Test Redis-related settings."""
    assert hasattr(settings, "redis_url")  # noqa: S101
    assert hasattr(settings, "redis_db")  # noqa: S101
    assert isinstance(settings.redis_db, int)  # noqa: S101


def test_weaviate_settings():
    """Test Weaviate-related settings."""
    assert hasattr(settings, "weaviate_url")  # noqa: S101
    assert settings.weaviate_url == "http://localhost:8080"  # noqa: S101
    assert hasattr(settings, "weaviate_api_key")  # noqa: S101
    # weaviate_timeout is not implemented yet


def test_security_settings():
    """Test security-related settings."""
    assert hasattr(settings, "secret_key")  # noqa: S101
    assert hasattr(settings, "jwt_algorithm")  # noqa: S101
    assert hasattr(settings, "jwt_access_token_expire_minutes")  # noqa: S101
    assert hasattr(settings, "jwt_refresh_token_expire_days")  # noqa: S101
    assert settings.jwt_algorithm == "HS256"  # noqa: S101
    assert isinstance(settings.jwt_access_token_expire_minutes, int)  # noqa: S101
    assert isinstance(settings.jwt_refresh_token_expire_days, int)  # noqa: S101


def test_ai_settings():
    """Test AI-related settings."""
    assert hasattr(settings, "litellm_model")  # noqa: S101
    assert hasattr(settings, "litellm_max_tokens")  # noqa: S101
    assert hasattr(settings, "litellm_temperature")  # noqa: S101
    assert isinstance(settings.litellm_max_tokens, int)  # noqa: S101
    assert isinstance(settings.litellm_temperature, float)  # noqa: S101


def test_internationalization_settings():
    """Test i18n-related settings."""
    assert hasattr(settings, "default_language")  # noqa: S101
    assert hasattr(settings, "languages")  # noqa: S101
    assert settings.default_language == "de"  # noqa: S101
    assert isinstance(settings.languages, list)  # noqa: S101
    assert "de" in settings.languages  # noqa: S101
    assert "en" in settings.languages  # noqa: S101
