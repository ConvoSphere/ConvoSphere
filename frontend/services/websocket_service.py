"""
WebSocket service for real-time communication.

This module provides WebSocket functionality for real-time chat,
notifications, and live updates.
"""

import json
import asyncio
from typing import Optional, Dict, Any, Callable, List
from websockets import connect
from websockets.exceptions import ConnectionClosed, WebSocketException
from nicegui import ui


class WebSocketService:
    """WebSocket service for real-time communication."""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        """
        Initialize WebSocket service.
        
        Args:
            base_url: WebSocket base URL
        """
        self.base_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 3
        self.reconnect_delay = 1.0
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.connection_handlers: List[Callable] = []
        self.disconnection_handlers: List[Callable] = []
        self.auth_token: Optional[str] = None
    
    def set_auth_token(self, token: str):
        """Set authentication token for WebSocket connection."""
        self.auth_token = token
    
    def clear_auth_token(self):
        """Clear authentication token."""
        self.auth_token = None
    
    def on_message(self, message_type: str):
        """Decorator to register message handlers."""
        def decorator(handler: Callable):
            if message_type not in self.message_handlers:
                self.message_handlers[message_type] = []
            self.message_handlers[message_type].append(handler)
            return handler
        return decorator
    
    def on_connect(self, handler: Callable):
        """Register connection handler."""
        self.connection_handlers.append(handler)
    
    def on_disconnect(self, handler: Callable):
        """Register disconnection handler."""
        self.disconnection_handlers.append(handler)
    
    async def connect(self, endpoint: str = "/ws"):
        """
        Connect to WebSocket server.
        
        Args:
            endpoint: WebSocket endpoint
        """
        if self.connected:
            return
        
        url = f"{self.base_url}{endpoint}"
        
        # Add auth token to URL if available
        if self.auth_token:
            separator = "&" if "?" in url else "?"
            url += f"{separator}token={self.auth_token}"
        
        for attempt in range(self.reconnect_attempts):
            try:
                self.websocket = await connect(url)
                self.connected = True
                
                # Notify connection handlers
                for handler in self.connection_handlers:
                    try:
                        await handler()
                    except Exception as e:
                        print(f"Connection handler error: {e}")
                
                # Start listening for messages
                await self._listen()
                break
                
            except WebSocketException as e:
                print(f"WebSocket connection attempt {attempt + 1} failed: {e}")
                if attempt < self.reconnect_attempts - 1:
                    await asyncio.sleep(self.reconnect_delay * (attempt + 1))
                else:
                    raise Exception(f"Failed to connect to WebSocket after {self.reconnect_attempts} attempts")
    
    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        
        self.connected = False
        
        # Notify disconnection handlers
        for handler in self.disconnection_handlers:
            try:
                await handler()
            except Exception as e:
                print(f"Disconnection handler error: {e}")
    
    async def send(self, message_type: str, data: Dict[str, Any]):
        """
        Send message through WebSocket.
        
        Args:
            message_type: Type of message
            data: Message data
        """
        if not self.connected or not self.websocket:
            raise Exception("WebSocket not connected")
        
        message = {
            "type": message_type,
            "data": data
        }
        
        try:
            await self.websocket.send(json.dumps(message))
        except ConnectionClosed:
            self.connected = False
            raise Exception("WebSocket connection closed")
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")
    
    async def _listen(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    message_data = data.get("data", {})
                    
                    if message_type in self.message_handlers:
                        for handler in self.message_handlers[message_type]:
                            try:
                                await handler(message_data)
                            except Exception as e:
                                print(f"Message handler error: {e}")
                    else:
                        print(f"No handler for message type: {message_type}")
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON message: {message}")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    
        except ConnectionClosed:
            self.connected = False
            print("WebSocket connection closed")
        except Exception as e:
            self.connected = False
            print(f"WebSocket error: {e}")
    
    # Convenience methods for specific message types
    async def send_chat_message(self, conversation_id: int, content: str, role: str = "user"):
        """Send chat message."""
        await self.send("chat_message", {
            "conversation_id": conversation_id,
            "content": content,
            "role": role
        })
    
    async def join_conversation(self, conversation_id: int):
        """Join conversation room."""
        await self.send("join_conversation", {
            "conversation_id": conversation_id
        })
    
    async def leave_conversation(self, conversation_id: int):
        """Leave conversation room."""
        await self.send("leave_conversation", {
            "conversation_id": conversation_id
        })
    
    async def send_typing_indicator(self, conversation_id: int, is_typing: bool):
        """Send typing indicator."""
        await self.send("typing_indicator", {
            "conversation_id": conversation_id,
            "is_typing": is_typing
        })


# Global WebSocket service instance
websocket_service = WebSocketService() 