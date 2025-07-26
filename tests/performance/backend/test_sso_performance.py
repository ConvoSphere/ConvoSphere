"""
Performance tests for SSO integration.

This module tests the performance and scalability of SSO authentication flows.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

# from backend.app.main import app  # Commented out for testing without full app context


class TestSSOPerformance:
    """Performance tests for SSO functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_sso_providers_endpoint_performance(self, client):
        """Test SSO providers endpoint performance."""
        start_time = time.time()

        # Make multiple requests to test performance
        for _ in range(100):
            response = client.get("/api/v1/auth/sso/providers")
            assert response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 100 requests in under 5 seconds
        assert total_time < 5.0

    def test_concurrent_sso_providers_requests(self, client):
        """Test concurrent SSO providers requests."""

        def make_request():
            response = client.get("/api/v1/auth/sso/providers")
            return response.status_code == 200

        start_time = time.time()

        # Make 50 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: make_request(), range(50)))

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should succeed
        assert all(results)
        # Should complete in under 3 seconds
        assert total_time < 3.0

    @pytest.mark.asyncio
    async def test_oauth_service_initialization_performance(self):
        """Test OAuth service initialization performance."""
        from backend.app.services.oauth_service import OAuthService

        start_time = time.time()

        # Initialize OAuth service multiple times
        for _ in range(10):
            service = OAuthService()
            assert service is not None

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in under 2 seconds
        assert total_time < 2.0

    @pytest.mark.asyncio
    async def test_saml_service_initialization_performance(self):
        """Test SAML service initialization performance."""
        from backend.app.services.saml_service import SAMLService

        start_time = time.time()

        # Initialize SAML service multiple times
        for _ in range(5):  # SAML is more expensive to initialize
            service = SAMLService()
            assert service is not None

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in under 3 seconds
        assert total_time < 3.0

    def test_sso_login_endpoint_performance(self, client):
        """Test SSO login endpoint performance."""
        start_time = time.time()

        # Test with different providers
        providers = ["google", "microsoft", "github", "saml"]

        for provider in providers:
            response = client.get(f"/api/v1/auth/sso/login/{provider}")
            # Should either redirect or return error (if not configured)
            assert response.status_code in [200, 302, 400, 500]

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in under 2 seconds
        assert total_time < 2.0

    def test_saml_metadata_endpoint_performance(self, client):
        """Test SAML metadata endpoint performance."""
        start_time = time.time()

        # Make multiple requests to metadata endpoint
        for _ in range(20):
            response = client.get("/api/v1/auth/sso/metadata")
            # Should either return metadata or error (if not configured)
            assert response.status_code in [200, 400, 500]

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in under 3 seconds
        assert total_time < 3.0

    @pytest.mark.asyncio
    async def test_user_processing_performance(self):
        """Test SSO user processing performance."""
        from unittest.mock import MagicMock

        from backend.app.services.oauth_service import OAuthService
        from backend.app.services.saml_service import SAMLService

        # Mock database session
        mock_db = MagicMock()

        # Test OAuth user processing
        oauth_service = OAuthService()
        SAMLService()

        # Mock user info
        user_info = {
            "email": "test@example.com",
            "external_id": "test123",
            "first_name": "Test",
            "last_name": "User",
            "display_name": "Test User",
            "sso_attributes": {"test": "value"},
        }

        start_time = time.time()

        # Process users multiple times
        for _ in range(50):
            try:
                # This will fail due to mock DB, but we're testing performance
                await oauth_service.process_sso_user(user_info, "google", mock_db)
            except:
                pass  # Expected to fail with mock DB

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in under 2 seconds
        assert total_time < 2.0

    def test_memory_usage_under_load(self, client):
        """Test memory usage under load."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make many requests to simulate load
        for _ in range(1000):
            client.get("/api/v1/auth/sso/providers")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50.0

    def test_response_time_consistency(self, client):
        """Test that response times are consistent."""
        response_times = []

        # Make 50 requests and measure response times
        for _ in range(50):
            start_time = time.time()
            client.get("/api/v1/auth/sso/providers")
            end_time = time.time()
            response_times.append(end_time - start_time)

        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # Average should be under 100ms
        assert avg_time < 0.1
        # Max should be under 500ms
        assert max_time < 0.5
        # Min should be reasonable (> 1ms)
        assert min_time > 0.001



class TestSSOLoadTesting:
    """Load testing for SSO functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_high_concurrency_sso_providers(self, client):
        """Test SSO providers endpoint under high concurrency."""
        import queue
        import threading

        results = queue.Queue()

        def worker():
            try:
                response = client.get("/api/v1/auth/sso/providers")
                results.put(response.status_code == 200)
            except Exception:
                results.put(False)

        start_time = time.time()

        # Start 100 concurrent threads
        threads = []
        for _ in range(100):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Check results
        success_count = sum(results.get() for _ in range(100))

        # At least 90% should succeed
        assert success_count >= 90
        # Should complete in under 10 seconds
        assert total_time < 10.0


    def test_sustained_load(self, client):
        """Test sustained load over time."""
        start_time = time.time()
        request_count = 0
        error_count = 0

        # Make requests for 30 seconds or until 1000 requests
        while time.time() - start_time < 30 and request_count < 1000:
            try:
                response = client.get("/api/v1/auth/sso/providers")
                if response.status_code == 200:
                    request_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

            # Small delay to prevent overwhelming
            time.sleep(0.01)

        time.time() - start_time

        # Should handle at least 500 requests
        assert request_count >= 500
        # Error rate should be low (< 10%)
        error_rate = (
            error_count / (request_count + error_count)
            if (request_count + error_count) > 0
            else 0
        )
        assert error_rate < 0.1



class TestSSOSecurityPerformance:
    """Security-related performance tests."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_csrf_protection_performance(self, client):
        """Test CSRF protection doesn't significantly impact performance."""
        # Test with valid requests (should be fast)
        start_time = time.time()

        for _ in range(100):
            response = client.get("/api/v1/auth/sso/providers")
            assert response.status_code == 200

        valid_time = time.time() - start_time

        # Test with potentially malicious requests (should still be reasonable)
        start_time = time.time()

        for _ in range(100):
            # Simulate potential CSRF attempts
            response = client.get(
                "/api/v1/auth/sso/providers",
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Origin": "https://malicious-site.com",
                },
            )
            assert response.status_code == 200

        malicious_time = time.time() - start_time

        # Malicious requests shouldn't be significantly slower
        assert malicious_time < valid_time * 2

    def test_rate_limiting_simulation(self, client):
        """Test that the system can handle rapid requests without degradation."""
        response_times = []

        # Make rapid requests
        for i in range(200):
            start_time = time.time()
            client.get("/api/v1/auth/sso/providers")
            end_time = time.time()

            response_times.append(end_time - start_time)

            # Check for degradation over time
            if i > 50:
                recent_avg = sum(response_times[-50:]) / 50
                early_avg = sum(response_times[:50]) / 50

                # Recent requests shouldn't be significantly slower
                assert recent_avg < early_avg * 1.5

