#!/usr/bin/env python3
"""
Frontend-Backend Integration Test Script

This script tests the communication between the frontend and backend
to ensure all API endpoints are working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.api import APIClient
from services.assistant_service import AssistantService
from services.auth_service import AuthService
from services.conversation_service import ConversationService
from services.knowledge_service import KnowledgeService
from services.tool_service import ToolService


class IntegrationTester:
    """Integration tester for frontend-backend communication."""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.api_client = APIClient(backend_url)
        self.auth_service = AuthService(self.api_client)
        self.assistant_service = AssistantService(self.api_client)
        self.conversation_service = ConversationService(self.api_client)
        self.tool_service = ToolService(self.api_client)
        self.knowledge_service = KnowledgeService(self.api_client)

        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append(
            {
                "test": test_name,
                "success": success,
                "details": details,
            },
        )

    async def test_health_check(self):
        """Test health check endpoint."""
        try:
            response = await self.api_client.health_check()
            if response.success:
                self.log_test(
                    "Health Check",
                    True,
                    f"Status: {response.data.get('status', 'unknown')}",
                )
            else:
                self.log_test("Health Check", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")

    async def test_auth_endpoints(self):
        """Test authentication endpoints."""
        # Test registration
        try:
            test_user = {
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPassword123!",
                "full_name": "Test User",
            }
            response = await self.auth_service.register(test_user)
            if response.success:
                self.log_test("User Registration", True)
            else:
                self.log_test("User Registration", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")

        # Test login
        try:
            response = await self.auth_service.login(
                "test@example.com", "TestPassword123!",
            )
            if response.success:
                self.log_test("User Login", True)
                # Set token for subsequent tests
                if hasattr(response, "data") and response.data:
                    token = response.data.get("access_token")
                    if token:
                        self.api_client.set_token(token)
            else:
                self.log_test("User Login", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")

    async def test_assistant_endpoints(self):
        """Test assistant endpoints."""
        try:
            response = await self.assistant_service.get_assistants()
            if response.success:
                assistants = response.data or []
                self.log_test(
                    "Get Assistants", True, f"Found {len(assistants)} assistants",
                )
            else:
                self.log_test("Get Assistants", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("Get Assistants", False, f"Exception: {str(e)}")

    async def test_conversation_endpoints(self):
        """Test conversation endpoints."""
        try:
            response = await self.conversation_service.get_conversations()
            if response.success:
                conversations = response.data or []
                self.log_test(
                    "Get Conversations",
                    True,
                    f"Found {len(conversations)} conversations",
                )
            else:
                self.log_test("Get Conversations", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("Get Conversations", False, f"Exception: {str(e)}")

    async def test_tool_endpoints(self):
        """Test tool endpoints."""
        try:
            response = await self.tool_service.get_tools()
            if response.success:
                tools = response.data or []
                self.log_test("Get Tools", True, f"Found {len(tools)} tools")
            else:
                self.log_test("Get Tools", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("Get Tools", False, f"Exception: {str(e)}")

    async def test_knowledge_endpoints(self):
        """Test knowledge base endpoints."""
        try:
            response = await self.knowledge_service.get_documents()
            if response.success:
                documents = response.data or []
                self.log_test(
                    "Get Documents", True, f"Found {len(documents)} documents",
                )
            else:
                self.log_test("Get Documents", False, f"Error: {response.error}")
        except Exception as e:
            self.log_test("Get Documents", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Frontend-Backend Integration Tests")
        print("=" * 50)

        # Test basic connectivity
        await self.test_health_check()

        # Test authentication
        print("\n🔐 Testing Authentication Endpoints")
        print("-" * 30)
        await self.test_auth_endpoints()

        # Test assistants
        print("\n🤖 Testing Assistant Endpoints")
        print("-" * 30)
        await self.test_assistant_endpoints()

        # Test conversations
        print("\n💬 Testing Conversation Endpoints")
        print("-" * 30)
        await self.test_conversation_endpoints()

        # Test tools
        print("\n🔧 Testing Tool Endpoints")
        print("-" * 30)
        await self.test_tool_endpoints()

        # Test knowledge base
        print("\n📚 Testing Knowledge Base Endpoints")
        print("-" * 30)
        await self.test_knowledge_endpoints()

        # Summary
        print("\n" + "=" * 50)
        print("📊 Integration Test Summary")
        print("=" * 50)

        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            print("\n🎉 All integration tests passed!")
        else:
            print("\n⚠️  Some tests failed. Check the details above.")

        return passed == total


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Frontend-Backend Integration Tests")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend API URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    tester = IntegrationTester(args.backend_url)
    success = await tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
