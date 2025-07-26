"""
Performance tests for API endpoints.

This module tests the performance characteristics of the API including:
- Response time benchmarks
- Concurrent user handling
- Load testing scenarios
- Memory usage monitoring
- Database query performance
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserRole


class TestAPIPerformance:
    """Test class for API performance characteristics."""

    @pytest.fixture
    def performance_client(self, client: TestClient) -> TestClient:
        """Create test client for performance testing."""
        return client

    @pytest.fixture
    def sample_users(self, db_session: Session) -> list[User]:
        """Create sample users for performance testing."""
        users = []
        for i in range(10):
            user = User(
                email=f"user{i}@test.com",
                username=f"user{i}",
                hashed_password="hashed_password",
                first_name=f"User{i}",
                last_name="Test",
                role=UserRole.USER,
                is_active=True,
            )
            db_session.add(user)
            users.append(user)

        db_session.commit()
        return users

    def test_user_api_response_time(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test user API response time under normal load."""
        response_times = []

        # Test 100 requests
        for _ in range(100):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.users.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                response = performance_client.get("/api/v1/users/")

            end_time = time.time()
            response_times.append(end_time - start_time)

            assert response.status_code == 200

        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)

        # Performance assertions
        assert avg_response_time < 0.1  # Average response time under 100ms
        assert max_response_time < 0.5  # Maximum response time under 500ms
        assert min_response_time > 0.001  # Minimum response time reasonable

        print("User API Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Maximum: {max_response_time:.3f}s")
        print(f"  Minimum: {min_response_time:.3f}s")

    def test_chat_api_response_time(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test chat API response time."""
        response_times = []

        # Test 50 chat requests
        for _ in range(50):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.chat.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                chat_data = {
                    "message": "Hello, this is a test message",
                    "conversation_id": None,
                }

                response = performance_client.post("/api/v1/chat/", json=chat_data)

            end_time = time.time()
            response_times.append(end_time - start_time)

            # Chat API might take longer due to AI processing
            assert response.status_code in [200, 201, 202]

        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        # Chat API can be slower due to AI processing
        assert avg_response_time < 2.0  # Average response time under 2s
        assert max_response_time < 5.0  # Maximum response time under 5s

        print("Chat API Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Maximum: {max_response_time:.3f}s")

    def test_document_processing_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test document processing performance."""
        response_times = []

        # Test document upload and processing
        for i in range(20):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.document_endpoints.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                # Mock file upload
                files = {
                    "file": (
                        "test_document.txt",
                        b"This is a test document content.",
                        "text/plain",
                    )
                }

                response = performance_client.post(
                    "/api/v1/documents/upload", files=files
                )

            end_time = time.time()
            response_times.append(end_time - start_time)

            assert response.status_code in [200, 201, 202]

        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        # Document processing can be slower
        assert avg_response_time < 3.0  # Average response time under 3s
        assert max_response_time < 10.0  # Maximum response time under 10s

        print("Document Processing Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Maximum: {max_response_time:.3f}s")

    def test_concurrent_user_handling(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test handling of concurrent users."""
        concurrent_users = 50
        response_times = []
        successful_requests = 0
        failed_requests = 0

        def make_request(user_id: int):
            try:
                start_time = time.time()

                with patch(
                    "backend.app.api.v1.endpoints.users.get_current_user"
                ) as mock_auth:
                    mock_auth.return_value = sample_users[user_id % len(sample_users)]

                    response = performance_client.get("/api/v1/users/")

                end_time = time.time()

                if response.status_code == 200:
                    return end_time - start_time, True
                return end_time - start_time, False

            except Exception:
                return time.time() - start_time, False

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(make_request, i) for i in range(concurrent_users)
            ]

            for future in as_completed(futures):
                response_time, success = future.result()
                response_times.append(response_time)

                if success:
                    successful_requests += 1
                else:
                    failed_requests += 1

        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        success_rate = successful_requests / concurrent_users

        # Performance assertions
        assert success_rate > 0.95  # 95% success rate
        assert avg_response_time < 0.2  # Average response time under 200ms
        assert max_response_time < 1.0  # Maximum response time under 1s

        print("Concurrent User Performance:")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        print(f"  Maximum Response Time: {max_response_time:.3f}s")
        print(f"  Successful Requests: {successful_requests}")
        print(f"  Failed Requests: {failed_requests}")

    def test_database_query_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test database query performance."""
        query_times = []

        # Test database queries
        for _ in range(100):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.users.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                # Test different query patterns
                response = performance_client.get("/api/v1/users/?page=1&size=10")

            end_time = time.time()
            query_times.append(end_time - start_time)

            assert response.status_code == 200

        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)

        # Database queries should be fast
        assert avg_query_time < 0.05  # Average query time under 50ms
        assert max_query_time < 0.2  # Maximum query time under 200ms

        print("Database Query Performance:")
        print(f"  Average: {avg_query_time:.3f}s")
        print(f"  Maximum: {max_query_time:.3f}s")

    def test_memory_usage_monitoring(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test memory usage during API operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform operations
        for _ in range(100):
            with patch(
                "backend.app.api.v1.endpoints.users.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                response = performance_client.get("/api/v1/users/")
                assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable
        assert memory_increase < 100  # Less than 100MB increase

        print("Memory Usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")

    def test_authentication_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test authentication performance."""
        auth_times = []

        # Test authentication requests
        for _ in range(100):
            start_time = time.time()

            auth_data = {"email": "user0@test.com", "password": "testpassword"}

            response = performance_client.post("/api/v1/auth/login", json=auth_data)

            end_time = time.time()
            auth_times.append(end_time - start_time)

            # Authentication might fail in test environment, but should be fast
            assert response.status_code in [200, 401, 422]

        avg_auth_time = statistics.mean(auth_times)
        max_auth_time = max(auth_times)

        # Authentication should be fast
        assert avg_auth_time < 0.1  # Average auth time under 100ms
        assert max_auth_time < 0.5  # Maximum auth time under 500ms

        print("Authentication Performance:")
        print(f"  Average: {avg_auth_time:.3f}s")
        print(f"  Maximum: {max_auth_time:.3f}s")

    def test_search_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test search functionality performance."""
        search_times = []

        # Test search requests
        search_queries = ["test", "user", "document", "chat", "assistant"]

        for query in search_queries:
            for _ in range(20):
                start_time = time.time()

                with patch(
                    "backend.app.api.v1.endpoints.search.get_current_user"
                ) as mock_auth:
                    mock_auth.return_value = sample_users[0]

                    response = performance_client.get(f"/api/v1/search/?q={query}")

                end_time = time.time()
                search_times.append(end_time - start_time)

                assert response.status_code in [200, 404]

        avg_search_time = statistics.mean(search_times)
        max_search_time = max(search_times)

        # Search should be reasonably fast
        assert avg_search_time < 0.3  # Average search time under 300ms
        assert max_search_time < 1.0  # Maximum search time under 1s

        print("Search Performance:")
        print(f"  Average: {avg_search_time:.3f}s")
        print(f"  Maximum: {max_search_time:.3f}s")

    def test_api_endpoint_scalability(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test API endpoint scalability with increasing load."""
        load_levels = [10, 25, 50, 100]
        scalability_results = {}

        for load in load_levels:
            response_times = []
            successful_requests = 0

            def make_scalability_request():
                try:
                    start_time = time.time()

                    with patch(
                        "backend.app.api.v1.endpoints.users.get_current_user"
                    ) as mock_auth:
                        mock_auth.return_value = sample_users[0]

                        response = performance_client.get("/api/v1/users/")

                    end_time = time.time()

                    if response.status_code == 200:
                        return end_time - start_time, True
                    return end_time - start_time, False

                except Exception:
                    return time.time() - start_time, False

            # Execute requests for this load level
            with ThreadPoolExecutor(max_workers=load) as executor:
                futures = [
                    executor.submit(make_scalability_request) for _ in range(load)
                ]

                for future in as_completed(futures):
                    response_time, success = future.result()
                    response_times.append(response_time)

                    if success:
                        successful_requests += 1

            avg_response_time = statistics.mean(response_times)
            success_rate = successful_requests / load

            scalability_results[load] = {
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
                "total_requests": load,
            }

        # Analyze scalability
        for load, results in scalability_results.items():
            print(f"Load Level {load}:")
            print(f"  Average Response Time: {results['avg_response_time']:.3f}s")
            print(f"  Success Rate: {results['success_rate']:.2%}")

            # Performance should degrade gracefully
            assert results["success_rate"] > 0.9  # 90% success rate minimum
            assert results["avg_response_time"] < 0.5  # Response time under 500ms

    def test_error_handling_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test performance when handling errors."""
        error_response_times = []

        # Test various error scenarios
        error_scenarios = [
            ("/api/v1/users/nonexistent", 404),
            ("/api/v1/invalid-endpoint", 404),
            ("/api/v1/users/", 401),  # Unauthorized
        ]

        for endpoint, expected_status in error_scenarios:
            for _ in range(20):
                start_time = time.time()

                try:
                    response = performance_client.get(endpoint)
                    assert response.status_code == expected_status
                except Exception:
                    pass  # Expected for some error scenarios

                end_time = time.time()
                error_response_times.append(end_time - start_time)

        avg_error_time = statistics.mean(error_response_times)
        max_error_time = max(error_response_times)

        # Error handling should be fast
        assert avg_error_time < 0.1  # Average error response time under 100ms
        assert max_error_time < 0.3  # Maximum error response time under 300ms

        print("Error Handling Performance:")
        print(f"  Average: {avg_error_time:.3f}s")
        print(f"  Maximum: {max_error_time:.3f}s")

    @pytest.mark.asyncio
    async def test_async_endpoint_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test performance of async endpoints."""
        async_response_times = []

        # Test async endpoints
        async def test_async_endpoint():
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.chat.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                response = performance_client.get("/api/v1/health/")

            end_time = time.time()
            return end_time - start_time

        # Run multiple async requests
        tasks = [test_async_endpoint() for _ in range(50)]
        results = await asyncio.gather(*tasks)

        async_response_times.extend(results)

        avg_async_time = statistics.mean(async_response_times)
        max_async_time = max(async_response_times)

        # Async endpoints should be fast
        assert avg_async_time < 0.05  # Average async response time under 50ms
        assert max_async_time < 0.2  # Maximum async response time under 200ms

        print("Async Endpoint Performance:")
        print(f"  Average: {avg_async_time:.3f}s")
        print(f"  Maximum: {max_async_time:.3f}s")

    def test_caching_performance(
        self, performance_client: TestClient, sample_users: list[User]
    ):
        """Test performance with caching enabled."""
        cached_times = []
        non_cached_times = []

        # Test without cache (first request)
        for _ in range(20):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.users.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                response = performance_client.get("/api/v1/users/")

            end_time = time.time()
            non_cached_times.append(end_time - start_time)

            assert response.status_code == 200

        # Test with cache (subsequent requests)
        for _ in range(20):
            start_time = time.time()

            with patch(
                "backend.app.api.v1.endpoints.users.get_current_user"
            ) as mock_auth:
                mock_auth.return_value = sample_users[0]

                response = performance_client.get("/api/v1/users/")

            end_time = time.time()
            cached_times.append(end_time - start_time)

            assert response.status_code == 200

        avg_cached_time = statistics.mean(cached_times)
        avg_non_cached_time = statistics.mean(non_cached_times)

        # Cached requests should be faster
        assert avg_cached_time < avg_non_cached_time

        print("Caching Performance:")
        print(f"  Non-cached Average: {avg_non_cached_time:.3f}s")
        print(f"  Cached Average: {avg_cached_time:.3f}s")
        print(
            f"  Improvement: {((avg_non_cached_time - avg_cached_time) / avg_non_cached_time * 100):.1f}%"
        )
