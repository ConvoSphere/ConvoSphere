"""
Response Handler for AI Service.

This module handles the processing of AI service responses and
provides centralized error handling and logging.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from ..types.ai_types import ChatResponse, ChatStreamResponse, EmbeddingResponse

# Configure logging
logger = logging.getLogger(__name__)


class ResponseHandler:
    """Handles AI service response processing and error handling."""

    def __init__(self):
        """Initialize the response handler."""
        self._request_id: Optional[str] = None

    def set_request_id(self, request_id: str) -> None:
        """Set the request ID for tracking."""
        self._request_id = request_id

    def create_chat_response(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
    ) -> ChatResponse:
        """Create a chat response."""
        return ChatResponse(
            content=content,
            model=model,
            usage=usage or {},
            finish_reason=finish_reason,
        )

    def create_stream_response(
        self,
        content: str,
        model: str,
        finish_reason: Optional[str] = None,
    ) -> ChatStreamResponse:
        """Create a streaming response."""
        return ChatStreamResponse(
            content=content,
            model=model,
            finish_reason=finish_reason,
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
            usage=usage or {},
        )

    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle provider-specific errors."""
        error_message = f"Provider '{provider}' error: {str(error)}"
        logger.error(f"Request {self._request_id}: {error_message}")
        
        # Log additional context for monitoring
        self._log_error_metrics("provider_error", provider, str(error))
        
        return Exception(error_message)

    def handle_validation_error(self, error: Exception) -> Exception:
        """Handle validation errors."""
        error_message = f"Validation error: {str(error)}"
        logger.error(f"Request {self._request_id}: {error_message}")
        
        # Log additional context for monitoring
        self._log_error_metrics("validation_error", "validation", str(error))
        
        return error

    def handle_streaming_error(self, error: Exception) -> Exception:
        """Handle streaming-specific errors."""
        error_message = f"Streaming error: {str(error)}"
        logger.error(f"Request {self._request_id}: {error_message}")
        
        # Log additional context for monitoring
        self._log_error_metrics("streaming_error", "streaming", str(error))
        
        return Exception(error_message)

    def validate_response_content(self, content: str) -> bool:
        """Validate response content."""
        if not content or not content.strip():
            return False
        
        # Check for reasonable content length (100KB limit)
        if len(content) > 100000:
            return False
        
        return True

    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """Validate embeddings."""
        if not embeddings:
            return False
        
        # Check that all items are lists of floats
        for embedding in embeddings:
            if not isinstance(embedding, list):
                return False
            if not all(isinstance(x, (int, float)) for x in embedding):
                return False
        
        return True

    def extract_usage_info(self, response: Any) -> Dict[str, int]:
        """Extract usage information from response."""
        if hasattr(response, 'usage'):
            return response.usage or {}
        
        if hasattr(response, 'model_dump') and callable(response.model_dump):
            data = response.model_dump()
            return data.get('usage', {})
        
        if isinstance(response, dict):
            return response.get('usage', {})
        
        return {}

    def extract_finish_reason(self, response: Any) -> Optional[str]:
        """Extract finish reason from response."""
        if hasattr(response, 'finish_reason'):
            return response.finish_reason
        
        if hasattr(response, 'model_dump') and callable(response.model_dump):
            data = response.model_dump()
            return data.get('finish_reason')
        
        if isinstance(response, dict):
            return response.get('finish_reason')
        
        return None

    def log_response_metrics(
        self, response: ChatResponse, processing_time: float, provider: str
    ) -> None:
        """Log response metrics for monitoring."""
        metrics = {
            "request_id": self._request_id,
            "provider": provider,
            "model": response.model,
            "processing_time": processing_time,
            "content_length": len(response.content),
            "usage": response.usage,
            "finish_reason": response.finish_reason,
            "timestamp": time.time(),
        }
        
        logger.info(f"Response metrics: {metrics}")
        self._log_metrics("response", metrics)

    def log_streaming_metrics(self, processing_time: float, provider: str) -> None:
        """Log streaming metrics for monitoring."""
        metrics = {
            "request_id": self._request_id,
            "provider": provider,
            "processing_time": processing_time,
            "timestamp": time.time(),
        }
        
        logger.info(f"Streaming metrics: {metrics}")
        self._log_metrics("streaming", metrics)

    def log_embedding_metrics(
        self, response: EmbeddingResponse, processing_time: float, provider: str
    ) -> None:
        """Log embedding metrics for monitoring."""
        metrics = {
            "request_id": self._request_id,
            "provider": provider,
            "model": response.model,
            "processing_time": processing_time,
            "embeddings_count": len(response.embeddings),
            "embedding_dimensions": len(response.embeddings[0]) if response.embeddings else 0,
            "usage": response.usage,
            "timestamp": time.time(),
        }
        
        logger.info(f"Embedding metrics: {metrics}")
        self._log_metrics("embedding", metrics)

    def _log_metrics(self, metric_type: str, metrics: Dict[str, Any]) -> None:
        """Log metrics to monitoring system."""
        try:
            # Integration with monitoring system (e.g., Prometheus, DataDog, etc.)
            # This is a placeholder for actual monitoring integration
            
            # Example: Send to monitoring system
            # monitoring_client.record_metric(metric_type, metrics)
            
            # For now, just log to structured logging
            logger.info(f"Monitoring metric - {metric_type}: {metrics}")
            
        except Exception as e:
            logger.warning(f"Failed to log metrics: {str(e)}")

    def _log_error_metrics(self, error_type: str, context: str, error_message: str) -> None:
        """Log error metrics for monitoring."""
        try:
            error_metrics = {
                "request_id": self._request_id,
                "error_type": error_type,
                "context": context,
                "error_message": error_message,
                "timestamp": time.time(),
            }
            
            # Integration with error monitoring system (e.g., Sentry, Rollbar, etc.)
            # This is a placeholder for actual error monitoring integration
            
            # Example: Send to error monitoring system
            # error_monitoring_client.capture_exception(error_metrics)
            
            # For now, just log to structured logging
            logger.error(f"Error monitoring - {error_type}: {error_metrics}")
            
        except Exception as e:
            logger.warning(f"Failed to log error metrics: {str(e)}")