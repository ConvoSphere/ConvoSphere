"""
Unit tests for AI Provider Manager.

This module tests the ProviderManager component that integrates
the existing provider factory with the new modular architecture.
"""

import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from backend.app.services.ai.core.provider_manager import ProviderManager
from backend.app.services.ai.types.ai_types import ProviderType, ProviderConfig


class TestProviderManager:
    """Test class for ProviderManager."""

    @pytest.fixture
    def provider_manager(self):
        """Create a ProviderManager instance."""
        return ProviderManager()

    @pytest.fixture
    def mock_openai_config(self):
        """Mock OpenAI provider configuration."""
        return ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-openai-key",
            base_url="https://api.openai.com/v1",
            default_model="gpt-3.5-turbo",
            available_models=[
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo",
                "text-embedding-ada-002",
            ],
        )

    @pytest.fixture
    def mock_anthropic_config(self):
        """Mock Anthropic provider configuration."""
        return ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="test-anthropic-key",
            base_url="https://api.anthropic.com",
            default_model="claude-3-sonnet-20240229",
            available_models=[
                "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229",
                "claude-3-opus-20240229",
            ],
        )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_manager_initialization(self, provider_manager):
        """Test ProviderManager initialization."""
        assert provider_manager._providers == {}
        assert provider_manager._provider_configs == {}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key"
    })
    def test_initialize_providers_with_env_vars(self):
        """Test provider initialization with environment variables."""
        provider_manager = ProviderManager()
        
        # Check that providers were initialized
        assert "openai" in provider_manager._provider_configs
        assert "anthropic" in provider_manager._provider_configs
        
        openai_config = provider_manager._provider_configs["openai"]
        assert openai_config.provider_type == ProviderType.OPENAI
        assert openai_config.api_key == "test-openai-key"
        assert "gpt-3.5-turbo" in openai_config.available_models

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @patch.dict(os.environ, {}, clear=True)
    def test_initialize_providers_without_env_vars(self):
        """Test provider initialization without environment variables."""
        provider_manager = ProviderManager()
        
        # Should not have any providers without API keys
        assert len(provider_manager._provider_configs) == 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_provider_not_configured(self, provider_manager):
        """Test getting a provider that is not configured."""
        provider = provider_manager.get_provider("nonexistent")
        assert provider is None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @patch('backend.app.services.ai.core.provider_manager.AIProviderFactory')
    def test_get_provider_creates_instance(self, mock_factory, provider_manager, mock_openai_config):
        """Test that get_provider creates provider instance."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider
        
        # Execute
        provider = provider_manager.get_provider("openai")
        
        # Verify
        assert provider == mock_provider
        mock_factory.create_provider.assert_called_once_with(
            provider_name="openai",
            api_key="test-openai-key",
            base_url="https://api.openai.com/v1"
        )
        assert "openai" in provider_manager._providers

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_provider_returns_cached_instance(self, provider_manager, mock_openai_config):
        """Test that get_provider returns cached provider instance."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        mock_provider = MagicMock()
        provider_manager._providers["openai"] = mock_provider
        
        # Execute
        provider = provider_manager.get_provider("openai")
        
        # Verify
        assert provider == mock_provider

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_providers(self, provider_manager, mock_openai_config, mock_anthropic_config):
        """Test getting available providers."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        provider_manager._provider_configs["anthropic"] = mock_anthropic_config
        
        # Execute
        providers = provider_manager.get_available_providers()
        
        # Verify
        assert "openai" in providers
        assert "anthropic" in providers
        assert len(providers) == 2

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_is_provider_available(self, provider_manager, mock_openai_config):
        """Test checking if provider is available."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute and verify
        assert provider_manager.is_provider_available("openai") is True
        assert provider_manager.is_provider_available("nonexistent") is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_provider_config(self, provider_manager, mock_openai_config):
        """Test getting provider configuration."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        config = provider_manager.get_provider_config("openai")
        
        # Verify
        assert config == mock_openai_config
        assert provider_manager.get_provider_config("nonexistent") is None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_models(self, provider_manager, mock_openai_config):
        """Test getting available models for a provider."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        models = provider_manager.get_available_models("openai")
        
        # Verify
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert "text-embedding-ada-002" in models
        assert len(models) == 4

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_models_nonexistent_provider(self, provider_manager):
        """Test getting available models for nonexistent provider."""
        models = provider_manager.get_available_models("nonexistent")
        assert models == []

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_default_model(self, provider_manager, mock_openai_config):
        """Test getting default model for a provider."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        default_model = provider_manager.get_default_model("openai")
        
        # Verify
        assert default_model == "gpt-3.5-turbo"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_default_model_nonexistent_provider(self, provider_manager):
        """Test getting default model for nonexistent provider."""
        default_model = provider_manager.get_default_model("nonexistent")
        assert default_model is None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_info_openai(self, provider_manager, mock_openai_config):
        """Test getting model info for OpenAI models."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        gpt4_info = provider_manager.get_model_info("openai", "gpt-4")
        gpt35_info = provider_manager.get_model_info("openai", "gpt-3.5-turbo")
        embedding_info = provider_manager.get_model_info("openai", "text-embedding-ada-002")
        
        # Verify
        assert gpt4_info["name"] == "gpt-4"
        assert gpt4_info["provider"] == "openai"
        assert gpt4_info["max_tokens"] == 8192
        assert gpt4_info["cost_per_1k_input"] == 0.03
        
        assert gpt35_info["name"] == "gpt-3.5-turbo"
        assert gpt35_info["max_tokens"] == 4096
        assert gpt35_info["cost_per_1k_input"] == 0.0015
        
        assert embedding_info["name"] == "text-embedding-ada-002"
        assert embedding_info["max_tokens"] == 8192
        assert embedding_info["cost_per_1k_input"] == 0.0001

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_info_anthropic(self, provider_manager, mock_anthropic_config):
        """Test getting model info for Anthropic models."""
        # Setup
        provider_manager._provider_configs["anthropic"] = mock_anthropic_config
        
        # Execute
        sonnet_info = provider_manager.get_model_info("anthropic", "claude-3-sonnet-20240229")
        opus_info = provider_manager.get_model_info("anthropic", "claude-3-opus-20240229")
        haiku_info = provider_manager.get_model_info("anthropic", "claude-3-haiku-20240307")
        
        # Verify
        assert sonnet_info["name"] == "claude-3-sonnet-20240229"
        assert sonnet_info["provider"] == "anthropic"
        assert sonnet_info["max_tokens"] == 200000
        assert sonnet_info["cost_per_1k_input"] == 0.003
        
        assert opus_info["name"] == "claude-3-opus-20240229"
        assert opus_info["max_tokens"] == 200000
        assert opus_info["cost_per_1k_input"] == 0.015
        
        assert haiku_info["name"] == "claude-3-haiku-20240307"
        assert haiku_info["max_tokens"] == 200000
        assert haiku_info["cost_per_1k_input"] == 0.00025

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_info_nonexistent_model(self, provider_manager, mock_openai_config):
        """Test getting model info for nonexistent model."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        info = provider_manager.get_model_info("openai", "nonexistent-model")
        
        # Verify
        assert info == {}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_provider_and_model(self, provider_manager, mock_openai_config):
        """Test validating provider and model combination."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute and verify
        assert provider_manager.validate_provider_and_model("openai", "gpt-4") is True
        assert provider_manager.validate_provider_and_model("openai", "gpt-3.5-turbo") is True
        assert provider_manager.validate_provider_and_model("openai", "nonexistent-model") is False
        assert provider_manager.validate_provider_and_model("nonexistent-provider", "gpt-4") is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_estimate(self, provider_manager, mock_openai_config):
        """Test cost estimation."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        cost = provider_manager.get_cost_estimate("openai", "gpt-4", 1000, 500)
        
        # Verify (1000 input tokens * 0.03 + 500 output tokens * 0.06)
        expected_cost = (1000 / 1000) * 0.03 + (500 / 1000) * 0.06
        assert cost == expected_cost

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_estimate_nonexistent_model(self, provider_manager, mock_openai_config):
        """Test cost estimation for nonexistent model."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        
        # Execute
        cost = provider_manager.get_cost_estimate("openai", "nonexistent-model", 1000, 500)
        
        # Verify
        assert cost == 0.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @patch('backend.app.services.ai.core.provider_manager.AIProviderFactory')
    def test_register_provider(self, mock_factory, provider_manager, mock_openai_config):
        """Test registering a new provider."""
        # Setup
        mock_provider_class = MagicMock()
        
        # Execute
        provider_manager.register_provider("custom", mock_provider_class, mock_openai_config)
        
        # Verify
        mock_factory.register_provider.assert_called_once_with("custom", mock_provider_class)
        assert "custom" in provider_manager._provider_configs
        assert provider_manager._provider_configs["custom"] == mock_openai_config

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_provider_status(self, provider_manager, mock_openai_config, mock_anthropic_config):
        """Test getting provider status."""
        # Setup
        provider_manager._provider_configs["openai"] = mock_openai_config
        provider_manager._provider_configs["anthropic"] = mock_anthropic_config
        mock_provider = MagicMock()
        provider_manager._providers["openai"] = mock_provider
        
        # Execute
        status = provider_manager.get_provider_status()
        
        # Verify
        assert "openai" in status
        assert "anthropic" in status
        
        openai_status = status["openai"]
        assert openai_status["available"] is True
        assert openai_status["initialized"] is True
        assert openai_status["config"]["provider_type"] == "openai"
        assert openai_status["config"]["default_model"] == "gpt-3.5-turbo"
        
        anthropic_status = status["anthropic"]
        assert anthropic_status["available"] is False  # Not initialized
        assert anthropic_status["initialized"] is False
        assert anthropic_status["config"]["provider_type"] == "anthropic"