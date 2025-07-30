"""
Integration tests for ConversationService.

This module provides integration testing of the ConversationService class,
focusing on database interactions and real service behavior.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.conversation_service import ConversationService


class TestConversationServiceIntegration:
    """Integration tests for ConversationService."""

    @pytest.fixture
    def conversation_service(self):
        """Create ConversationService instance."""
        return ConversationService()

    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data for testing."""
        return {
            "id": str(uuid.uuid4()),
            "title": "Test Conversation",
            "user_id": str(uuid.uuid4()),
            "assistant_id": str(uuid.uuid4()),
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.conversations
    def test_create_conversation(self, conversation_service, sample_conversation_data):
        """Test successful conversation creation."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            mock_db.query.return_value.filter.return_value.first.return_value = None

            result = conversation_service.create_conversation(
                title=sample_conversation_data["title"],
                user_id=sample_conversation_data["user_id"],
                assistant_id=sample_conversation_data["assistant_id"],
            )

            assert result is not None
            assert result.title == sample_conversation_data["title"]

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.conversations
    def test_get_conversation_by_id(
        self,
        conversation_service,
        sample_conversation_data,
    ):
        """Test getting conversation by ID."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_conversation_data
            )

            result = conversation_service.get_conversation_by_id(
                sample_conversation_data["id"]
            )

            assert result == sample_conversation_data

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.conversations
    def test_get_conversations_by_user(self, conversation_service):
        """Test getting conversations by user ID."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_query = MagicMock()
            mock_query.filter.return_value.order_by.return_value.all.return_value = []
            mock_db.query.return_value = mock_query

            user_id = str(uuid.uuid4())
            result = conversation_service.get_conversations_by_user(user_id)

            assert result == []

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.conversations
    def test_add_message_to_conversation(self, conversation_service):
        """Test adding message to conversation."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            conversation_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            content = "Hello, this is a test message"
            role = "user"

            result = conversation_service.add_message_to_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                content=content,
                role=role,
            )

            assert result is not None
            assert result.content == content
            assert result.role == role

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.conversations
    def test_get_messages_by_conversation(self, conversation_service):
        """Test getting messages by conversation ID."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_query = MagicMock()
            mock_query.filter.return_value.order_by.return_value.all.return_value = []
            mock_db.query.return_value = mock_query

            conversation_id = str(uuid.uuid4())
            result = conversation_service.get_messages_by_conversation(conversation_id)

            assert result == []