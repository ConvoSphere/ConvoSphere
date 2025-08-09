"""Response Handler for AI Service."""

import uuid
from typing import Any, Dict, List, Optional

from ..types.ai_types import (
    ChatResponse,
    ChatStreamResponse,
    EmbeddingResponse,
)


class ResponseHandler:
    """Handles AI service responses and error processing."""

    def __init__(self):
        self._request_id = None

    def set_request_id(self, request_id: str) -> None:
        """Set the current request ID."""
        self._request_id = request_id

    def create_chat_response(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
    ) -> ChatResponse:
        """Create a chat completion response."""
        return ChatResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason,
            request_id=self._request_id or str(uuid.uuid4()),
        )

    def create_stream_response(
        self,
        content: str,
        model: str,
        finish_reason: Optional[str] = None,
    ) -> ChatStreamResponse:
        """Create a streaming chat completion response."""
        return ChatStreamResponse(
            content=content,
            model=model,
            finish_reason=finish_reason,
            request_id=self._request_id or str(uuid.uuid4()),
        )

    def create_embedding_response(
        self,
        embeddings: List[List[float]],
        model: str,
        usage: Optional[Dict[str, int]] = None,
    ) -> EmbeddingResponse:
        """Create an embedding response."""
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage=usage,
        )

    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle provider-specific errors."""
        error_message = str(error)
        
        # Common provider error patterns
        if "rate limit" in error_message.lower():
            return Exception(f"Rate limit exceeded for {provider}. Please try again later.")
        
        if "quota" in error_message.lower():
            return Exception(f"Quota exceeded for {provider}. Please check your account limits.")
        
        if "invalid api key" in error_message.lower():
            return Exception(f"Invalid API key for {provider}. Please check your configuration.")
        
        if "model not found" in error_message.lower():
            return Exception(f"Model not found for {provider}. Please check the model name.")
        
        if "context length" in error_message.lower():
            return Exception(f"Context length exceeded for {provider}. Please reduce the input size.")
        
        # Generic error handling
        return Exception(f"Error with {provider}: {error_message}")

    def handle_validation_error(self, error: Exception) -> Exception:
        """Handle validation errors."""
        error_message = str(error)
        
        if "messages cannot be empty" in error_message:
            return Exception("Chat messages cannot be empty.")
        
        if "invalid role" in error_message:
            return Exception("Invalid message role. Must be 'system', 'user', or 'assistant'.")
        
        if "temperature must be between" in error_message:
            return Exception("Temperature must be between 0 and 2.")
        
        if "max tokens must be positive" in error_message:
            return Exception("Max tokens must be a positive number.")
        
        if "unsupported provider" in error_message:
            return Exception("Unsupported AI provider. Please use 'openai' or 'anthropic'.")
        
        return Exception(f"Validation error: {error_message}")

    def handle_streaming_error(self, error: Exception) -> Exception:
        """Handle streaming-specific errors."""
        error_message = str(error)
        
        if "connection" in error_message.lower():
            return Exception("Streaming connection failed. Please try again.")
        
        if "timeout" in error_message.lower():
            return Exception("Streaming request timed out. Please try again.")
        
        return Exception(f"Streaming error: {error_message}")

    def validate_response_content(self, content: str) -> bool:
        """Validate response content."""
        if not content:
            return False
        
        if not isinstance(content, str):
            return False
        
        # Check for reasonable content length
        if len(content) > 100000:  # 100KB limit
            return False
        
        return True

    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """Validate embedding response."""
        if not embeddings:
            return False
        
        if not isinstance(embeddings, list):
            return False
        
        for embedding in embeddings:
            if not isinstance(embedding, list):
                return False
            
            if not all(isinstance(dim, (int, float)) for dim in embedding):
                return False
        
        return True

    def extract_usage_info(self, response: Any) -> Optional[Dict[str, int]]:
        """Extract usage information from provider response."""
        if hasattr(response, 'usage'):
            return response.usage
        
        if hasattr(response, 'model_dump') and callable(response.model_dump):
            data = response.model_dump()
            return data.get('usage')
        
        if isinstance(response, dict):
            return response.get('usage')
        
        return None

    def extract_finish_reason(self, response: Any) -> Optional[str]:
        """Extract finish reason from provider response."""
        if hasattr(response, 'finish_reason'):
            return response.finish_reason
        
        if hasattr(response, 'model_dump') and callable(response.model_dump):
            data = response.model_dump()
            return data.get('finish_reason')
        
        if isinstance(response, dict):
            return response.get('finish_reason')
        
        return None

    def log_response_metrics(
        self,
        response: ChatResponse,
        processing_time: float,
        provider: str,
    ) -> None:
        """Log response metrics for monitoring."""
        # This would integrate with your logging system
        metrics = {
            "request_id": response.request_id,
            "provider": provider,
            "model": response.model,
            "content_length": len(response.content),
            "processing_time": processing_time,
            "usage": response.usage,
        }
        
        # TODO: Integrate with your logging/monitoring system
        print(f"Response metrics: {metrics}")  # Placeholder