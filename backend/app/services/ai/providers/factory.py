"""AI Provider Factory."""

from typing import Dict, Type
from .base import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider


class AIProviderFactory:
    """Factory for creating AI providers."""
    
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseAIProvider]) -> None:
        """Register a new provider."""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str,
        base_url: str = None
    ) -> BaseAIProvider:
        """Create a provider instance."""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key, base_url=base_url)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers."""
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """Check if provider is available."""
        return provider_name in cls._providers