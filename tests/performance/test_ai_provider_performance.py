"""
Performance tests for AI Provider Integration.

This module tests the performance characteristics of the AI provider integration,
including provider caching, load handling, and response times.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.ai.core.provider_manager import ProviderManager
from backend.app.services.ai.core import ChatProcessor, RequestBuilder, ResponseHandler
from backend.app.services.ai.types.ai_types import ProviderType, ProviderConfig


class TestProviderPerformance:
    """Performance tests for AI providers."""

    @pytest.fixture
    def provider_manager(self):
        """Create a ProviderManager instance."""
        return ProviderManager()

    @pytest.fixture
    def chat_processor(self):
        """Create a ChatProcessor instance."""
        request_builder = RequestBuilder()
        response_handler = ResponseHandler()
        return ChatProcessor(request_builder, response_handler)

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "Hello, how are you?"},
        ]

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_caching_performance(self, provider_manager):
        """Test provider caching performance."""
        # Mock provider configuration
        mock_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            default_model="gpt-3.5-turbo",
            available_models=["gpt-3.5-turbo"],
        )
        provider_manager._provider_configs["openai"] = mock_config

        # Mock provider factory
        with patch('backend.app.services.ai.core.provider_manager.AIProviderFactory') as mock_factory:
            mock_provider = MagicMock()
            mock_factory.create_provider.return_value = mock_provider

            # First call - should create provider
            start_time = time.time()
            provider1 = provider_manager.get_provider("openai")
            first_call_time = time.time() - start_time

            # Second call - should return cached provider
            start_time = time.time()
            provider2 = provider_manager.get_provider("openai")
            second_call_time = time.time() - start_time

            # Verify caching
            assert provider1 is provider2
            assert "openai" in provider_manager._providers

            # Second call should be significantly faster
            assert second_call_time < first_call_time * 0.1  # 10x faster

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_validation_performance(self, provider_manager):
        """Test provider validation performance."""
        # Mock provider configuration
        mock_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            default_model="gpt-3.5-turbo",
            available_models=["gpt-3.5-turbo", "gpt-4"],
        )
        provider_manager._provider_configs["openai"] = mock_config

        # Test validation performance
        start_time = time.time()
        for _ in range(1000):  # 1000 validations
            provider_manager.validate_provider_and_model("openai", "gpt-4")
        validation_time = time.time() - start_time

        # Should complete 1000 validations in reasonable time (< 1 second)
        assert validation_time < 1.0
        assert validation_time > 0  # Should take some time

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cost_estimation_performance(self, provider_manager):
        """Test cost estimation performance."""
        # Mock provider configuration
        mock_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            default_model="gpt-3.5-turbo",
            available_models=["gpt-3.5-turbo", "gpt-4"],
        )
        provider_manager._provider_configs["openai"] = mock_config

        # Test cost estimation performance
        start_time = time.time()
        for _ in range(1000):  # 1000 cost estimations
            provider_manager.get_cost_estimate("openai", "gpt-4", 1000, 500)
        estimation_time = time.time() - start_time

        # Should complete 1000 estimations in reasonable time (< 1 second)
        assert estimation_time < 1.0
        assert estimation_time > 0  # Should take some time

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_provider_access(self, provider_manager):
        """Test concurrent provider access performance."""
        # Mock provider configuration
        mock_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            default_model="gpt-3.5-turbo",
            available_models=["gpt-3.5-turbo"],
        )
        provider_manager._provider_configs["openai"] = mock_config

        # Mock provider factory
        with patch('backend.app.services.ai.core.provider_manager.AIProviderFactory') as mock_factory:
            mock_provider = MagicMock()
            mock_factory.create_provider.return_value = mock_provider

            # Test concurrent access
            async def get_provider():
                return provider_manager.get_provider("openai")

            start_time = time.time()
            tasks = [get_provider() for _ in range(100)]  # 100 concurrent requests
            providers = await asyncio.gather(*tasks)
            concurrent_time = time.time() - start_time

            # All providers should be the same (cached)
            assert all(p is providers[0] for p in providers)
            
            # Should complete quickly (< 0.1 seconds)
            assert concurrent_time < 0.1

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_status_performance(self, provider_manager):
        """Test provider status retrieval performance."""
        # Mock multiple provider configurations
        for i in range(10):  # 10 providers
            mock_config = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key=f"test-key-{i}",
                default_model="gpt-3.5-turbo",
                available_models=["gpt-3.5-turbo"],
            )
            provider_manager._provider_configs[f"provider-{i}"] = mock_config

        # Test status retrieval performance
        start_time = time.time()
        for _ in range(100):  # 100 status retrievals
            status = provider_manager.get_provider_status()
        status_time = time.time() - start_time

        # Should complete 100 status retrievals in reasonable time (< 1 second)
        assert status_time < 1.0
        assert len(status) == 10  # All 10 providers

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_chat_processor_provider_integration_performance(self, chat_processor):
        """Test ChatProcessor provider integration performance."""
        # Mock provider manager
        with patch.object(chat_processor.provider_manager, 'is_provider_available', return_value=True):
            with patch.object(chat_processor.provider_manager, 'validate_provider_and_model', return_value=True):
                with patch.object(chat_processor.provider_manager, 'get_provider') as mock_get_provider:
                    mock_provider = MagicMock()
                    mock_provider.chat_completion = AsyncMock()
                    mock_get_provider.return_value = mock_provider

                    # Test provider integration performance
                    start_time = time.time()
                    for _ in range(100):  # 100 provider validations
                        chat_processor.provider_manager.is_provider_available("openai")
                        chat_processor.provider_manager.validate_provider_and_model("openai", "gpt-4")
                    integration_time = time.time() - start_time

                    # Should complete 100 validations in reasonable time (< 1 second)
                    assert integration_time < 1.0

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_middleware_pipeline_performance(self, chat_processor):
        """Test middleware pipeline performance."""
        # Mock all middleware components
        with patch.object(chat_processor.provider_manager, 'is_provider_available', return_value=True):
            with patch.object(chat_processor.provider_manager, 'validate_provider_and_model', return_value=True):
                with patch.object(chat_processor.provider_manager, 'get_provider') as mock_get_provider:
                    mock_provider = MagicMock()
                    mock_provider.chat_completion = AsyncMock()
                    mock_get_provider.return_value = mock_provider

                    # Test middleware pipeline performance
                    start_time = time.time()
                    for _ in range(50):  # 50 pipeline executions
                        await chat_processor._apply_middleware(
                            messages=[{"role": "user", "content": "test"}],
                            user_id="user123",
                            use_knowledge_base=True,
                            use_tools=True,
                            max_context_chunks=5,
                        )
                    pipeline_time = time.time() - start_time

                    # Should complete 50 pipeline executions in reasonable time (< 5 seconds)
                    assert pipeline_time < 5.0

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_memory_usage(self, provider_manager):
        """Test provider memory usage under load."""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create many provider configurations
        for i in range(100):  # 100 providers
            mock_config = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key=f"test-key-{i}",
                default_model="gpt-3.5-turbo",
                available_models=["gpt-3.5-turbo", "gpt-4"] * 10,  # 20 models each
            )
            provider_manager._provider_configs[f"provider-{i}"] = mock_config

        # Get memory usage after creating providers
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 10MB for 100 providers)
        assert memory_increase < 10 * 1024 * 1024  # 10MB

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_response_time_simulation(self, provider_manager):
        """Test simulated provider response times."""
        # Mock provider with simulated response time
        with patch('backend.app.services.ai.core.provider_manager.AIProviderFactory') as mock_factory:
            mock_provider = MagicMock()
            
            async def simulated_chat_completion(request):
                await asyncio.sleep(0.1)  # Simulate 100ms response time
                return MagicMock(content="Response", usage={}, finish_reason="stop")
            
            mock_provider.chat_completion = simulated_chat_completion
            mock_factory.create_provider.return_value = mock_provider

            # Mock provider configuration
            mock_config = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                default_model="gpt-3.5-turbo",
                available_models=["gpt-3.5-turbo"],
            )
            provider_manager._provider_configs["openai"] = mock_config

            # Test response time
            start_time = time.time()
            provider = provider_manager.get_provider("openai")
            response = await provider.chat_completion(MagicMock())
            response_time = time.time() - start_time

            # Response time should be around 100ms (with some tolerance)
            assert 0.09 <= response_time <= 0.15  # 90-150ms tolerance

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_error_handling_performance(self, provider_manager):
        """Test provider error handling performance."""
        # Mock provider that raises errors
        with patch('backend.app.services.ai.core.provider_manager.AIProviderFactory') as mock_factory:
            mock_provider = MagicMock()
            mock_provider.chat_completion = AsyncMock(side_effect=Exception("Test error"))
            mock_factory.create_provider.return_value = mock_provider

            # Mock provider configuration
            mock_config = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                default_model="gpt-3.5-turbo",
                available_models=["gpt-3.5-turbo"],
            )
            provider_manager._provider_configs["openai"] = mock_config

            # Test error handling performance
            start_time = time.time()
            for _ in range(100):  # 100 error scenarios
                try:
                    provider = provider_manager.get_provider("openai")
                    await provider.chat_completion(MagicMock())
                except Exception:
                    pass  # Expected
            error_handling_time = time.time() - start_time

            # Should handle 100 errors in reasonable time (< 2 seconds)
            assert error_handling_time < 2.0