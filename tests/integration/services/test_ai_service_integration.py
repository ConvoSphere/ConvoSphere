"""
Integration tests for AIService.

This module provides integration testing of the AIService class,
focusing on AI model interactions and real service behavior.
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.ai_service import AIService


class TestAIServiceIntegration:
    """Integration tests for AIService."""

    @pytest.fixture
    def ai_service(self):
        """Create AIService instance."""
        return AIService()

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.ai
    def test_generate_response(self, ai_service):
        """Test generating AI response."""
        with patch.object(ai_service, "openai_client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Hello! How can I help you?"
            mock_client.chat.completions.create.return_value = mock_response

            messages = [{"role": "user", "content": "Hello"}]
            result = ai_service.generate_response(messages)

            assert result is not None
            assert "Hello! How can I help you?" in result

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.ai
    def test_generate_response_with_tools(self, ai_service):
        """Test generating AI response with tools."""
        with patch.object(ai_service, "openai_client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "I'll help you with that."
            mock_response.choices[0].message.tool_calls = [
                MagicMock(
                    id="call_123",
                    function=MagicMock(name="test_tool", arguments='{"param": "value"}'),
                )
            ]
            mock_client.chat.completions.create.return_value = mock_response

            messages = [{"role": "user", "content": "Use the test tool"}]
            tools = [{"type": "function", "function": {"name": "test_tool"}}]

            result = ai_service.generate_response_with_tools(messages, tools)

            assert result is not None
            assert "I'll help you with that." in result

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.ai
    def test_embed_text(self, ai_service):
        """Test text embedding."""
        with patch.object(ai_service, "openai_client") as mock_client:
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            mock_client.embeddings.create.return_value = mock_response

            text = "This is a test text for embedding"
            result = ai_service.embed_text(text)

            assert result is not None
            assert len(result) == 3
            assert result[0] == 0.1

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.ai
    def test_chat_completion(self, ai_service):
        """Test chat completion."""
        with patch.object(ai_service, "openai_client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Chat response"
            mock_client.chat.completions.create.return_value = mock_response

            messages = [{"role": "user", "content": "Hello"}]
            result = ai_service.chat_completion(messages)

            assert result is not None
            assert "Chat response" in result