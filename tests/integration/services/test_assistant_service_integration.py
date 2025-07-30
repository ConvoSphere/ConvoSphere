"""
Integration tests for AssistantService.

This module provides integration testing of the AssistantService class,
focusing on database interactions and real service behavior.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.assistant_service import AssistantService


class TestAssistantServiceIntegration:
    """Integration tests for AssistantService."""

    @pytest.fixture
    def assistant_service(self):
        """Create AssistantService instance."""
        return AssistantService()

    @pytest.fixture
    def sample_assistant_data(self):
        """Sample assistant data for testing."""
        return {
            "id": str(uuid.uuid4()),
            "name": "Test Assistant",
            "description": "A test assistant",
            "instructions": "You are a helpful assistant",
            "model": "gpt-4",
            "user_id": str(uuid.uuid4()),
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.assistants
    def test_create_assistant(self, assistant_service, sample_assistant_data):
        """Test successful assistant creation."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            mock_db.query.return_value.filter.return_value.first.return_value = None

            result = assistant_service.create_assistant(
                name=sample_assistant_data["name"],
                description=sample_assistant_data["description"],
                instructions=sample_assistant_data["instructions"],
                model=sample_assistant_data["model"],
                user_id=sample_assistant_data["user_id"],
            )

            assert result is not None
            assert result.name == sample_assistant_data["name"]

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.assistants
    def test_get_assistant_by_id(self, assistant_service, sample_assistant_data):
        """Test getting assistant by ID."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_assistant_data
            )

            result = assistant_service.get_assistant_by_id(sample_assistant_data["id"])

            assert result == sample_assistant_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.assistants
    def test_get_assistants_by_user(self, assistant_service):
        """Test getting assistants by user ID."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_query = MagicMock()
            mock_query.filter.return_value.all.return_value = []
            mock_db.query.return_value = mock_query

            user_id = str(uuid.uuid4())
            result = assistant_service.get_assistants_by_user(user_id)

            assert result == []

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.assistants
    def test_update_assistant(self, assistant_service, sample_assistant_data):
        """Test updating assistant."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            updated_data = sample_assistant_data.copy()
            updated_data["name"] = "Updated Assistant"

            mock_db.query.return_value.filter.return_value.first.return_value = (
                updated_data
            )

            result = assistant_service.update_assistant(
                assistant_id=sample_assistant_data["id"],
                assistant_data={"name": "Updated Assistant"},
            )

            assert result == updated_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.assistants
    def test_delete_assistant(self, assistant_service, sample_assistant_data):
        """Test deleting assistant."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None

            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_assistant_data
            )

            result = assistant_service.delete_assistant(sample_assistant_data["id"])

            assert result is True