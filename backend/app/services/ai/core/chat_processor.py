"""Chat Processor for AI Service."""

import time
from typing import Any, Dict, List, Optional

from .provider_manager import ProviderManager
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
        self.provider_manager = ProviderManager()

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
            # Validate provider and model
            if not self.provider_manager.is_provider_available(provider):
                raise ValueError(f"Provider '{provider}' is not available")

            # Get default model if not specified
            if not model:
                model = self.provider_manager.get_default_model(provider)
                if not model:
                    raise ValueError(f"No default model available for provider '{provider}'")

            # Validate model
            if not self.provider_manager.validate_provider_and_model(provider, model):
                raise ValueError(f"Model '{model}' is not available for provider '{provider}'")

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

            # Get provider and generate response
            ai_provider = self.provider_manager.get_provider(provider)
            if not ai_provider:
                raise Exception(f"Failed to get provider instance for '{provider}'")

            # Convert messages to provider format
            provider_messages = self._convert_messages_to_provider_format(messages)
            
            # Create provider request
            from ..providers.base import ChatCompletionRequest
            provider_request = ChatCompletionRequest(
                messages=provider_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            # Get response from provider
            provider_response = await ai_provider.chat_completion(provider_request)

            # Extract response data
            content = provider_response.content
            usage = provider_response.usage or {}
            finish_reason = provider_response.finish_reason

            # Validate response
            if not self.response_handler.validate_response_content(content):
                raise Exception("Invalid response content received")

            # Create response
            response = self.response_handler.create_chat_response(
                content=content,
                model=model,
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
            # Validate provider and model
            if not self.provider_manager.is_provider_available(provider):
                raise ValueError(f"Provider '{provider}' is not available")

            # Get default model if not specified
            if not model:
                model = self.provider_manager.get_default_model(provider)
                if not model:
                    raise ValueError(f"No default model available for provider '{provider}'")

            # Validate model
            if not self.provider_manager.validate_provider_and_model(provider, model):
                raise ValueError(f"Model '{model}' is not available for provider '{provider}'")

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

            # Get provider and generate response
            ai_provider = self.provider_manager.get_provider(provider)
            if not ai_provider:
                raise Exception(f"Failed to get provider instance for '{provider}'")

            # Convert messages to provider format
            provider_messages = self._convert_messages_to_provider_format(messages)
            
            # Create provider request
            from ..providers.base import ChatCompletionRequest
            provider_request = ChatCompletionRequest(
                messages=provider_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            # Stream response from provider
            async for chunk in ai_provider.chat_completion_stream(provider_request):
                # Create streaming response
                response = self.response_handler.create_stream_response(
                    content=chunk.content,
                    model=model,
                    finish_reason=chunk.finish_reason,
                )
                
                yield response

            # Log metrics
            processing_time = time.time() - start_time
            self.response_handler.log_streaming_metrics(processing_time, provider)

        except Exception as e:
            # Handle different types of errors
            if "validation" in str(e).lower():
                raise self.response_handler.handle_validation_error(e)
            else:
                raise self.response_handler.handle_provider_error(e, provider)

    async def process_embeddings(
        self,
        texts: List[str],
        provider: str = "openai",
        model: str = "text-embedding-ada-002",
    ) -> EmbeddingResponse:
        """Process an embeddings request."""
        start_time = time.time()
        
        try:
            # Validate provider and model
            if not self.provider_manager.is_provider_available(provider):
                raise ValueError(f"Provider '{provider}' is not available")

            # Validate model
            if not self.provider_manager.validate_provider_and_model(provider, model):
                raise ValueError(f"Model '{model}' is not available for provider '{provider}'")

            # Build request
            request = self.request_builder.build_embedding_request(
                texts=texts,
                provider=provider,
                model=model,
            )

            # Set request ID for tracking
            request_id = self.request_builder.generate_request_id()
            self.response_handler.set_request_id(request_id)

            # Get provider and generate embeddings
            ai_provider = self.provider_manager.get_provider(provider)
            if not ai_provider:
                raise Exception(f"Failed to get provider instance for '{provider}'")

            # Get embeddings from provider
            embeddings = await ai_provider.get_embeddings(texts, model)

            # Create response
            response = self.response_handler.create_embedding_response(
                embeddings=embeddings,
                model=model,
                usage={"input_tokens": len(texts) * 10},  # Rough estimate
            )

            # Log metrics
            processing_time = time.time() - start_time
            self.response_handler.log_embedding_metrics(response, processing_time, provider)

            return response

        except Exception as e:
            # Handle different types of errors
            if "validation" in str(e).lower():
                raise self.response_handler.handle_validation_error(e)
            else:
                raise self.response_handler.handle_provider_error(e, provider)

    def _convert_messages_to_provider_format(self, messages: List[Dict[str, str]]) -> List:
        """Convert messages to provider format."""
        from ..providers.base import ChatMessage
        
        provider_messages = []
        for msg in messages:
            provider_messages.append(ChatMessage(
                role=msg["role"],
                content=msg["content"],
                name=msg.get("name"),
            ))
        
        return provider_messages

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return self.provider_manager.get_available_providers()

    def get_provider(self, provider_name: str):
        """Get a specific provider."""
        return self.provider_manager.get_provider(provider_name)

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a provider."""
        return self.provider_manager.get_available_models(provider)

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return self.provider_manager.get_model_info(provider, model)

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return self.provider_manager.get_provider_status()