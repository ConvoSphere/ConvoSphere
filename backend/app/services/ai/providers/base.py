"""Base AI provider class."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ChatMessage:
    """Chat message structure."""

    role: str
    content: str
    name: Optional[str] = None


@dataclass
class ChatCompletionRequest:
    """Chat completion request structure."""

    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


@dataclass
class ChatCompletionResponse:
    """Chat completion response structure."""

    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionChunk:
    """Chat completion chunk for streaming."""

    content: str
    finish_reason: Optional[str] = None


class BaseAIProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the provider client."""

    @abstractmethod
    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Generate chat completion."""

    @abstractmethod
    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate streaming chat completion."""

    @abstractmethod
    async def get_embeddings(
        self, texts: List[str], model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """Generate embeddings for texts."""

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""

    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""

    def validate_model(self, model: str) -> bool:
        """Validate if model is available."""
        available_models = self.get_available_models()
        return model in available_models

    def get_cost_estimate(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for token usage."""
        # Default implementation - should be overridden by providers
        return 0.0
