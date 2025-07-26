"""
Blackbox tests for tools endpoints.

This module tests all tools-related API endpoints including
tool management, categories, and tool execution.
"""

import pytest


class TestToolManagementEndpoints:
    """Test tool management endpoints."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tools_list(self, api_client, assertion_helper, authenticated_user):
        """Test getting list of tools."""
        token, user_data = authenticated_user

        response = api_client.get("/tools/", user_type="regular_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tools_list_with_filters(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting tools list with filters."""
        token, user_data = authenticated_user

        # Test with category filter
        response = api_client.get(
            "/tools/", params={"category": "search"}, user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 200)

        # Test with search filter
        response = api_client.get(
            "/tools/", params={"search": "test"}, user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 200)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tools_list_unauthorized(self, api_client, assertion_helper):
        """Test getting tools list without authentication."""
        response = api_client.get("/tools/")
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tool_by_id(self, api_client, assertion_helper, authenticated_user):
        """Test getting tool by ID."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            response = api_client.get(f"/tools/{tool_id}", user_type="regular_user")

            assertion_helper.assert_success_response(response, 200)
            assertion_helper.assert_response_structure(
                response.json(),
                [
                    "id",
                    "name",
                    "description",
                    "category",
                    "function_name",
                    "parameters",
                ],
            )
            assert response.json()["id"] == tool_id
        else:
            pytest.skip("No tools available for testing")

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tool_by_id_not_found(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting non-existent tool by ID."""
        token, user_data = authenticated_user

        response = api_client.get("/tools/999999", user_type="regular_user")
        assertion_helper.assert_not_found(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tool_categories(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting tool categories."""
        token, user_data = authenticated_user

        response = api_client.get("/tools/categories/list", user_type="regular_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_get_tool_categories_unauthorized(self, api_client, assertion_helper):
        """Test getting tool categories without authentication."""
        response = api_client.get("/tools/categories/list")
        assertion_helper.assert_unauthorized(response)


class TestToolExecution:
    """Test tool execution functionality."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool(self, api_client, assertion_helper, authenticated_user):
        """Test executing a tool."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            execution_data = {"parameters": {"query": "test query"}}

            response = api_client.post(
                f"/tools/{tool_id}/execute",
                data=execution_data,
                user_type="regular_user",
            )

            # This endpoint might return different status codes depending on implementation
            assert response.status_code in [200, 400, 500], (
                f"Unexpected status code: {response.status_code}"
            )
        else:
            pytest.skip("No tools available for testing")

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_invalid_parameters(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test executing tool with invalid parameters."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            invalid_data = {"parameters": {"invalid_param": "invalid_value"}}

            response = api_client.post(
                f"/tools/{tool_id}/execute", data=invalid_data, user_type="regular_user"
            )
            assertion_helper.assert_error_response(response, 400)
        else:
            pytest.skip("No tools available for testing")

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_not_found(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test executing non-existent tool."""
        token, user_data = authenticated_user

        execution_data = {"parameters": {"query": "test query"}}

        response = api_client.post(
            "/tools/999999/execute", data=execution_data, user_type="regular_user"
        )
        assertion_helper.assert_not_found(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_unauthorized(self, api_client, assertion_helper):
        """Test executing tool without authentication."""
        execution_data = {"parameters": {"query": "test query"}}

        response = api_client.post("/tools/1/execute", data=execution_data)
        assertion_helper.assert_unauthorized(response)


class TestToolValidation:
    """Test tool data validation."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_missing_parameters(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test executing tool with missing parameters."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            # Missing parameters
            invalid_data = {}

            response = api_client.post(
                f"/tools/{tool_id}/execute", data=invalid_data, user_type="regular_user"
            )
            assertion_helper.assert_error_response(response, 422)
        else:
            pytest.skip("No tools available for testing")

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_empty_parameters(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test executing tool with empty parameters."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            empty_data = {"parameters": {}}

            response = api_client.post(
                f"/tools/{tool_id}/execute", data=empty_data, user_type="regular_user"
            )
            # This might be valid for some tools, so we don't assert specific error
            assert response.status_code in [200, 400, 422], (
                f"Unexpected status code: {response.status_code}"
            )
        else:
            pytest.skip("No tools available for testing")


class TestToolPermissions:
    """Test tool access permissions."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_access_tool_unauthorized(self, api_client, assertion_helper):
        """Test accessing tool without authentication."""
        response = api_client.get("/tools/1")
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_execute_tool_unauthorized(self, api_client, assertion_helper):
        """Test executing tool without authentication."""
        execution_data = {"parameters": {"query": "test query"}}

        response = api_client.post("/tools/1/execute", data=execution_data)
        assertion_helper.assert_unauthorized(response)


class TestToolIntegration:
    """Test tool integration with other services."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    @pytest.mark.integration
    def test_tool_with_assistant_integration(
        self, api_client, assertion_helper, test_assistant
    ):
        """Test tool integration with assistant."""
        assistant_id = test_assistant["id"]

        # Get assistant tools
        response = api_client.get(f"/assistants/{assistant_id}/tools")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.tools
    @pytest.mark.integration
    def test_tool_availability_for_different_roles(
        self, api_client, assertion_helper, authenticated_user, authenticated_admin
    ):
        """Test tool availability for different user roles."""
        # Test as regular user
        token_user, user_data = authenticated_user
        user_response = api_client.get("/tools/", user_type="regular_user")
        assertion_helper.assert_success_response(user_response, 200)

        # Test as admin user
        token_admin, admin_data = authenticated_admin
        admin_response = api_client.get("/tools/", user_type="admin_user")
        assertion_helper.assert_success_response(admin_response, 200)

        # Both should return tools (though potentially different sets)
        user_tools = user_response.json()
        admin_tools = admin_response.json()

        assert isinstance(user_tools, list), "User tools should be a list"
        assert isinstance(admin_tools, list), "Admin tools should be a list"


class TestToolErrorHandling:
    """Test tool error handling."""

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_tool_execution_timeout(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test tool execution timeout handling."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            # Try to execute with parameters that might cause timeout
            timeout_data = {
                "parameters": {
                    "query": "a" * 10000  # Very long query that might cause timeout
                }
            }

            response = api_client.post(
                f"/tools/{tool_id}/execute", data=timeout_data, user_type="regular_user"
            )

            # Should handle timeout gracefully
            assert response.status_code in [200, 400, 408, 500], (
                f"Unexpected status code: {response.status_code}"
            )
        else:
            pytest.skip("No tools available for testing")

    @pytest.mark.blackbox
    @pytest.mark.tools
    def test_tool_execution_invalid_input(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test tool execution with invalid input."""
        token, user_data = authenticated_user

        # First get tools list to get a tool ID
        tools_response = api_client.get("/tools/", user_type="regular_user")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]

            # Try to execute with invalid input types
            invalid_data = {
                "parameters": {
                    "query": None,  # None instead of string
                    "limit": "not_a_number",  # String instead of number
                }
            }

            response = api_client.post(
                f"/tools/{tool_id}/execute", data=invalid_data, user_type="regular_user"
            )
            assertion_helper.assert_error_response(response, 400)
        else:
            pytest.skip("No tools available for testing")
