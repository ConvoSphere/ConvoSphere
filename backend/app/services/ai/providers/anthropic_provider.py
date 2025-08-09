"""Anthropic provider implementation."""

from collections.abc import AsyncGenerator
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

from .base import (
    BaseAIProvider,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
)


class AnthropicProvider(BaseAIProvider):
    """Anthropic provider implementation."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)

    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        self.client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Generate chat completion using Anthropic."""
        try:
            # Convert messages to Anthropic format
            messages = []
            for msg in request.messages:
                if msg.role == "system":
                    # Anthropic doesn't support system messages in the same way
                    # We'll prepend system content to the first user message
                    continue
                if msg.role == "user":
                    messages.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    messages.append({"role": "assistant", "content": msg.content})

            # Prepare request parameters
            params = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
            }

            if request.max_tokens:
                params["max_tokens"] = request.max_tokens

            # Add additional parameters
            for key, value in request.__dict__.items():
                if key not in [
                    "messages",
                    "model",
                    "temperature",
                    "max_tokens",
                    "stream",
                ]:
                    params[key] = value

            # Make API call
            response = await self.client.messages.create(**params)

            # Extract response
            content = response.content[0].text if response.content else ""
            usage = (
                {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
                if response.usage
                else None
            )
            finish_reason = response.stop_reason

            return ChatCompletionResponse(
                content=content,
                model=request.model,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate streaming chat completion using Anthropic."""
        try:
            # Convert messages to Anthropic format
            messages = []
            for msg in request.messages:
                if msg.role == "system":
                    continue
                elif msg.role == "user":
                    messages.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    messages.append({"role": "assistant", "content": msg.content})

            # Prepare request parameters
            params = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
                "stream": True,
            }

            if request.max_tokens:
                params["max_tokens"] = request.max_tokens

            # Add additional parameters
            for key, value in request.__dict__.items():
                if key not in [
                    "messages",
                    "model",
                    "temperature",
                    "max_tokens",
                    "stream",
                ]:
                    params[key] = value

            # Make streaming API call
            stream = await self.client.messages.create(**params)

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield ChatCompletionChunk(
                        content=chunk.delta.text, finish_reason=None
                    )
                elif chunk.type == "message_delta":
                    if chunk.delta.stop_reason:
                        yield ChatCompletionChunk(
                            content="", finish_reason=chunk.delta.stop_reason
                        )

        except Exception as e:
            raise Exception(f"Anthropic streaming API error: {str(e)}")

    async def get_embeddings(
        self, texts: List[str], model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """Generate embeddings using Anthropic."""
        try:
            embeddings = []

            for text in texts:
                response = await self.client.embeddings.create(model=model, input=text)
                embeddings.append(response.embedding)

            return embeddings

        except Exception as e:
            raise Exception(f"Anthropic embeddings API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about Anthropic model."""
        model_info = {
            "claude-3-opus-20240229": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.00025,
                "cost_per_1k_output": 0.00125,
            },
            "claude-2.1": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.008,
                "cost_per_1k_output": 0.024,
            },
            "claude-2.0": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.008,
                "cost_per_1k_output": 0.024,
            },
            "claude-instant-1.2": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.00163,
                "cost_per_1k_output": 0.00551,
            },
        }

        return model_info.get(model, {})

    def get_cost_estimate(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for Anthropic token usage."""
        model_info = self.get_model_info(model)

        if not model_info:
            return 0.0

        input_cost = (input_tokens / 1000) * model_info.get("cost_per_1k_input", 0)
        output_cost = (output_tokens / 1000) * model_info.get("cost_per_1k_output", 0)

        return input_cost + output_cost
