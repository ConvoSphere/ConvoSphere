"""Chat Processor for AI Service."""

import time
from typing import Any, Dict, List, Optional

from ..types.ai_types import (
    ChatRequest,
    ChatResponse,
    ChatStreamResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)


class ChatProcessor:
    """Core chat processing logic for AI service."""

    def __init__(self, request_builder, response_handler):
        self.request_builder = request_builder
        self.response_handler = response_handler

    async def process_chat_completion(
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
    ) -> ChatResponse:
        """Process a chat completion request."""
        start_time = time.time()
        
        try:
            # Build request
            request = self.request_builder.build_chat_request(
                messages=messages,
                user_id=user_id,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_knowledge_base=use_knowledge_base,
                use_tools=use_tools,
                max_context_chunks=max_context_chunks,
                **kwargs,
            )

            # Set request ID for tracking
            request_id = self.request_builder.generate_request_id()
            self.response_handler.set_request_id(request_id)

            # Process with middleware (to be implemented)
            processed_messages = await self._apply_middleware(request)
            
            # Get provider and generate response
            ai_provider = self._get_provider(provider)
            provider_response = await ai_provider.chat_completion(processed_messages)

            # Extract response data
            content = self._extract_content(provider_response)
            usage = self.response_handler.extract_usage_info(provider_response)
            finish_reason = self.response_handler.extract_finish_reason(provider_response)

            # Validate response
            if not self.response_handler.validate_response_content(content):
                raise Exception("Invalid response content received")

            # Create response
            response = self.response_handler.create_chat_response(
                content=content,
                model=request.model,
                usage=usage,
                finish_reason=finish_reason,
            )

            # Log metrics
            processing_time = time.time() - start_time
            self.response_handler.log_response_metrics(response, processing_time, provider)

            return response

        except Exception as e:
            # Handle different types of errors
            if "validation" in str(e).lower():
                raise self.response_handler.handle_validation_error(e)
            else:
                raise self.response_handler.handle_provider_error(e, provider)

    async def process_chat_completion_stream(
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
    ):
        """Process a streaming chat completion request."""
        start_time = time.time()
        
        try:
            # Build request
            request = self.request_builder.build_chat_request(
                messages=messages,
                user_id=user_id,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_knowledge_base=use_knowledge_base,
                use_tools=use_tools,
                max_context_chunks=max_context_chunks,
                **kwargs,
            )

            # Set request ID for tracking
            request_id = self.request_builder.generate_request_id()
            self.response_handler.set_request_id(request_id)

            # Process with middleware (to be implemented)
            processed_messages = await self._apply_middleware(request)
            
            # Get provider and generate streaming response
            ai_provider = self._get_provider(provider)
            
            full_content = ""
            async for chunk in ai_provider.chat_completion_stream(processed_messages):
                # Extract chunk content
                chunk_content = self._extract_content(chunk)
                full_content += chunk_content
                
                # Create stream response
                stream_response = self.response_handler.create_stream_response(
                    content=chunk_content,
                    model=request.model,
                )
                
                yield stream_response

            # Log metrics for streaming
            processing_time = time.time() - start_time
            # TODO: Implement streaming metrics logging

        except Exception as e:
            # Handle streaming-specific errors
            raise self.response_handler.handle_streaming_error(e)

    async def process_embeddings(
        self,
        texts: List[str],
        provider: str = "openai",
        model: str = "text-embedding-ada-002",
    ) -> EmbeddingResponse:
        """Process an embedding request."""
        try:
            # Build request
            request = self.request_builder.build_embedding_request(
                texts=texts,
                provider=provider,
                model=model,
            )

            # Get provider and generate embeddings
            ai_provider = self._get_provider(provider)
            embeddings = await ai_provider.get_embeddings(texts, model)

            # Validate embeddings
            if not self.response_handler.validate_embeddings(embeddings):
                raise Exception("Invalid embeddings received")

            # Create response
            response = self.response_handler.create_embedding_response(
                embeddings=embeddings,
                model=model,
            )

            return response

        except Exception as e:
            raise self.response_handler.handle_provider_error(e, provider)

    async def _apply_middleware(self, request: ChatRequest) -> List[Dict[str, str]]:
        """Apply middleware processing to messages."""
        # TODO: Implement middleware processing
        # This will integrate with RAG, Tools, and Cost middleware
        return request.messages

    def _get_provider(self, provider_name: str):
        """Get AI provider instance."""
        # TODO: Implement provider factory integration
        # This will use the existing provider factory
        raise NotImplementedError("Provider integration to be implemented")

    def _extract_content(self, response: Any) -> str:
        """Extract content from provider response."""
        if hasattr(response, 'content'):
            return response.content
        
        if hasattr(response, 'model_dump') and callable(response.model_dump):
            data = response.model_dump()
            return data.get('content', '')
        
        if isinstance(response, dict):
            return response.get('content', '')
        
        return str(response)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        # TODO: Implement provider discovery
        return ["openai", "anthropic"]

    def get_provider(self, provider_name: str):
        """Get a specific provider."""
        if provider_name not in self.get_available_providers():
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return self._get_provider(provider_name)

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a provider."""
        try:
            ai_provider = self.get_provider(provider)
            return ai_provider.get_available_models()
        except Exception as e:
            print(f"Failed to get models for {provider}: {str(e)}")
            return []

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            ai_provider = self.get_provider(provider)
            return ai_provider.get_model_info(model)
        except Exception as e:
            print(f"Failed to get model info: {str(e)}")
            return {}