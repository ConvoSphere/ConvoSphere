"""
Security tests for identifying vulnerabilities.
"""
import pytest


@pytest.mark.security
class TestSQLInjection:
    """Test SQL injection vulnerabilities."""

    def test_sql_injection_in_user_search(self, client):
        """Test SQL injection in user search endpoint."""
        payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "1' OR '1'='1'--",
        ]

        for payload in payloads:
            response = client.get(f"/api/users/search?q={payload}")
            # Should not return sensitive data or crash
            assert response.status_code in [200, 400, 404, 422]

    def test_sql_injection_in_login(self, client):
        """Test SQL injection in login endpoint."""
        payloads = [
            "admin'--",
            "' OR '1'='1",
            "'; DROP TABLE users; --",
        ]

        for payload in payloads:
            login_data = {
                "username": payload,
                "password": "password",
            }
            response = client.post("/api/auth/login", data=login_data)
            # Should not authenticate with SQL injection
            assert response.status_code == 401


@pytest.mark.security
class TestXSS:
    """Test Cross-Site Scripting vulnerabilities."""

    def test_xss_in_message_content(self, client, test_user_headers):
        """Test XSS in message content."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
        ]

        for payload in xss_payloads:
            message_data = {
                "content": payload,
                "role": "user",
            }

            response = client.post(
                "/api/conversations/1/messages",
                json=message_data,
                headers=test_user_headers,
            )

            # Should sanitize or reject XSS payloads
            if response.status_code == 201:
                message = response.json()
                # Check if content was sanitized
                assert "<script>" not in message["content"]
                assert "javascript:" not in message["content"]
                assert "onerror=" not in message["content"]
            else:
                # Should reject malicious content
                assert response.status_code in [400, 422]


@pytest.mark.security
class TestCSRF:
    """Test Cross-Site Request Forgery vulnerabilities."""

    def test_csrf_protection(self, client, test_user_headers):
        """Test CSRF protection on state-changing endpoints."""
        # Test without CSRF token
        user_data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        response = client.put(
            "/api/users/me",
            json=user_data,
            headers=test_user_headers,
        )

        # Should either require CSRF token or use other protection
        assert response.status_code in [200, 403, 422]


class TestAuthentication:
    """Test authentication vulnerabilities."""

    def test_weak_password_validation(self, client):
        """Test weak password validation."""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "123456",
            "qwerty",
        ]

        for password in weak_passwords:
            user_data = {
                "email": f"test_{password}@example.com",
                "username": f"test_{password}",
                "password": password,
                "first_name": "Test",
                "last_name": "User",
            }

            response = client.post("/api/auth/register", json=user_data)
            # Should reject weak passwords
            assert response.status_code in [400, 422]

    def test_brute_force_protection(self, client):
        """Test brute force protection."""
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword",
        }

        # Try multiple login attempts
        for _ in range(10):
            response = client.post("/api/auth/login", data=login_data)

        # Should implement rate limiting or account lockout
        assert response.status_code in [401, 429]


@pytest.mark.security
class TestAuthorization:
    """Test authorization vulnerabilities."""

    def test_unauthorized_access(self, client, test_user_headers):
        """Test unauthorized access to resources."""
        # Try to access another user's data
        response = client.get("/api/users/2", headers=test_user_headers)
        # Should not allow access to other users' data
        assert response.status_code in [403, 404]

    def test_privilege_escalation(self, client, test_user_headers):
        """Test privilege escalation attempts."""
        # Try to access admin endpoints as regular user
        admin_endpoints = [
            "/api/admin/users",
            "/api/admin/stats",
            "/api/admin/system",
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=test_user_headers)
            # Should not allow regular users to access admin endpoints
            assert response.status_code in [403, 404]


@pytest.mark.security
class TestInputValidation:
    """Test input validation vulnerabilities."""

    def test_path_traversal(self, client, test_user_headers):
        """Test path traversal attacks."""
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
        ]

        for payload in payloads:
            response = client.get(f"/api/documents/{payload}", headers=test_user_headers)
            # Should not allow access to system files
            assert response.status_code in [400, 404, 422]

    def test_command_injection(self, client, test_user_headers):
        """Test command injection vulnerabilities."""
        payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
        ]

        for payload in payloads:
            # Test in various input fields
            data = {"query": payload}
            response = client.post("/api/search", json=data, headers=test_user_headers)
            # Should not execute commands
            assert response.status_code in [200, 400, 422]


@pytest.mark.security
class TestDataExposure:
    """Test data exposure vulnerabilities."""

    def test_sensitive_data_in_response(self, client, test_user_headers):
        """Test for sensitive data exposure in responses."""
        response = client.get("/api/users/me", headers=test_user_headers)

        if response.status_code == 200:
            user_data = response.json()
            # Should not expose sensitive information
            sensitive_fields = ["hashed_password", "password", "secret_key"]
            for field in sensitive_fields:
                assert field not in user_data

    def test_error_information_disclosure(self, client):
        """Test for information disclosure in error messages."""
        # Try to access non-existent endpoint
        response = client.get("/api/nonexistent")

        # Should not reveal internal system information
        if response.status_code != 404:
            error_content = response.text.lower()
            sensitive_info = [
                "database",
                "sql",
                "stack trace",
                "internal server error",
                "file path",
            ]

            for info in sensitive_info:
                assert info not in error_content


@pytest.mark.security
class TestSessionManagement:
    """Test session management vulnerabilities."""

    def test_session_fixation(self, client):
        """Test session fixation vulnerability."""
        # This would require more complex testing with session tokens

    def test_session_timeout(self, client, test_user_headers):
        """Test session timeout."""
        # Test with expired token
        expired_token = "expired_token_here"
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/api/users/me", headers=headers)
        # Should reject expired tokens
        assert response.status_code == 401


@pytest.mark.security
class TestFileUpload:
    """Test file upload vulnerabilities."""

    def test_malicious_file_upload(self, client, test_user_headers):
        """Test malicious file upload."""
        malicious_files = [
            ("malicious.php", "<?php system($_GET['cmd']); ?>", "text/plain"),
            ("malicious.js", "alert('XSS')", "text/plain"),
            ("malicious.exe", b"fake_exe_content", "application/octet-stream"),
        ]

        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}

            response = client.post(
                "/api/documents/upload",
                files=files,
                headers=test_user_headers,
            )

            # Should reject malicious files
            assert response.status_code in [400, 422]


@pytest.mark.security
class TestAPIEndpoints:
    """Test API endpoint security."""

    def test_cors_configuration(self, client):
        """Test CORS configuration."""
        response = client.options("/api/users/me")

        # Check CORS headers
        cors_headers = response.headers.get("Access-Control-Allow-Origin")
        if cors_headers:
            # Should not allow all origins in production
            assert cors_headers != "*"

    def test_http_methods(self, client):
        """Test allowed HTTP methods."""
        # Test dangerous methods
        dangerous_methods = ["DELETE", "PUT", "PATCH"]

        for method in dangerous_methods:
            response = client.request(method, "/api/users/me")
            # Should not allow dangerous methods without proper authentication
            assert response.status_code in [401, 405, 403]
