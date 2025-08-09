"""Main AI service with modular architecture."""

import uuid
from collections.abc import AsyncGenerator
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.ai.providers.base import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from app.services.ai.providers.factory import AIProviderFactory
from app.services.ai.utils.cost_tracker import CostTracker
from app.services.ai.utils.rag_service import RAGService
from app.services.ai.utils.tool_manager import ToolManager
from sqlalchemy.orm import Session


class AIService:
    """Main AI service with modular architecture."""

    def __init__(self, db: Session):
        self.db = db
        self.cost_tracker = CostTracker(db)
        self.rag_service = RAGService(db)
        self.tool_manager = ToolManager(db)
        self._providers: Dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize AI providers."""
        try:
            # Initialize OpenAI provider
            if settings.openai_api_key:
                self._providers["openai"] = AIProviderFactory.create_provider(
                    "openai",
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                )

            # Initialize Anthropic provider
            if settings.anthropic_api_key:
                self._providers["anthropic"] = AIProviderFactory.create_provider(
                    "anthropic",
                    api_key=settings.anthropic_api_key,
                    base_url=settings.anthropic_base_url,
                )

        except Exception as e:
            print(f"Failed to initialize providers: {str(e)}")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self._providers.keys())

    def get_provider(self, provider_name: str):
        """Get a specific provider."""
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        return self._providers[provider_name]

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
        **kwargs,
    ) -> ChatCompletionResponse:
        """Generate chat completion."""
        try:
            # Get provider
            ai_provider = self.get_provider(provider)

            # Convert messages to ChatMessage objects
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]

            # Apply RAG if enabled
            if use_knowledge_base and messages:
                last_user_message = next(
                    (
                        msg["content"]
                        for msg in reversed(messages)
                        if msg["role"] == "user"
                    ),
                    None,
                )
                if last_user_message:
                    rag_messages = await self.rag_service.create_rag_prompt(
                        last_user_message,
                        user_id,
                        max_context_chunks=max_context_chunks,
                    )
                    chat_messages = rag_messages

            # Add tools information if enabled
            if use_tools:
                tools_prompt = self.tool_manager.format_tools_for_prompt()
                if tools_prompt:
                    # Add tools information to system message
                    if chat_messages and chat_messages[0].role == "system":
                        chat_messages[0].content += f"\n\n{tools_prompt}"
                    else:
                        chat_messages.insert(
                            0,
                            ChatMessage(
                                role="system",
                                content=f"You have access to the following tools:\n\n{tools_prompt}",
                            ),
                        )

            # Create request
            request = ChatCompletionRequest(
                messages=chat_messages,
                model=model or self._get_default_model(provider),
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Generate response
            response = await ai_provider.chat_completion(request)

            # Track cost
            if response.usage:
                cost = ai_provider.get_cost_estimate(
                    request.model,
                    response.usage.get("input_tokens", 0),
                    response.usage.get("output_tokens", 0),
                )

                await self.cost_tracker.track_cost(
                    user_id=user_id,
                    provider=provider,
                    model=request.model,
                    input_tokens=response.usage.get("input_tokens", 0),
                    output_tokens=response.usage.get("output_tokens", 0),
                    cost=cost,
                    request_id=str(uuid.uuid4()),
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
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate streaming chat completion."""
        try:
            # Get provider
            ai_provider = self.get_provider(provider)

            # Convert messages to ChatMessage objects
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]

            # Apply RAG if enabled
            if use_knowledge_base and messages:
                last_user_message = next(
                    (
                        msg["content"]
                        for msg in reversed(messages)
                        if msg["role"] == "user"
                    ),
                    None,
                )
                if last_user_message:
                    rag_messages = await self.rag_service.create_rag_prompt(
                        last_user_message,
                        user_id,
                        max_context_chunks=max_context_chunks,
                    )
                    chat_messages = rag_messages

            # Add tools information if enabled
            if use_tools:
                tools_prompt = self.tool_manager.format_tools_for_prompt()
                if tools_prompt:
                    if chat_messages and chat_messages[0].role == "system":
                        chat_messages[0].content += f"\n\n{tools_prompt}"
                    else:
                        chat_messages.insert(
                            0,
                            ChatMessage(
                                role="system",
                                content=f"You have access to the following tools:\n\n{tools_prompt}",
                            ),
                        )

            # Create request
            request = ChatCompletionRequest(
                messages=chat_messages,
                model=model or self._get_default_model(provider),
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )

            # Generate streaming response
            full_content = ""
            async for chunk in ai_provider.chat_completion_stream(request):
                full_content += chunk.content
                yield chunk

            # Track cost (approximate for streaming)
            if full_content:
                # Estimate tokens (rough approximation)
                estimated_tokens = len(full_content.split()) * 1.3
                cost = ai_provider.get_cost_estimate(
                    request.model, estimated_tokens, estimated_tokens
                )

                await self.cost_tracker.track_cost(
                    user_id=user_id,
                    provider=provider,
                    model=request.model,
                    input_tokens=int(estimated_tokens),
                    output_tokens=int(estimated_tokens),
                    cost=cost,
                    request_id=str(uuid.uuid4()),
                )

        except Exception as e:
            raise Exception(f"Streaming chat completion failed: {str(e)}")

    async def get_embeddings(
        self,
        texts: List[str],
        provider: str = "openai",
        model: str = "text-embedding-ada-002",
    ) -> List[List[float]]:
        """Generate embeddings."""
        try:
            ai_provider = self.get_provider(provider)
            return await ai_provider.get_embeddings(texts, model)

        except Exception as e:
            raise Exception(f"Embeddings generation failed: {str(e)}")

    async def execute_tools(
        self, ai_response: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tools based on AI response."""
        return await self.tool_manager.execute_tools_from_response(ai_response, user_id)

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

    def get_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, float]:
        """Get cost summary for a user."""
        return self.cost_tracker.get_cost_summary(user_id, days)

    def get_daily_costs(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        return self.cost_tracker.get_daily_costs(user_id, days)

    def get_model_usage_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get model usage statistics."""
        return self.cost_tracker.get_model_usage_stats(user_id, days)

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        default_models = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-sonnet-20240229",
        }
        return default_models.get(provider, "gpt-3.5-turbo")
