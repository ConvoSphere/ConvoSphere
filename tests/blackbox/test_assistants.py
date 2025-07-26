"""
Blackbox tests for assistant management endpoints.

This module tests all assistant-related API endpoints including
CRUD operations, tool management, and assistant configuration.
"""

import pytest
from backend.appconftest import TEST_ASSISTANT_DATA


class TestAssistantManagementEndpoints:
    """Test assistant management endpoints."""
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_success(self, api_client, assertion_helper, authenticated_user):
        """Test successful assistant creation."""
        token, user_data = authenticated_user
        
        assistant_data = TEST_ASSISTANT_DATA.copy()
        assistant_data["name"] = "Test Assistant Blackbox"
        
        response = api_client.post("/assistants/", data=assistant_data, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "description", "system_prompt", "model", "temperature",
            "max_tokens", "status", "is_public", "is_template", "category", "tags",
            "tools_config", "tools_enabled", "creator_id", "version"
        ])
        
        # Verify assistant data
        assistant = response.json()
        assert assistant["name"] == assistant_data["name"]
        assert assistant["description"] == assistant_data["description"]
        assert assistant["model"] == assistant_data["model"]
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_invalid_data(self, api_client, assertion_helper, authenticated_user):
        """Test assistant creation with invalid data."""
        token, user_data = authenticated_user
        
        invalid_data = {
            "name": "",  # Empty name
            "description": "Test description",
            "model": "invalid-model",
            "temperature": 2.0,  # Invalid temperature
            "max_tokens": -1  # Invalid max tokens
        }
        
        response = api_client.post("/assistants/", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_unauthorized(self, api_client, assertion_helper):
        """Test assistant creation without authentication."""
        assistant_data = TEST_ASSISTANT_DATA.copy()
        
        response = api_client.post("/assistants/", data=assistant_data)
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistants_list(self, api_client, assertion_helper, authenticated_user):
        """Test getting list of assistants."""
        token, user_data = authenticated_user
        
        response = api_client.get("/assistants/", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "assistants", "total", "page", "size"
        ])
        assertion_helper.assert_list_response(response.json()["assistants"])
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistants_list_with_filters(self, api_client, assertion_helper, authenticated_user):
        """Test getting assistants list with filters."""
        token, user_data = authenticated_user
        
        # Test with status filter
        response = api_client.get("/assistants/", params={"status": "active"}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
        
        # Test with category filter
        response = api_client.get("/assistants/", params={"category": "general"}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
        
        # Test with pagination
        response = api_client.get("/assistants/", params={"page": 1, "size": 10}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_by_id(self, api_client, assertion_helper, test_assistant):
        """Test getting assistant by ID."""
        assistant_id = test_assistant["id"]
        
        response = api_client.get(f"/assistants/{assistant_id}")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "description", "system_prompt", "model", "temperature", 
            "max_tokens", "is_active", "created_at", "updated_at"
        ])
        assert response.json()["id"] == assistant_id
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_by_id_not_found(self, api_client, assertion_helper, authenticated_user):
        """Test getting non-existent assistant by ID."""
        token, user_data = authenticated_user
        
        response = api_client.get("/assistants/00000000-0000-0000-0000-000000000000", user_type="regular_user")
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_update_assistant(self, api_client, assertion_helper, test_assistant):
        """Test updating assistant."""
        assistant_id = test_assistant["id"]
        
        update_data = {
            "name": "Updated Assistant Name",
            "description": "Updated description",
            "temperature": 0.5
        }
        
        response = api_client.put(f"/assistants/{assistant_id}", data=update_data)
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "description", "system_prompt", "model", "temperature", 
            "max_tokens", "is_active", "created_at", "updated_at"
        ])
        
        # Verify updates
        updated_assistant = response.json()
        assert updated_assistant["name"] == update_data["name"]
        assert updated_assistant["description"] == update_data["description"]
        assert updated_assistant["temperature"] == update_data["temperature"]
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_delete_assistant(self, api_client, assertion_helper, authenticated_user):
        """Test deleting assistant."""
        token, user_data = authenticated_user
        
        # First create an assistant to delete
        assistant_data = TEST_ASSISTANT_DATA.copy()
        assistant_data["name"] = "Assistant to Delete"
        
        create_response = api_client.post("/assistants/", data=assistant_data, user_type="regular_user")
        assistant_id = create_response.json()["id"]
        
        # Delete the assistant
        response = api_client.delete(f"/assistants/{assistant_id}", user_type="regular_user")
        assertion_helper.assert_success_response(response, 204)
        
        # Verify assistant is deleted
        get_response = api_client.get(f"/assistants/{assistant_id}", user_type="regular_user")
        assertion_helper.assert_not_found(get_response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_activate_assistant(self, api_client, assertion_helper, test_assistant):
        """Test activating assistant."""
        assistant_id = test_assistant["id"]
        
        response = api_client.post(f"/assistants/{assistant_id}/activate")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "is_active"
        ])
        assert response.json()["is_active"] is True
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_deactivate_assistant(self, api_client, assertion_helper, test_assistant):
        """Test deactivating assistant."""
        assistant_id = test_assistant["id"]
        
        response = api_client.post(f"/assistants/{assistant_id}/deactivate")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "is_active"
        ])
        assert response.json()["is_active"] is False
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_public_assistants(self, api_client, assertion_helper):
        """Test getting public assistants."""
        response = api_client.get("/assistants/public")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_status_list(self, api_client, assertion_helper, authenticated_user):
        """Test getting assistant status list."""
        token, user_data = authenticated_user
        
        response = api_client.get("/assistants/status/list", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_default_assistant(self, api_client, assertion_helper, authenticated_user):
        """Test getting default assistant."""
        token, user_data = authenticated_user
        
        response = api_client.get("/assistants/default", user_type="regular_user")
        
        # This endpoint might return 404 if no default is set
        if response.status_code == 200:
            assertion_helper.assert_response_structure(response.json(), [
                "id", "name", "description", "system_prompt", "model"
            ])
        else:
            assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_default_assistant_id(self, api_client, assertion_helper, authenticated_user):
        """Test getting default assistant ID."""
        token, user_data = authenticated_user
        
        response = api_client.get("/assistants/default/id", user_type="regular_user")
        
        # This endpoint might return 404 if no default is set
        if response.status_code == 200:
            assertion_helper.assert_response_structure(response.json(), ["id"])
        else:
            assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_set_default_assistant(self, api_client, assertion_helper, test_assistant):
        """Test setting default assistant."""
        assistant_id = test_assistant["id"]
        
        response = api_client.post("/assistants/default/set", data={"assistant_id": assistant_id})
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "name", "is_default"
        ])
        assert response.json()["is_default"] is True


