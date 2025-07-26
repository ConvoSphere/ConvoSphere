from backend.app.utils.helpers import generate_uuid, sanitize_filename, validate_email


def test_generate_uuid():
    """Test UUID generation."""
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()

    # UUIDs should be different
    assert uuid1 != uuid2

    # UUIDs should be strings
    assert isinstance(uuid1, str)
    assert isinstance(uuid2, str)

    # UUIDs should have correct format
    assert len(uuid1) == 36  # Standard UUID length
    assert uuid1.count("-") == 4  # Standard UUID format


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test basic sanitization
    assert sanitize_filename("test file.txt") == "test_file.txt"
    assert (
        sanitize_filename("file with spaces & symbols!.pdf")
        == "file_with_spaces___symbols_.pdf"
    )
    # Test edge cases
    assert sanitize_filename("") == "unnamed"
    assert sanitize_filename("   ") == "unnamed"
    assert sanitize_filename("file.txt") == "file.txt"
    assert sanitize_filename("file with spaces.txt") == "file_with_spaces.txt"


def test_validate_email():
    """Test email validation."""
    # Valid emails
    assert validate_email("test@example.com") is True
    assert validate_email("user.name@domain.co.uk") is True
    assert validate_email("user+tag@example.org") is True
    # Invalid emails
    assert validate_email("invalid-email") is False
    assert validate_email("@example.com") is False
    assert validate_email("user@") is False
    assert validate_email("") is False
    assert validate_email(None) is False


def test_validate_password_strength():
    """Test password strength validation."""
    from backend.app.utils.helpers import validate_password_strength

    # Strong passwords
    assert validate_password_strength("StrongPass123!") is True
    assert validate_password_strength("Abc123!X") is True
    # Weak passwords
    assert validate_password_strength("short") is False
    assert validate_password_strength("alllowercase123") is False
    assert validate_password_strength("ALLUPPERCASE123") is False
    assert validate_password_strength("NoDigits!") is False
    # Custom min_length
    assert validate_password_strength("Abc123!", min_length=8) is False
    assert validate_password_strength("Abc123!X", min_length=8) is True


def test_validate_password_strength_custom_rules():
    """Test password strength with custom rules."""
    from backend.app.utils.helpers import validate_password_strength

    # Test with minimum length requirement
    assert validate_password_strength("Abc123!", min_length=8) is False
    assert validate_password_strength("Abc123!X", min_length=8) is True
    # Test with higher minimum length
    assert validate_password_strength("Abc123!X", min_length=12) is False
    assert validate_password_strength("Abc123!XyZ123", min_length=12) is True
