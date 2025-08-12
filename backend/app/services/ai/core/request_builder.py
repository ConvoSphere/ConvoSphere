"""Request Builder for AI Service."""

import uuid
from typing import Any, Dict, List, Optional

from ..types.ai_types import (
    ChatConfig,
    ChatRequest,
    EmbeddingRequest,
    ProviderType,
)


class RequestBuilder:
    """Builds and validates AI service requests."""

    def __init__(self):
        self._default_models = {
            ProviderType.OPENAI: "gpt-3.5-turbo",
            ProviderType.ANTHROPIC: "claude-3-sonnet-20240229",
        }

    def build_chat_request(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_knowledge_base: bool = True,
        use_tools: bool = True,
        max_context_chunks: int = 5,
        **kwargs: Any,
    ) -> ChatRequest:
        """Build a chat completion request."""
        # Validate inputs
        self._validate_messages(messages)
        self._validate_user_id(user_id)
        self._validate_provider(provider)
        self._validate_temperature(temperature)
        self._validate_max_tokens(max_tokens)

        # Create configuration
        config = ChatConfig(
            temperature=temperature,
            max_tokens=max_tokens,
            use_knowledge_base=use_knowledge_base,
            use_tools=use_tools,
            max_context_chunks=max_context_chunks,
            **kwargs,
        )

        # Get default model if not specified
        if not model:
            model = self._get_default_model(provider)

        return ChatRequest(
            messages=messages,
            user_id=user_id,
            provider=provider,
            model=model,
            config=config,
        )

    def build_embedding_request(
        self,
        texts: List[str],
        provider: str = "openai",
        model: str = "text-embedding-ada-002",
    ) -> EmbeddingRequest:
        """Build an embedding request."""
        # Validate inputs
        self._validate_texts(texts)
        self._validate_provider(provider)
        self._validate_embedding_model(model)

        return EmbeddingRequest(
            texts=texts,
            provider=provider,
            model=model,
        )

    def _validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """Validate chat messages."""
        if not messages:
            raise ValueError("Messages cannot be empty")

        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"Message {i} must be a dictionary")

            if "role" not in message:
                raise ValueError(f"Message {i} must have a 'role' field")

            if "content" not in message:
                raise ValueError(f"Message {i} must have a 'content' field")

            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid role '{message['role']}' in message {i}")

            if not isinstance(message["content"], str):
                raise ValueError(f"Content in message {i} must be a string")

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID."""
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")

    def _validate_provider(self, provider: str) -> None:
        """Validate provider."""
        if provider not in [p.value for p in ProviderType]:
            raise ValueError(f"Unsupported provider: {provider}")

    def _validate_temperature(self, temperature: float) -> None:
        """Validate temperature."""
        if not isinstance(temperature, (int, float)):
            raise ValueError("Temperature must be a number")

        if temperature < 0 or temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

    def _validate_max_tokens(self, max_tokens: Optional[int]) -> None:
        """Validate max tokens."""
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                raise ValueError("Max tokens must be an integer")

            if max_tokens <= 0:
                raise ValueError("Max tokens must be positive")

    def _validate_texts(self, texts: List[str]) -> None:
        """Validate texts for embeddings."""
        if not texts:
            raise ValueError("Texts cannot be empty")

        for i, text in enumerate(texts):
            if not isinstance(text, str):
                raise ValueError(f"Text {i} must be a string")

            if not text.strip():
                raise ValueError(f"Text {i} cannot be empty")

    def _validate_embedding_model(self, model: str) -> None:
        """Validate embedding model."""
        if not model or not isinstance(model, str):
            raise ValueError("Model must be a non-empty string")

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        provider_enum = ProviderType(provider)
        return self._default_models.get(provider_enum, "gpt-3.5-turbo")

    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())
