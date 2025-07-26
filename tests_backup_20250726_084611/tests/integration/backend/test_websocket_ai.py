#!/usr/bin/env python3
"""
Test script to verify WebSocket AI functionality.
This script tests the WebSocket endpoint to ensure it can receive AI model responses.
"""

import asyncio
import json
import websockets
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws"
LOGIN_URL = f"{BACKEND_URL}/api/v1/auth/login"
CONVERSATIONS_URL = f"{BACKEND_URL}/api/v1/conversations"

# Test credentials - using a test user
TEST_USER = {
    "email": "test@example.com",
    "password": "test123"
}

# Known IDs from the database
TEST_USER_ID = "869c561e-aca1-4b3f-b5c4-1ef758475c67"
TEST_ASSISTANT_ID = "74a01673-1ee1-4ae4-bb32-cda3424dc4a8"

async def get_auth_token():
    """Get authentication token by logging in."""
    try:
        response = requests.post(LOGIN_URL, json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

async def create_conversation(token):
    """Create a test conversation."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        conversation_data = {
            "title": "WebSocket AI Test",
            "user_id": TEST_USER_ID,
            "assistant_id": TEST_ASSISTANT_ID
        }
        
        response = requests.post(CONVERSATIONS_URL, json=conversation_data, headers=headers)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Conversation created: {data['id']}")
            return data["id"]
        else:
            print(f"❌ Failed to create conversation: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return None

async def test_websocket_ai_response():
    """Test WebSocket AI response functionality."""
    print("🔍 Testing WebSocket AI Response Functionality")
    print("=" * 50)
    
    # Step 1: Get authentication token
    print("1. Getting authentication token...")
    token = await get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    print(f"✅ Authentication token obtained: {token[:20]}...")
    
    # Step 2: Create a conversation
    print("\n2. Creating test conversation...")
    conversation_id = await create_conversation(token)
    if not conversation_id:
        print("❌ Failed to create conversation")
        return False
    
    # Step 3: Connect to WebSocket for the conversation
    print(f"\n3. Connecting to WebSocket for conversation {conversation_id}...")
    ws_url_with_token = f"{WS_URL}/{conversation_id}?token={token}"
    
    try:
        async with websockets.connect(ws_url_with_token) as websocket:
            print("✅ WebSocket connection established")
            
            # Step 4: Wait for connection confirmation
            print("\n4. Waiting for connection confirmation...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "connection_established":
                print("✅ Connection confirmed by server")
                print(f"   User ID: {response_data['data']['user_id']}")
                print(f"   Conversation ID: {response_data['data']['conversation_id']}")
                print(f"   Message: {response_data['data']['message']}")
            else:
                print(f"❌ Unexpected response: {response_data}")
                return False
            
            # Step 5: Send a test message
            print("\n5. Sending test message to AI...")
            test_message = {
                "type": "message",
                "data": {
                    "content": "Hello! Can you tell me a short joke?",
                    "knowledgeContext": {
                        "enabled": False
                    }
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent")
            
            # Step 6: Wait for AI response
            print("\n6. Waiting for AI response...")
            print("   (This may take a few seconds...)")
            
            try:
                # Wait for response with timeout
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "message":
                    ai_content = response_data["data"]["content"]
                    ai_role = response_data["data"]["role"]
                    message_id = response_data["data"]["id"]
                    
                    print("✅ AI Response received!")
                    print(f"   Message ID: {message_id}")
                    print(f"   Role: {ai_role}")
                    print(f"   Content: {ai_content[:100]}{'...' if len(ai_content) > 100 else ''}")
                    
                    # Check if it's a meaningful response
                    if len(ai_content.strip()) > 10:
                        print("✅ AI provided a meaningful response")
                        return True
                    else:
                        print("❌ AI response seems too short")
                        return False
                        
                elif response_data.get("type") == "error":
                    print(f"❌ Error response: {response_data['data']['message']}")
                    return False
                else:
                    print(f"❌ Unexpected response type: {response_data.get('type')}")
                    print(f"   Full response: {response_data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for AI response")
                return False
            
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 403:
            print("❌ WebSocket connection rejected (403 Forbidden)")
            print("   This might be due to invalid token or authentication issues")
        else:
            print(f"❌ WebSocket connection failed with status {e.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def test_websocket_ping_pong():
    """Test WebSocket ping-pong functionality."""
    print("\n🔍 Testing WebSocket Ping-Pong")
    print("=" * 30)
    
    token = await get_auth_token()
    if not token:
        return False
    
    ws_url_with_token = f"{WS_URL}/?token={token}"
    
    try:
        async with websockets.connect(ws_url_with_token) as websocket:
            # Wait for connection confirmation
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") != "connection_established":
                print("❌ Connection not established")
                return False
            
            # Send ping
            ping_message = {
                "type": "ping",
                "data": {}
            }
            
            await websocket.send(json.dumps(ping_message))
            print("✅ Ping sent")
            
            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "pong":
                print("✅ Pong received")
                print(f"   Timestamp: {response_data['data']['timestamp']}")
                return True
            else:
                print(f"❌ Unexpected ping-pong response: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ Ping-pong test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting WebSocket AI Response Tests")
    print("=" * 60)
    
    # Test 1: Basic WebSocket connection and AI response
    ai_test_result = await test_websocket_ai_response()
    
    # Test 2: Ping-pong functionality
    ping_pong_result = await test_websocket_ping_pong()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"AI Response Test: {'✅ PASSED' if ai_test_result else '❌ FAILED'}")
    print(f"Ping-Pong Test:  {'✅ PASSED' if ping_pong_result else '❌ FAILED'}")
    
    if ai_test_result and ping_pong_result:
        print("\n🎉 All tests passed! WebSocket AI functionality is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the logs above for details.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1) 