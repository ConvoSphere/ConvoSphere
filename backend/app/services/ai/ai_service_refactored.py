"""Refactored AI Service with modular architecture."""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from .core import ChatProcessor, RequestBuilder, ResponseHandler
from .middleware import RAGMiddleware, ToolMiddleware, CostMiddleware
from .types.ai_types import (
    ChatResponse,
    ChatStreamResponse,
    EmbeddingResponse,
)


class AIService:
    """Refactored AI service with modular architecture."""

    def __init__(self, db: Session):
        self.db = db
        
        # Initialize core components
        self.request_builder = RequestBuilder()
        self.response_handler = ResponseHandler()
        self.chat_processor = ChatProcessor(self.request_builder, self.response_handler)
        
        # Initialize middleware
        self.rag_middleware = RAGMiddleware()
        self.tool_middleware = ToolMiddleware()
        self.cost_middleware = CostMiddleware()
        
        # Initialize providers (to be integrated)
        self._providers: Dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize AI providers."""
        try:
            # TODO: Integrate with existing provider factory
            # This will use the existing provider factory from the original service
            pass
        except Exception as e:
            print(f"Failed to initialize providers: {str(e)}")

    async def chat_completion(
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
        """Generate chat completion using modular architecture."""
        try:
            # Process with middleware
            processed_messages = await self._apply_middleware(
                messages, user_id, use_knowledge_base, use_tools, max_context_chunks
            )
            
            # Use chat processor for core logic
            response = await self.chat_processor.process_chat_completion(
                messages=processed_messages,
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
            
            return response

        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")

    async def chat_completion_stream(
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
        """Generate streaming chat completion using modular architecture."""
        try:
            # Process with middleware
            processed_messages = await self._apply_middleware(
                messages, user_id, use_knowledge_base, use_tools, max_context_chunks
            )
            
            # Use chat processor for core logic
            async for response in self.chat_processor.process_chat_completion_stream(
                messages=processed_messages,
                user_id=user_id,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_knowledge_base=use_knowledge_base,
                use_tools=use_tools,
                max_context_chunks=max_context_chunks,
                **kwargs,
            ):
                yield response

        except Exception as e:
            raise Exception(f"Streaming chat completion failed: {str(e)}")

    async def get_embeddings(
        self,
        texts: List[str],
        provider: str = "openai",
        model: str = "text-embedding-ada-002",
    ) -> EmbeddingResponse:
        """Generate embeddings using modular architecture."""
        try:
            response = await self.chat_processor.process_embeddings(
                texts=texts,
                provider=provider,
                model=model,
            )
            
            return response

        except Exception as e:
            raise Exception(f"Embeddings generation failed: {str(e)}")

    async def execute_tools(
        self, ai_response: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tools based on AI response."""
        return await self.tool_middleware.execute_tools_from_response(ai_response, user_id)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return self.chat_processor.get_available_providers()

    def get_provider(self, provider_name: str):
        """Get a specific provider."""
        return self.chat_processor.get_provider(provider_name)

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a provider."""
        return self.chat_processor.get_available_models(provider)

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return self.chat_processor.get_model_info(provider, model)

    def get_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, float]:
        """Get cost summary for a user."""
        return self.cost_middleware.get_cost_summary(user_id, days)

    def get_daily_costs(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        return self.cost_middleware.get_daily_costs(user_id, days)

    def get_model_usage_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get model usage statistics."""
        return self.cost_middleware.get_model_usage_stats(user_id, days)

    async def _apply_middleware(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        use_knowledge_base: bool,
        use_tools: bool,
        max_context_chunks: int,
    ) -> List[Dict[str, str]]:
        """Apply all middleware processing to messages."""
        processed_messages = messages.copy()

        # Apply RAG middleware
        if self.rag_middleware.should_apply_rag(messages, use_knowledge_base):
            processed_messages = await self.rag_middleware.process(
                processed_messages, user_id, max_context_chunks
            )

        # Apply Tool middleware
        if self.tool_middleware.should_apply_tools(processed_messages, use_tools):
            processed_messages = await self.tool_middleware.process(
                processed_messages, use_tools
            )

        return processed_messages

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        return self.request_builder._get_default_model(provider)