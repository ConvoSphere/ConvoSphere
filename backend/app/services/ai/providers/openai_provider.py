"""OpenAI provider implementation."""

from collections.abc import AsyncGenerator
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .base import (
    BaseAIProvider,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
)


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Generate chat completion using OpenAI."""
        try:
            # Convert messages to OpenAI format
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    **({"name": msg.name} if msg.name else {}),
                }
                for msg in request.messages
            ]

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
            response = await self.client.chat.completions.create(**params)

            # Extract response
            content = response.choices[0].message.content or ""
            usage = response.usage.dict() if response.usage else None
            finish_reason = response.choices[0].finish_reason

            return ChatCompletionResponse(
                content=content,
                model=request.model,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate streaming chat completion using OpenAI."""
        try:
            # Convert messages to OpenAI format
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    **({"name": msg.name} if msg.name else {}),
                }
                for msg in request.messages
            ]

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
            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield ChatCompletionChunk(
                        content=chunk.choices[0].delta.content,
                        finish_reason=chunk.choices[0].finish_reason,
                    )
                elif chunk.choices[0].finish_reason:
                    yield ChatCompletionChunk(
                        content="", finish_reason=chunk.choices[0].finish_reason
                    )

        except Exception as e:
            raise Exception(f"OpenAI streaming API error: {str(e)}")

    async def get_embeddings(
        self, texts: List[str], model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """Generate embeddings using OpenAI."""
        try:
            embeddings = []

            for text in texts:
                response = await self.client.embeddings.create(model=model, input=text)
                embeddings.append(response.data[0].embedding)

            return embeddings

        except Exception as e:
            raise Exception(f"OpenAI embeddings API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about OpenAI model."""
        model_info = {
            "gpt-4": {
                "max_tokens": 8192,
                "cost_per_1k_input": 0.03,
                "cost_per_1k_output": 0.06,
            },
            "gpt-4-turbo": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03,
            },
            "gpt-4-turbo-preview": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03,
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "cost_per_1k_input": 0.0015,
                "cost_per_1k_output": 0.002,
            },
            "gpt-3.5-turbo-16k": {
                "max_tokens": 16384,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.004,
            },
        }

        return model_info.get(model, {})

    def get_cost_estimate(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for OpenAI token usage."""
        model_info = self.get_model_info(model)

        if not model_info:
            return 0.0

        input_cost = (input_tokens / 1000) * model_info.get("cost_per_1k_input", 0)
        output_cost = (output_tokens / 1000) * model_info.get("cost_per_1k_output", 0)

        return input_cost + output_cost
