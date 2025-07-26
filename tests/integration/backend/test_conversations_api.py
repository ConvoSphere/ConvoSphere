#!/usr/bin/env python3
"""
Test script for Conversations API with enterprise features.

This script tests the comprehensive Conversations API including:
- Conversation CRUD operations
- Message management
- Archiving and status management
- Pagination and filtering
- Enterprise features (participants, groups, access control)
"""

import uuid
from datetime import datetime
from typing import Any

import requests


class ConversationsAPITester:
    """Test class for Conversations API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.conversations_endpoint = f"{self.api_base}/conversations"
        self.auth_token = None

    def set_auth_token(self, token: str):
        """Set authentication token for API requests."""
        self.auth_token = token

    def get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def test_create_conversation(self) -> dict[str, Any]:
        """Test creating a new conversation."""

        conversation_data = {
            "title": f"Test Conversation {uuid.uuid4().hex[:8]}",
            "description": "Test conversation for API testing",
            "user_id": str(uuid.uuid4()),  # Mock user ID
            "assistant_id": str(uuid.uuid4()),  # Mock assistant ID
            "tags": ["test", "api"],
            "access": "private",
            "conversation_metadata": {
                "test_metadata": "value",
                "created_by": "api_test",
            },
        }

        try:
            response = requests.post(
                f"{self.conversations_endpoint}/",
                json=conversation_data,
                headers=self.get_headers(),
            )

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_list_conversations(self) -> dict[str, Any]:
        """Test listing conversations with pagination."""

        try:
            response = requests.get(
                f"{self.conversations_endpoint}/",
                params={
                    "page": 1,
                    "size": 10,
                },
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Test getting a specific conversation."""

        try:
            response = requests.get(
                f"{self.conversations_endpoint}/{conversation_id}",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_update_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Test updating a conversation."""

        update_data = {
            "title": "Updated Test Conversation",
            "description": "Updated description for testing",
            "tags": ["updated", "test", "api"],
            "access": "team",
            "conversation_metadata": {
                "updated_metadata": "new_value",
                "updated_at": datetime.utcnow().isoformat(),
            },
        }

        try:
            response = requests.put(
                f"{self.conversations_endpoint}/{conversation_id}",
                json=update_data,
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_add_message(self, conversation_id: str) -> dict[str, Any]:
        """Test adding a message to a conversation."""

        message_data = {
            "content": "Hello, this is a test message from the API!",
            "role": "user",
            "message_type": "text",
            "message_metadata": {
                "test_message": True,
                "created_by": "api_test",
            },
        }

        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers(),
            )

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_add_assistant_message(self, conversation_id: str) -> dict[str, Any]:
        """Test adding an assistant message to a conversation."""

        message_data = {
            "content": "Hello! I'm an AI assistant. How can I help you today?",
            "role": "assistant",
            "message_type": "text",
            "tokens_used": 15,
            "model_used": "gpt-3.5-turbo",
            "message_metadata": {
                "assistant_response": True,
                "model_version": "3.5-turbo",
            },
        }

        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers(),
            )

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_add_tool_message(self, conversation_id: str) -> dict[str, Any]:
        """Test adding a tool message to a conversation."""

        message_data = {
            "content": "Tool execution completed successfully",
            "role": "tool",
            "message_type": "text",
            "tool_name": "search_tool",
            "tool_input": {"query": "test search"},
            "tool_output": {"results": ["result1", "result2"]},
            "message_metadata": {
                "tool_execution": True,
                "execution_time": 1.5,
            },
        }

        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers(),
            )

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_list_messages(self, conversation_id: str) -> dict[str, Any]:
        """Test listing messages in a conversation."""

        try:
            response = requests.get(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception:
            return []

    def test_archive_conversation(self, conversation_id: str) -> bool:
        """Test archiving a conversation."""

        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/archive",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                response.json()
                return True
            return False

        except Exception:
            return False

    def test_delete_conversation(self, conversation_id: str) -> bool:
        """Test deleting a conversation."""

        try:
            response = requests.delete(
                f"{self.conversations_endpoint}/{conversation_id}",
                headers=self.get_headers(),
            )

            return response.status_code == 204

        except Exception:
            return False

    def run_all_tests(self):
        """Run all tests for the Conversations API."""

        # Test conversation creation
        conversation = self.test_create_conversation()
        if not conversation:
            return

        conversation_id = conversation["id"]

        # Test listing conversations
        self.test_list_conversations()

        # Test getting specific conversation
        self.test_get_conversation(conversation_id)

        # Test updating conversation
        self.test_update_conversation(conversation_id)

        # Test adding messages
        self.test_add_message(conversation_id)
        self.test_add_assistant_message(conversation_id)
        self.test_add_tool_message(conversation_id)

        # Test listing messages
        self.test_list_messages(conversation_id)

        # Test archiving conversation
        self.test_archive_conversation(conversation_id)

        # Test getting archived conversation
        self.test_get_conversation(conversation_id)

        # Test deleting conversation
        self.test_delete_conversation(conversation_id)


def main():
    """Main function to run the tests."""
    # Initialize tester
    tester = ConversationsAPITester()

    # Set authentication token if available
    # tester.set_auth_token("your-auth-token-here")

    # Run all tests
    tester.run_all_tests()


if __name__ == "__main__":
    main()