class TestAssistantTools:
    """Test assistant tool management."""
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_tools(self, api_client, assertion_helper, test_assistant):
        """Test getting assistant tools."""
        assistant_id = test_assistant["id"]
        
        response = api_client.get(f"/assistants/{assistant_id}/tools")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_add_tool_to_assistant(self, api_client, assertion_helper, test_assistant):
        """Test adding tool to assistant."""
        assistant_id = test_assistant["id"]
        
        # First get available tools
        tools_response = api_client.get("/tools/")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]
            
            tool_data = {
                "tool_id": tool_id,
                "enabled": True
            }
            
            response = api_client.post(f"/assistants/{assistant_id}/tools", data=tool_data)
            
            # This endpoint might return different status codes depending on implementation
            assert response.status_code in [200, 201, 400], \
                f"Unexpected status code: {response.status_code}"
        else:
            pytest.skip("No tools available for testing")
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_tool(self, api_client, assertion_helper, test_assistant):
        """Test getting specific assistant tool."""
        assistant_id = test_assistant["id"]
        
        # First get assistant tools
        tools_response = api_client.get(f"/assistants/{assistant_id}/tools")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]
            
            response = api_client.get(f"/assistants/{assistant_id}/tools/{tool_id}")
            
            assertion_helper.assert_success_response(response, 200)
            assertion_helper.assert_response_structure(response.json(), [
                "id", "name", "description", "enabled"
            ])
        else:
            pytest.skip("No tools available for testing")
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_get_assistant_tool_not_found(self, api_client, assertion_helper, test_assistant):
        """Test getting non-existent assistant tool."""
        assistant_id = test_assistant["id"]
        
        response = api_client.get(f"/assistants/{assistant_id}/tools/00000000-0000-0000-0000-000000000000")
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_update_assistant_tool(self, api_client, assertion_helper, test_assistant):
        """Test updating assistant tool."""
        assistant_id = test_assistant["id"]
        
        # First get assistant tools
        tools_response = api_client.get(f"/assistants/{assistant_id}/tools")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]
            
            update_data = {
                "enabled": False
            }
            
            response = api_client.put(f"/assistants/{assistant_id}/tools/{tool_id}", data=update_data)
            
            assertion_helper.assert_success_response(response, 200)
            assertion_helper.assert_response_structure(response.json(), [
                "id", "name", "description", "enabled"
            ])
            assert response.json()["enabled"] is False
        else:
            pytest.skip("No tools available for testing")
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_remove_tool_from_assistant(self, api_client, assertion_helper, test_assistant):
        """Test removing tool from assistant."""
        assistant_id = test_assistant["id"]
        
        # First get assistant tools
        tools_response = api_client.get(f"/assistants/{assistant_id}/tools")
        if tools_response.status_code == 200 and tools_response.json():
            tool_id = tools_response.json()[0]["id"]
            
            response = api_client.delete(f"/assistants/{assistant_id}/tools/{tool_id}")
            
            assertion_helper.assert_success_response(response, 204)
            
            # Verify tool is removed
            get_response = api_client.get(f"/assistants/{assistant_id}/tools/{tool_id}")
            assertion_helper.assert_not_found(get_response)
        else:
            pytest.skip("No tools available for testing")


