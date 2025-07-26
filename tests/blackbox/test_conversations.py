"""
Blackbox tests for conversation management endpoints.

This module tests all conversation-related API endpoints including
CRUD operations, message management, and conversation features.
"""

import pytest

from backend.appconftest import TEST_CONVERSATION_DATA, TEST_MESSAGE_DATA


class TestConversationManagementEndpoints:
    """Test conversation management endpoints."""

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_conversation_success(
        self, api_client, assertion_helper, test_assistant
    ):
        """Test successful conversation creation."""
        assistant_id = test_assistant["id"]

        conversation_data = TEST_CONVERSATION_DATA.copy()
        conversation_data["assistant_id"] = assistant_id
        conversation_data["title"] = "Test Conversation Blackbox"

        response = api_client.post("/conversations/", data=conversation_data)

        assertion_helper.assert_success_response(response, 201)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "title", "assistant_id", "user_id", "created_at", "updated_at"],
        )

        # Verify conversation data
        conversation = response.json()
        assert conversation["title"] == conversation_data["title"]
        assert conversation["assistant_id"] == assistant_id

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_conversation_invalid_data(self, api_client, assertion_helper):
        """Test conversation creation with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "assistant_id": 999999,  # Non-existent assistant
        }

        response = api_client.post("/conversations/", data=invalid_data)
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_conversation_unauthorized(self, api_client, assertion_helper):
        """Test conversation creation without authentication."""
        conversation_data = TEST_CONVERSATION_DATA.copy()

        response = api_client.post("/conversations/", data=conversation_data)
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversations_list(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting list of conversations."""
        token, user_data = authenticated_user

        response = api_client.get("/conversations/", user_type="regular_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(), ["conversations", "total", "page", "size"]
        )
        assertion_helper.assert_list_response(response.json()["conversations"])

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversations_list_with_filters(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting conversations list with filters."""
        token, user_data = authenticated_user

        # Test with pagination
        response = api_client.get(
            "/conversations/", params={"page": 1, "size": 10}, user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 200)

        # Test with search
        response = api_client.get(
            "/conversations/", params={"search": "test"}, user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 200)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversation_by_id(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test getting conversation by ID."""
        conversation_id = test_conversation["id"]

        response = api_client.get(f"/conversations/{conversation_id}")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "title", "assistant_id", "user_id", "created_at", "updated_at"],
        )
        assert response.json()["id"] == conversation_id

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversation_by_id_not_found(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting non-existent conversation by ID."""
        token, user_data = authenticated_user

        response = api_client.get("/conversations/999999", user_type="regular_user")
        assertion_helper.assert_not_found(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_update_conversation(self, api_client, assertion_helper, test_conversation):
        """Test updating conversation."""
        conversation_id = test_conversation["id"]

        update_data = {"title": "Updated Conversation Title"}

        response = api_client.put(f"/conversations/{conversation_id}", data=update_data)

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "title", "assistant_id", "user_id", "created_at", "updated_at"],
        )

        # Verify updates
        updated_conversation = response.json()
        assert updated_conversation["title"] == update_data["title"]

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_delete_conversation(
        self, api_client, assertion_helper, authenticated_user, test_assistant
    ):
        """Test deleting conversation."""
        token, user_data = authenticated_user

        # First create a conversation to delete
        conversation_data = TEST_CONVERSATION_DATA.copy()
        conversation_data["assistant_id"] = test_assistant["id"]
        conversation_data["title"] = "Conversation to Delete"

        create_response = api_client.post(
            "/conversations/", data=conversation_data, user_type="regular_user"
        )
        conversation_id = create_response.json()["id"]

        # Delete the conversation
        response = api_client.delete(
            f"/conversations/{conversation_id}", user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 204)

        # Verify conversation is deleted
        get_response = api_client.get(
            f"/conversations/{conversation_id}", user_type="regular_user"
        )
        assertion_helper.assert_not_found(get_response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_archive_conversation(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test archiving conversation."""
        conversation_id = test_conversation["id"]

        response = api_client.post(f"/conversations/{conversation_id}/archive")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(), ["id", "title", "archived", "archived_at"]
        )
        assert response.json()["archived"] is True


