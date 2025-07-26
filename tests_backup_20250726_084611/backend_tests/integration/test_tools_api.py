#!/usr/bin/env python3
"""
Simple test script to validate the Tools API implementation.
This script tests the ToolService and API endpoints without starting the full application.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))


def test_tool_service():
    """Test the ToolService implementation."""

    try:
        # Test imports
        from app.models.tool import Tool, ToolCategory

        # Test ToolCategory enum
        [cat.value for cat in ToolCategory]

        # Test Tool model
        Tool(
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.CUSTOM,
            function_name="test_function",
        )

        # Test ToolService methods (without database)

        return True

    except Exception:
        return False


def test_api_endpoints():
    """Test the API endpoints implementation."""

    try:
        # Test imports
        from app.api.v1.endpoints.tools import (
            ToolCreate,
            ToolUpdate,
        )

        # Test Pydantic models
        ToolCreate(
            name="Test API Tool",
            description="A tool created via API",
            category="custom",
            function_name="test_api_function",
        )

        ToolUpdate(
            description="Updated description",
        )

        return True

    except Exception:
        return False


def test_permissions():
    """Test permission checking logic."""

    try:
        from app.models.user import User, UserRole

        # Test user model
        user = User(
            username="testuser",
            email="test@example.com",
            role=UserRole.USER,
        )

        # Test permission checking
        user.has_permission("tool:read")

        return True

    except Exception:
        return False


def main():
    """Run all tests."""

    tests = [
        ("ToolService", test_tool_service),
        ("API Endpoints", test_api_endpoints),
        ("Permissions", test_permissions),
    ]

    passed = 0
    total = len(tests)

    for _test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            pass

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
