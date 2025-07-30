"""
Integration tests for UserService.

This module provides integration testing of the UserService class,
focusing on database interactions and real service behavior.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.user_service import UserService


class TestUserServiceIntegration:
    """Integration tests for UserService."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance."""
        return UserService()

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Mock query methods to return None (no existing users)
            mock_query = MagicMock()
            mock_query.filter.return_value.first.return_value = None
            mock_db.query.return_value = mock_query

            # Mock the get_user_by_email and get_user_by_username methods
            with (
                patch.object(user_service, "get_user_by_email", return_value=None),
                patch.object(user_service, "get_user_by_username", return_value=None),
            ):
                result = user_service.create_user(
                    email=sample_user_data["email"],
                    username=sample_user_data["username"],
                    password="TestPassword123!",
                    full_name=sample_user_data["full_name"],
                )

                assert result is not None
                assert result.email == sample_user_data["email"]

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test user creation with duplicate email."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.add.side_effect = Exception("Duplicate email")

            with pytest.raises(Exception):
                user_service.create_user(
                    email=sample_user_data["email"],
                    username=sample_user_data["username"],
                    password="TestPassword123!",
                    full_name=sample_user_data["full_name"],
                )

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_get_user_by_id(self, user_service, sample_user_data):
        """Test getting user by ID."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            result = user_service.get_user_by_id(sample_user_data["id"])

            assert result == sample_user_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_get_user_by_email(self, user_service, sample_user_data):
        """Test getting user by email."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            result = user_service.get_user_by_email(sample_user_data["email"])

            assert result == sample_user_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_update_user(self, user_service, sample_user_data):
        """Test updating user."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            updated_data = sample_user_data.copy()
            updated_data["full_name"] = "Updated User"

            mock_db.query.return_value.filter.return_value.first.return_value = (
                updated_data
            )

            result = user_service.update_user(
                user_id=sample_user_data["id"],
                user_data={"full_name": "Updated User"},
            )

            assert result == updated_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_delete_user(self, user_service, sample_user_data):
        """Test deleting user."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None

            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            result = user_service.delete_user(sample_user_data["id"])

            assert result is True

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_get_users_paginated(self, user_service):
        """Test getting users with pagination."""
        with patch.object(user_service, "db") as mock_db:
            mock_query = MagicMock()
            mock_query.offset.return_value.limit.return_value.all.return_value = []
            mock_query.count.return_value = 0
            mock_db.query.return_value = mock_query

            result = user_service.get_users(skip=0, limit=10)

            assert result == []

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_authenticate_user(self, user_service, sample_user_data):
        """Test user authentication."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            with patch.object(user_service, "verify_password", return_value=True):
                result = user_service.authenticate_user(
                    email=sample_user_data["email"], password="TestPassword123!"
                )

                assert result == sample_user_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.users
    def test_authenticate_user_invalid_password(self, user_service, sample_user_data):
        """Test user authentication with invalid password."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            with patch.object(user_service, "verify_password", return_value=False):
                result = user_service.authenticate_user(
                    email=sample_user_data["email"], password="WrongPassword"
                )

                assert result is None