class TestMessageManagement:
    """Test message management within conversations."""

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_success(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test successful message creation."""
        conversation_id = test_conversation["id"]

        message_data = TEST_MESSAGE_DATA.copy()
        message_data["conversation_id"] = conversation_id
        message_data["content"] = "Hello, this is a test message from blackbox tests"

        response = api_client.post(
            f"/conversations/{conversation_id}/messages", data=message_data
        )

        assertion_helper.assert_success_response(response, 201)
        assertion_helper.assert_response_structure(
            response.json(), ["id", "content", "role", "conversation_id", "created_at"]
        )

        # Verify message data
        message = response.json()
        assert message["content"] == message_data["content"]
        assert message["role"] == message_data["role"]
        assert message["conversation_id"] == conversation_id

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_invalid_data(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test message creation with invalid data."""
        conversation_id = test_conversation["id"]

        invalid_data = {
            "content": "",  # Empty content
            "role": "invalid_role",  # Invalid role
        }

        response = api_client.post(
            f"/conversations/{conversation_id}/messages", data=invalid_data
        )
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_conversation_not_found(self, api_client, assertion_helper):
        """Test message creation in non-existent conversation."""
        message_data = TEST_MESSAGE_DATA.copy()
        message_data["conversation_id"] = 999999

        response = api_client.post("/conversations/999999/messages", data=message_data)
        assertion_helper.assert_not_found(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversation_messages(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test getting messages from conversation."""
        conversation_id = test_conversation["id"]

        # First create a message
        message_data = TEST_MESSAGE_DATA.copy()
        message_data["conversation_id"] = conversation_id
        api_client.post(f"/conversations/{conversation_id}/messages", data=message_data)

        # Get messages
        response = api_client.get(f"/conversations/{conversation_id}/messages")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response, 1)  # At least one message

        # Verify message structure
        messages = response.json()
        if messages:
            assertion_helper.assert_response_structure(
                messages[0], ["id", "content", "role", "conversation_id", "created_at"]
            )

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversation_messages_with_pagination(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test getting messages with pagination."""
        conversation_id = test_conversation["id"]

        response = api_client.get(
            f"/conversations/{conversation_id}/messages", params={"page": 1, "size": 10}
        )

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_conversation_messages_not_found(self, api_client, assertion_helper):
        """Test getting messages from non-existent conversation."""
        response = api_client.get("/conversations/999999/messages")
        assertion_helper.assert_not_found(response)


class TestChatEndpoints:
    """Test chat-specific endpoints."""

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_chat_conversations(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting chat conversations."""
        token, user_data = authenticated_user

        response = api_client.get("/chat/conversations", user_type="regular_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_chat_conversation_messages(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test getting messages from chat conversation."""
        conversation_id = test_conversation["id"]

        # First create a message
        message_data = TEST_MESSAGE_DATA.copy()
        message_data["conversation_id"] = conversation_id
        api_client.post(f"/conversations/{conversation_id}/messages", data=message_data)

        # Get messages via chat endpoint
        response = api_client.get(f"/chat/conversations/{conversation_id}/messages")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_get_chat_conversation_messages_not_found(
        self, api_client, assertion_helper
    ):
        """Test getting messages from non-existent chat conversation."""
        response = api_client.get("/chat/conversations/999999/messages")
        assertion_helper.assert_not_found(response)


class TestConversationValidation:
    """Test conversation data validation."""

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_conversation_missing_required_fields(
        self, api_client, assertion_helper
    ):
        """Test creating conversation with missing required fields."""
        # Missing title
        invalid_data = {"assistant_id": 1}

        response = api_client.post("/conversations/", data=invalid_data)
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_conversation_invalid_assistant_id(
        self, api_client, assertion_helper
    ):
        """Test creating conversation with invalid assistant ID."""
        invalid_data = TEST_CONVERSATION_DATA.copy()
        invalid_data["assistant_id"] = -1  # Invalid assistant ID

        response = api_client.post("/conversations/", data=invalid_data)
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_update_conversation_invalid_data(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test updating conversation with invalid data."""
        conversation_id = test_conversation["id"]

        invalid_data = {
            "title": ""  # Empty title
        }

        response = api_client.put(
            f"/conversations/{conversation_id}", data=invalid_data
        )
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_missing_content(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test creating message with missing content."""
        conversation_id = test_conversation["id"]

        invalid_data = {
            "role": "user"
            # Missing content
        }

        response = api_client.post(
            f"/conversations/{conversation_id}/messages", data=invalid_data
        )
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_invalid_role(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test creating message with invalid role."""
        conversation_id = test_conversation["id"]

        invalid_data = {"content": "Test message", "role": "invalid_role"}

        response = api_client.post(
            f"/conversations/{conversation_id}/messages", data=invalid_data
        )
        assertion_helper.assert_error_response(response, 422)


class TestConversationPermissions:
    """Test conversation access permissions."""

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_access_conversation_unauthorized(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test accessing conversation without authentication."""
        conversation_id = test_conversation["id"]

        response = api_client.get(f"/conversations/{conversation_id}")
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_create_message_unauthorized(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test creating message without authentication."""
        conversation_id = test_conversation["id"]

        message_data = TEST_MESSAGE_DATA.copy()
        message_data["conversation_id"] = conversation_id

        response = api_client.post(
            f"/conversations/{conversation_id}/messages", data=message_data
        )
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_update_conversation_unauthorized(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test updating conversation without authentication."""
        conversation_id = test_conversation["id"]

        update_data = {"title": "Unauthorized Update"}

        response = api_client.put(f"/conversations/{conversation_id}", data=update_data)
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.conversations
    def test_delete_conversation_unauthorized(
        self, api_client, assertion_helper, test_conversation
    ):
        """Test deleting conversation without authentication."""
        conversation_id = test_conversation["id"]

        response = api_client.delete(f"/conversations/{conversation_id}")
        assertion_helper.assert_unauthorized(response)
