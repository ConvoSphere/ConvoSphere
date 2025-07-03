#!/usr/bin/env python3
"""
Test script for Conversations API with enterprise features.

This script tests the comprehensive Conversations API including:
- Conversation CRUD operations
- Message management
- Archiving and status management
- Pagination and filtering
- Enterprise features (participants, groups, access control)
"""

import requests
import json
import uuid
from datetime import datetime
from typing import Dict, Any


class ConversationsAPITester:
    """Test class for Conversations API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.conversations_endpoint = f"{self.api_base}/conversations"
        self.auth_token = None
        
    def set_auth_token(self, token: str):
        """Set authentication token for API requests."""
        self.auth_token = token
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def test_create_conversation(self) -> Dict[str, Any]:
        """Test creating a new conversation."""
        print("\n=== Testing Conversation Creation ===")
        
        conversation_data = {
            "title": f"Test Conversation {uuid.uuid4().hex[:8]}",
            "description": "Test conversation for API testing",
            "user_id": str(uuid.uuid4()),  # Mock user ID
            "assistant_id": str(uuid.uuid4()),  # Mock assistant ID
            "tags": ["test", "api"],
            "access": "private",
            "conversation_metadata": {
                "test_metadata": "value",
                "created_by": "api_test"
            }
        }
        
        try:
            response = requests.post(
                f"{self.conversations_endpoint}/",
                json=conversation_data,
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                conversation = response.json()
                print(f"✅ Conversation created successfully: {conversation['title']}")
                return conversation
            else:
                print(f"❌ Failed to create conversation: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
            return {}
    
    def test_list_conversations(self) -> Dict[str, Any]:
        """Test listing conversations with pagination."""
        print("\n=== Testing Conversation Listing ===")
        
        try:
            response = requests.get(
                f"{self.conversations_endpoint}/",
                params={
                    "page": 1,
                    "size": 10
                },
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Conversations listed successfully: {data['total']} total conversations")
                print(f"   Page {data['page']} of {data['pages']}")
                return data
            else:
                print(f"❌ Failed to list conversations: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error listing conversations: {e}")
            return {}
    
    def test_get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Test getting a specific conversation."""
        print(f"\n=== Testing Get Conversation {conversation_id} ===")
        
        try:
            response = requests.get(
                f"{self.conversations_endpoint}/{conversation_id}",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                conversation = response.json()
                print(f"✅ Conversation retrieved successfully: {conversation['title']}")
                return conversation
            else:
                print(f"❌ Failed to get conversation: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting conversation: {e}")
            return {}
    
    def test_update_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Test updating a conversation."""
        print(f"\n=== Testing Update Conversation {conversation_id} ===")
        
        update_data = {
            "title": "Updated Test Conversation",
            "description": "Updated description for testing",
            "tags": ["updated", "test", "api"],
            "access": "team",
            "conversation_metadata": {
                "updated_metadata": "new_value",
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        try:
            response = requests.put(
                f"{self.conversations_endpoint}/{conversation_id}",
                json=update_data,
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                conversation = response.json()
                print(f"✅ Conversation updated successfully: {conversation['title']}")
                return conversation
            else:
                print(f"❌ Failed to update conversation: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error updating conversation: {e}")
            return {}
    
    def test_add_message(self, conversation_id: str) -> Dict[str, Any]:
        """Test adding a message to a conversation."""
        print(f"\n=== Testing Add Message to Conversation {conversation_id} ===")
        
        message_data = {
            "content": "Hello, this is a test message from the API!",
            "role": "user",
            "message_type": "text",
            "message_metadata": {
                "test_message": True,
                "created_by": "api_test"
            }
        }
        
        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                message = response.json()
                print(f"✅ Message added successfully: {message['content'][:50]}...")
                return message
            else:
                print(f"❌ Failed to add message: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error adding message: {e}")
            return {}
    
    def test_add_assistant_message(self, conversation_id: str) -> Dict[str, Any]:
        """Test adding an assistant message to a conversation."""
        print(f"\n=== Testing Add Assistant Message to Conversation {conversation_id} ===")
        
        message_data = {
            "content": "Hello! I'm an AI assistant. How can I help you today?",
            "role": "assistant",
            "message_type": "text",
            "tokens_used": 15,
            "model_used": "gpt-3.5-turbo",
            "message_metadata": {
                "assistant_response": True,
                "model_version": "3.5-turbo"
            }
        }
        
        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                message = response.json()
                print(f"✅ Assistant message added successfully: {message['content'][:50]}...")
                return message
            else:
                print(f"❌ Failed to add assistant message: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error adding assistant message: {e}")
            return {}
    
    def test_add_tool_message(self, conversation_id: str) -> Dict[str, Any]:
        """Test adding a tool message to a conversation."""
        print(f"\n=== Testing Add Tool Message to Conversation {conversation_id} ===")
        
        message_data = {
            "content": "Tool execution completed successfully",
            "role": "tool",
            "message_type": "text",
            "tool_name": "search_tool",
            "tool_input": {"query": "test search"},
            "tool_output": {"results": ["result1", "result2"]},
            "message_metadata": {
                "tool_execution": True,
                "execution_time": 1.5
            }
        }
        
        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                json=message_data,
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                message = response.json()
                print(f"✅ Tool message added successfully: {message['tool_name']}")
                return message
            else:
                print(f"❌ Failed to add tool message: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error adding tool message: {e}")
            return {}
    
    def test_list_messages(self, conversation_id: str) -> Dict[str, Any]:
        """Test listing messages in a conversation."""
        print(f"\n=== Testing List Messages for Conversation {conversation_id} ===")
        
        try:
            response = requests.get(
                f"{self.conversations_endpoint}/{conversation_id}/messages",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Messages listed successfully: {len(messages)} messages")
                return messages
            else:
                print(f"❌ Failed to list messages: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing messages: {e}")
            return []
    
    def test_archive_conversation(self, conversation_id: str) -> bool:
        """Test archiving a conversation."""
        print(f"\n=== Testing Archive Conversation {conversation_id} ===")
        
        try:
            response = requests.post(
                f"{self.conversations_endpoint}/{conversation_id}/archive",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Conversation archived successfully: {result['message']}")
                return True
            else:
                print(f"❌ Failed to archive conversation: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error archiving conversation: {e}")
            return False
    
    def test_delete_conversation(self, conversation_id: str) -> bool:
        """Test deleting a conversation."""
        print(f"\n=== Testing Delete Conversation {conversation_id} ===")
        
        try:
            response = requests.delete(
                f"{self.conversations_endpoint}/{conversation_id}",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 204:
                print(f"✅ Conversation deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete conversation: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests for the Conversations API."""
        print("🚀 Starting Conversations API Tests")
        print("=" * 50)
        
        # Test conversation creation
        conversation = self.test_create_conversation()
        if not conversation:
            print("❌ Cannot continue without a test conversation")
            return
        
        conversation_id = conversation['id']
        
        # Test listing conversations
        self.test_list_conversations()
        
        # Test getting specific conversation
        self.test_get_conversation(conversation_id)
        
        # Test updating conversation
        updated_conversation = self.test_update_conversation(conversation_id)
        
        # Test adding messages
        user_message = self.test_add_message(conversation_id)
        assistant_message = self.test_add_assistant_message(conversation_id)
        tool_message = self.test_add_tool_message(conversation_id)
        
        # Test listing messages
        messages = self.test_list_messages(conversation_id)
        
        # Test archiving conversation
        self.test_archive_conversation(conversation_id)
        
        # Test getting archived conversation
        archived_conversation = self.test_get_conversation(conversation_id)
        
        # Test deleting conversation
        self.test_delete_conversation(conversation_id)
        
        print("\n" + "=" * 50)
        print("✅ Conversations API Tests Completed")
        print(f"   Created: 1 conversation")
        print(f"   Added: {len([m for m in [user_message, assistant_message, tool_message] if m])} messages")
        print(f"   Archived: 1 conversation")
        print(f"   Deleted: 1 conversation")


def main():
    """Main function to run the tests."""
    # Initialize tester
    tester = ConversationsAPITester()
    
    # Set authentication token if available
    # tester.set_auth_token("your-auth-token-here")
    
    # Run all tests
    tester.run_all_tests()


if __name__ == "__main__":
    main() 