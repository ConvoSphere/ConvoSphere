import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"  # nosec # noqa: S105
    hashed = get_password_hash(password)

    # Verify the hash is different from original
    assert hashed != password  # noqa: S101

    # Verify password matches
    assert verify_password(password, hashed) is True  # noqa: S101

    # Verify wrong password fails
    assert verify_password("wrong_password", hashed) is False  # noqa: S101


@pytest.mark.asyncio()
async def test_jwt_token_creation():
    """Test JWT token creation and verification."""
    user_id = "test_user_123"

    # Create tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Verify tokens are different
    assert access_token != refresh_token  # noqa: S101

    # Verify tokens are valid
    decoded_user_id = await verify_token(access_token)
    assert decoded_user_id == user_id  # noqa: S101

    decoded_refresh_user_id = await verify_token(refresh_token)
    assert decoded_refresh_user_id == user_id  # noqa: S101


@pytest.mark.asyncio()
async def test_jwt_token_verification_invalid():
    """Test JWT token verification with invalid token."""
    invalid_token = "invalid.jwt.token"  # nosec # noqa: S105
    result = await verify_token(invalid_token)
    assert result is None  # noqa: S101


def test_rate_limiter():
    """Test rate limiter function (basic structure test)."""
    from app.utils.security import rate_limiter

    # This is a basic test to ensure the function exists and is callable
    assert callable(rate_limiter)  # noqa: S101