class TestAssistantValidation:
    """Test assistant data validation."""
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_missing_required_fields(self, api_client, assertion_helper, authenticated_user):
        """Test creating assistant with missing required fields."""
        token, user_data = authenticated_user
        
        # Missing name
        invalid_data = {
            "description": "Test description",
            "model": "gpt-4"
        }
        
        response = api_client.post("/assistants/", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_invalid_model(self, api_client, assertion_helper, authenticated_user):
        """Test creating assistant with invalid model."""
        token, user_data = authenticated_user
        
        invalid_data = TEST_ASSISTANT_DATA.copy()
        invalid_data["model"] = "invalid-model"
        
        response = api_client.post("/assistants/", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_invalid_temperature(self, api_client, assertion_helper, authenticated_user):
        """Test creating assistant with invalid temperature."""
        token, user_data = authenticated_user
        
        invalid_data = TEST_ASSISTANT_DATA.copy()
        invalid_data["temperature"] = 2.5  # Should be between 0 and 2
        
        response = api_client.post("/assistants/", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_create_assistant_invalid_max_tokens(self, api_client, assertion_helper, authenticated_user):
        """Test creating assistant with invalid max tokens."""
        token, user_data = authenticated_user
        
        invalid_data = TEST_ASSISTANT_DATA.copy()
        invalid_data["max_tokens"] = -1  # Should be positive
        
        response = api_client.post("/assistants/", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.assistants
    def test_update_assistant_invalid_data(self, api_client, assertion_helper, test_assistant):
        """Test updating assistant with invalid data."""
        assistant_id = test_assistant["id"]
        
        invalid_data = {
            "temperature": 3.0,  # Invalid temperature
            "max_tokens": 0  # Invalid max tokens
        }
        
        response = api_client.put(f"/assistants/{assistant_id}", data=invalid_data)
        assertion_helper.assert_error_response(response, 422) 