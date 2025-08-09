"""AI Service Type Definitions."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ProviderType(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelType(str, Enum):
    """Model types."""
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE = "image"


@dataclass
class ProviderConfig:
    """Provider configuration."""
    name: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass
class ChatConfig:
    """Chat configuration."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    use_knowledge_base: bool = True
    use_tools: bool = True
    max_context_chunks: int = 5


@dataclass
class ChatRequest:
    """Chat completion request."""
    messages: List[Dict[str, str]]
    user_id: str
    provider: str = "openai"
    model: Optional[str] = None
    config: Optional[ChatConfig] = None
    **kwargs: Any


@dataclass
class ChatResponse:
    """Chat completion response."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ChatStreamResponse:
    """Streaming chat completion response."""
    content: str
    model: str
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class EmbeddingRequest:
    """Embedding request."""
    texts: List[str]
    provider: str = "openai"
    model: str = "text-embedding-ada-002"


@dataclass
class EmbeddingResponse:
    """Embedding response."""
    embeddings: List[List[float]]
    model: str
    usage: Optional[Dict[str, int]] = None


@dataclass
class ModelInfo:
    """Model information."""
    name: str
    provider: str
    type: ModelType
    max_tokens: Optional[int] = None
    cost_per_1k_input: Optional[float] = None
    cost_per_1k_output: Optional[float] = None
    capabilities: List[str] = None


@dataclass
class CostInfo:
    """Cost information."""
    input_tokens: int
    output_tokens: int
    cost: float
    model: str
    provider: str


@dataclass
class RAGContext:
    """RAG context information."""
    query: str
    chunks: List[Dict[str, Any]]
    relevance_scores: List[float]
    sources: List[str]


@dataclass
class ToolInfo:
    """Tool information."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: bool = False


@dataclass
class ToolCall:
    """Tool call information."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None


# Type aliases for backward compatibility
ChatMessage = Dict[str, str]
ChatCompletionRequest = ChatRequest
ChatCompletionResponse = ChatResponse
ChatCompletionChunk = ChatStreamResponse