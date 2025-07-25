import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestPerformance:
    """Performance tests for the application."""

    def test_health_check_response_time(self):
        """Test health check endpoint response time."""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 400, 404]  # noqa: S101
        assert response_time < 0.1  # noqa: S101

    def test_login_response_time(self):
        """Test login endpoint response time."""
        login_data = {
            "email": "test@example.com",
            "password": "password123",
        }

        start_time = time.time()
        response = client.post("/api/v1/auth/login", json=login_data)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 401, 422]  # noqa: S101
        assert response_time < 0.5  # noqa: S101

    def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""

        def make_request():
            return client.get("/health")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should succeed
        assert all(r.status_code in [200, 400, 404] for r in responses)  # noqa: S101
        # Should handle 50 concurrent requests within 5 seconds
        assert total_time < 5.0  # noqa: S101
        # Average response time should be reasonable
        avg_response_time = total_time / len(responses)
        assert avg_response_time < 0.1  # noqa: S101

    def test_concurrent_login_requests(self):
        """Test concurrent login requests."""
        login_data = {
            "email": "test@example.com",
            "password": "password123",
        }

        def make_login_request():
            return client.post("/api/v1/auth/login", json=login_data)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_login_request) for _ in range(20)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should complete
        assert all(r.status_code in [200, 401, 422] for r in responses)  # noqa: S101
        # Should handle 20 concurrent login requests within 10 seconds
        assert total_time < 10.0  # noqa: S101

    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        def make_requests():
            for _ in range(100):
                client.get("/health")

        # Run requests in background
        thread = threading.Thread(target=make_requests)
        thread.start()
        thread.join()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50.0

    def test_database_connection_pool(self):
        """Test database connection pool performance."""

        def make_db_request():
            # Simulate database operation
            response = client.get("/api/v1/users/me")
            return response.status_code

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_db_request) for _ in range(100)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle database requests efficiently
        assert total_time < 10.0  # noqa: S101
        assert all(r in [200, 401, 403, 404] for r in responses)

    def test_api_response_size(self):
        """Test API response size optimization."""
        response = client.get("/health")

        # Response should not be too large
        response_size = len(response.content)
        assert response_size < 10000  # Less than 10KB

    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        large_data = {
            "content": "x" * 10000,  # 10KB of data
            "metadata": {"key": "value" * 1000},
        }

        start_time = time.time()
        response = client.post("/api/v1/chat/messages", json=large_data)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 400, 401, 422]
        assert response_time < 2.0  # Should handle large payloads within 2 seconds

    def test_file_upload_performance(self):
        """Test file upload performance."""
        test_file_content = b"x" * 1024 * 1024  # 1MB file

        start_time = time.time()
        response = client.post(
            "/api/v1/knowledge/upload",
            files={"file": ("test.txt", test_file_content, "text/plain")},
        )
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 201, 400, 401, 422]
        assert response_time < 5.0  # Should handle 1MB upload within 5 seconds

    def test_search_performance(self):
        """Test search endpoint performance."""
        search_data = {
            "query": "test query",
            "type": "all",
            "limit": 100,
        }

        start_time = time.time()
        response = client.post("/api/v1/search", json=search_data)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 400, 401, 422]
        assert response_time < 1.0  # Search should complete within 1 second

    def test_websocket_connection_performance(self):
        """Test WebSocket connection performance."""
        # This would require a WebSocket client
        # For now, we'll test the endpoint availability
        response = client.get("/ws")
        assert response.status_code in [200, 400, 404, 426]  # 426 = Upgrade Required

    def test_rate_limiting_performance(self):
        """Test rate limiting performance."""

        def make_request():
            return client.get("/health")

        start_time = time.time()

        # Make many requests quickly
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(200)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle rate limiting efficiently
        assert total_time < 15.0  # noqa: S101
        # Some requests might be rate limited (429)
        status_codes = [r.status_code for r in responses]
        assert all(code in [200, 400, 404, 429] for code in status_codes)

    def test_caching_performance(self):
        """Test caching performance."""
        # First request
        start_time = time.time()
        response1 = client.get("/health")
        first_request_time = time.time() - start_time

        # Second request (should be cached)
        start_time = time.time()
        response2 = client.get("/health")
        second_request_time = time.time() - start_time

        # Cached request should be faster
        assert second_request_time <= first_request_time
        assert response1.status_code == response2.status_code

    def test_error_handling_performance(self):
        """Test error handling performance."""
        start_time = time.time()
        response = client.get("/nonexistent-endpoint")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code == 404
        assert response_time < 0.1  # Error responses should be fast

    def test_authentication_performance(self):
        """Test authentication performance."""

        def make_authenticated_request():
            headers = {"Authorization": "Bearer invalid-token"}
            return client.get("/api/v1/users/me", headers=headers)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_authenticated_request) for _ in range(50)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Authentication checks should be fast
        assert total_time < 2.0  # noqa: S101
        assert all(r.status_code in [401, 403] for r in responses)

    def test_json_parsing_performance(self):
        """Test JSON parsing performance."""
        large_json = {
            "data": [{"id": i, "content": f"content {i}" * 100} for i in range(1000)],
        }

        start_time = time.time()
        response = client.post("/api/v1/chat/batch", json=large_json)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 400, 401, 422]
        assert response_time < 3.0  # Large JSON parsing should be efficient

    def test_database_query_performance(self):
        """Test database query performance."""

        def make_db_query():
            # Simulate database query
            response = client.get("/api/v1/conversations/")
            return response.status_code

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_db_query) for _ in range(50)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Database queries should be efficient
        assert total_time < 5.0  # noqa: S101
        assert all(r in [200, 401, 403, 404] for r in responses)

    def test_static_file_serving_performance(self):
        """Test static file serving performance."""
        start_time = time.time()
        response = client.get("/static/favicon.ico")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 404]
        assert response_time < 0.1  # Static files should be served quickly

    def test_api_documentation_performance(self):
        """Test API documentation performance."""
        start_time = time.time()
        response = client.get("/docs")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 404]
        assert response_time < 1.0  # Documentation should load quickly

    def test_health_check_endpoint_load(self):
        """Test health check endpoint under load."""

        def make_health_request():
            return client.get("/health")

        # Simulate high load
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_health_request) for _ in range(1000)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle 1000 requests efficiently
        assert total_time < 30.0  # noqa: S101
        assert all(r.status_code in [200, 400, 404] for r in responses)

        # Calculate requests per second
        rps = len(responses) / total_time
        assert rps > 30  # Should handle at least 30 requests per second

    def test_memory_leak_detection(self):
        """Test for memory leaks."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform many operations
        for _ in range(1000):
            client.get("/health")

        # Force garbage collection
        import gc

        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (less than 10MB)
        assert memory_increase < 10.0

    def test_cpu_usage_under_load(self):
        """Test CPU usage under load."""
        process = psutil.Process(os.getpid())

        def make_requests():
            for _ in range(100):
                client.get("/health")

        # Monitor CPU usage during load
        cpu_percentages = []

        def monitor_cpu():
            for _ in range(10):
                cpu_percentages.append(process.cpu_percent())
                time.sleep(0.1)

        # Start monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Start load
        load_thread = threading.Thread(target=make_requests)
        load_thread.start()

        # Wait for completion
        load_thread.join()
        monitor_thread.join()

        # CPU usage should be reasonable
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        assert avg_cpu < 80.0  # Should not exceed 80% CPU usage

    def test_network_io_performance(self):
        """Test network I/O performance."""
        large_data = {
            "messages": [{"content": "test message" * 100} for _ in range(100)],
        }

        start_time = time.time()
        response = client.post("/api/v1/chat/batch", json=large_data)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code in [200, 400, 401, 422]
        assert response_time < 2.0  # Network I/O should be efficient

    def test_concurrent_user_sessions(self):
        """Test concurrent user sessions."""

        def simulate_user_session():
            # Login
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                },
            )

            if login_response.status_code == 200:
                token = login_response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}

                # Make authenticated requests
                for _ in range(10):
                    client.get("/api/v1/users/me", headers=headers)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_user_session) for _ in range(20)]
            for future in as_completed(futures):
                future.result()  # Wait for completion

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle concurrent sessions efficiently
        assert total_time < 30.0


class TestLoadTesting:
    """Load testing scenarios."""

    def test_sustained_load(self):
        """Test sustained load over time."""

        def make_request():
            return client.get("/health")

        start_time = time.time()
        request_count = 0

        # Run for 30 seconds
        while time.time() - start_time < 30:
            response = make_request()
            assert response.status_code in [200, 400, 404]
            request_count += 1
            time.sleep(0.01)  # 100 requests per second

        # Should handle sustained load
        assert request_count > 2500  # At least 2500 requests in 30 seconds

    def test_burst_load(self):
        """Test burst load handling."""

        def make_request():
            return client.get("/health")

        start_time = time.time()

        # Burst of 1000 requests
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(make_request) for _ in range(1000)]
            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle burst load
        assert total_time < 10.0
        assert all(r.status_code in [200, 400, 404] for r in responses)

    def test_mixed_workload(self):
        """Test mixed workload performance."""

        def health_check():
            return client.get("/health")

        def login_request():
            return client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                },
            )

        def search_request():
            return client.post(
                "/api/v1/search",
                json={
                    "query": "test",
                    "type": "all",
                },
            )

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            # Mix different types of requests
            for _ in range(100):
                futures.append(executor.submit(health_check))
            for _ in range(50):
                futures.append(executor.submit(login_request))
            for _ in range(50):
                futures.append(executor.submit(search_request))

            responses = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle mixed workload
        assert total_time < 15.0
        assert all(r.status_code in [200, 400, 401, 404, 422] for r in responses)
