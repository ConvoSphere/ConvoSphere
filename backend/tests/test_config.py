from app.core.config import settings


def test_settings_loading():
    """Test that settings load correctly."""
    assert settings.app_name == "AI Assistant Platform"
    assert settings.app_version == "1.0.0"
    assert isinstance(settings.debug, bool)
    assert isinstance(settings.port, int)
    assert settings.port == 8000


def test_database_settings():
    """Test database-related settings."""
    assert hasattr(settings, "database_url")
    assert hasattr(settings, "database_pool_size")
    assert hasattr(settings, "database_max_overflow")
    assert isinstance(settings.database_pool_size, int)
    assert isinstance(settings.database_max_overflow, int)


def test_redis_settings():
    """Test Redis-related settings."""
    assert hasattr(settings, "redis_url")
    assert hasattr(settings, "redis_db")
    assert isinstance(settings.redis_db, int)


def test_weaviate_settings():
    """Test Weaviate-related settings."""
    assert hasattr(settings, "weaviate_url")
    assert settings.weaviate_url == "http://localhost:8080"
    assert hasattr(settings, "weaviate_api_key")
    # weaviate_timeout is not implemented yet


def test_security_settings():
    """Test security-related settings."""
    assert hasattr(settings, "secret_key")
    assert hasattr(settings, "jwt_algorithm")
    assert hasattr(settings, "jwt_access_token_expire_minutes")
    assert hasattr(settings, "jwt_refresh_token_expire_days")
    assert settings.jwt_algorithm == "HS256"
    assert isinstance(settings.jwt_access_token_expire_minutes, int)
    assert isinstance(settings.jwt_refresh_token_expire_days, int)


def test_ai_settings():
    """Test AI-related settings."""
    assert hasattr(settings, "litellm_model")
    assert hasattr(settings, "litellm_max_tokens")
    assert hasattr(settings, "litellm_temperature")
    assert isinstance(settings.litellm_max_tokens, int)
    assert isinstance(settings.litellm_temperature, float)


def test_internationalization_settings():
    """Test i18n-related settings."""
    assert hasattr(settings, "default_language")
    assert hasattr(settings, "supported_languages")
    assert settings.default_language == "de"
    assert isinstance(settings.supported_languages, list)
    assert "de" in settings.supported_languages
    assert "en" in settings.supported_languages
