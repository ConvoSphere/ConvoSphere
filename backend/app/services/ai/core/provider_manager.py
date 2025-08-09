"""
Provider Manager for AI Service.

This module manages AI providers using the existing provider factory
and integrates them with the new modular architecture.
"""

import os
from typing import Any, Dict, List, Optional

from ..providers.factory import AIProviderFactory
from ..providers.base import BaseAIProvider
from ..types.ai_types import ProviderType, ModelType, ProviderConfig


class ProviderManager:
    """Manages AI providers for the modular AI service."""

    def __init__(self):
        """Initialize the provider manager."""
        self._providers: Dict[str, BaseAIProvider] = {}
        self._provider_configs: Dict[str, ProviderConfig] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available providers with their configurations."""
        try:
            # Initialize OpenAI provider
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                openai_config = ProviderConfig(
                    provider_type=ProviderType.OPENAI,
                    api_key=openai_api_key,
                    base_url=os.getenv("OPENAI_BASE_URL"),
                    default_model="gpt-3.5-turbo",
                    available_models=[
                        "gpt-3.5-turbo",
                        "gpt-3.5-turbo-16k",
                        "gpt-4",
                        "gpt-4-turbo",
                        "gpt-4o",
                        "text-embedding-ada-002",
                        "text-embedding-3-small",
                        "text-embedding-3-large",
                    ],
                )
                self._provider_configs["openai"] = openai_config

            # Initialize Anthropic provider
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_api_key:
                anthropic_config = ProviderConfig(
                    provider_type=ProviderType.ANTHROPIC,
                    api_key=anthropic_api_key,
                    base_url=os.getenv("ANTHROPIC_BASE_URL"),
                    default_model="claude-3-sonnet-20240229",
                    available_models=[
                        "claude-3-haiku-20240307",
                        "claude-3-sonnet-20240229",
                        "claude-3-opus-20240229",
                        "claude-3-5-sonnet-20241022",
                        "claude-3-5-haiku-20241022",
                    ],
                )
                self._provider_configs["anthropic"] = anthropic_config

        except Exception as e:
            print(f"Failed to initialize providers: {str(e)}")

    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get a provider instance, creating it if necessary."""
        if provider_name not in self._provider_configs:
            return None

        if provider_name not in self._providers:
            config = self._provider_configs[provider_name]
            try:
                provider = AIProviderFactory.create_provider(
                    provider_name=provider_name,
                    api_key=config.api_key,
                    base_url=config.base_url,
                )
                self._providers[provider_name] = provider
            except Exception as e:
                print(f"Failed to create provider {provider_name}: {str(e)}")
                return None

        return self._providers[provider_name]

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self._provider_configs.keys())

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available."""
        return provider_name in self._provider_configs

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get provider configuration."""
        return self._provider_configs.get(provider_name)

    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider."""
        config = self._provider_configs.get(provider_name)
        if config:
            return config.available_models
        return []

    def get_default_model(self, provider_name: str) -> Optional[str]:
        """Get default model for a provider."""
        config = self._provider_configs.get(provider_name)
        if config:
            return config.default_model
        return None

    def get_model_info(self, provider_name: str, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        config = self._provider_configs.get(provider_name)
        if not config:
            return {}

        # Check if model is available for this provider
        if model not in config.available_models:
            return {}

        # Return model information
        model_info = {
            "name": model,
            "provider": provider_name,
            "provider_type": config.provider_type.value,
        }

        # Add provider-specific model information
        if provider_name == "openai":
            model_info.update(self._get_openai_model_info(model))
        elif provider_name == "anthropic":
            model_info.update(self._get_anthropic_model_info(model))

        return model_info

    def _get_openai_model_info(self, model: str) -> Dict[str, Any]:
        """Get OpenAI-specific model information."""
        model_info = {
            "max_tokens": 4096,
            "cost_per_1k_input": 0.0015,
            "cost_per_1k_output": 0.002,
        }

        if model.startswith("gpt-4"):
            model_info.update({
                "max_tokens": 8192,
                "cost_per_1k_input": 0.03,
                "cost_per_1k_output": 0.06,
            })
        elif model.startswith("gpt-3.5-turbo-16k"):
            model_info.update({
                "max_tokens": 16384,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.004,
            })
        elif model.startswith("text-embedding"):
            model_info.update({
                "max_tokens": 8192,
                "cost_per_1k_input": 0.0001,
                "cost_per_1k_output": 0.0,
            })

        return model_info

    def _get_anthropic_model_info(self, model: str) -> Dict[str, Any]:
        """Get Anthropic-specific model information."""
        model_info = {
            "max_tokens": 4096,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
        }

        if model.startswith("claude-3-opus"):
            model_info.update({
                "max_tokens": 200000,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
            })
        elif model.startswith("claude-3-sonnet"):
            model_info.update({
                "max_tokens": 200000,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
            })
        elif model.startswith("claude-3-haiku"):
            model_info.update({
                "max_tokens": 200000,
                "cost_per_1k_input": 0.00025,
                "cost_per_1k_output": 0.00125,
            })

        return model_info

    def validate_provider_and_model(self, provider_name: str, model: str) -> bool:
        """Validate if provider and model combination is valid."""
        if not self.is_provider_available(provider_name):
            return False

        available_models = self.get_available_models(provider_name)
        return model in available_models

    def get_cost_estimate(
        self, provider_name: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for token usage."""
        model_info = self.get_model_info(provider_name, model)
        if not model_info:
            return 0.0

        input_cost = (input_tokens / 1000) * model_info.get("cost_per_1k_input", 0.0)
        output_cost = (output_tokens / 1000) * model_info.get("cost_per_1k_output", 0.0)

        return input_cost + output_cost

    def register_provider(
        self, name: str, provider_class: type, config: ProviderConfig
    ) -> None:
        """Register a new provider."""
        try:
            AIProviderFactory.register_provider(name, provider_class)
            self._provider_configs[name] = config
        except Exception as e:
            print(f"Failed to register provider {name}: {str(e)}")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        for provider_name in self.get_available_providers():
            config = self._provider_configs[provider_name]
            provider_instance = self.get_provider(provider_name)
            
            status[provider_name] = {
                "available": provider_instance is not None,
                "config": {
                    "provider_type": config.provider_type.value,
                    "default_model": config.default_model,
                    "available_models": config.available_models,
                },
                "initialized": provider_name in self._providers,
            }
        
        return status