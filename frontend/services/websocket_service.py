"""
WebSocket service for real-time communication.

This module provides WebSocket functionality for real-time chat
and notifications in the AI Assistant Platform.
"""

import json
import asyncio
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from datetime import datetime

try:
    import websockets
except ImportError:
    websockets = None


@dataclass
class WebSocketMessage:
    """WebSocket message data model."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    conversation_id: Optional[str] = None


class WebSocketService:
    """WebSocket service for real-time communication."""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        """Initialize the WebSocket service."""
        self.base_url = base_url.rstrip("/")
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.conversation_id: Optional[str] = None
        self.message_handlers: List[Callable[[WebSocketMessage], None]] = []
        self.error_handlers: List[Callable[[str], None]] = []
        self.connection_handlers: List[Callable[[bool], None]] = []
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0
        
    async def connect(self, conversation_id: str, token: str) -> bool:
        """
        Connect to WebSocket for a specific conversation.
        
        Args:
            conversation_id: Conversation ID to connect to
            token: Authentication token
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not websockets:
            print("WebSocket support not available")
            return False
        
        try:
            # Close existing connection
            await self.disconnect()
            
            # Build WebSocket URL
            ws_url = f"{self.base_url}/api/v1/chat/ws/{conversation_id}"
            
            # Connect with authentication
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={"Authorization": f"Bearer {token}"}
            )
            
            self.conversation_id = conversation_id
            self.is_connected = True
            self.reconnect_attempts = 0
            
            # Notify connection handlers
            for handler in self.connection_handlers:
                try:
                    handler(True)
                except Exception as e:
                    print(f"Connection handler error: {e}")
            
            # Start message listener
            asyncio.create_task(self._listen_for_messages())
            
            print(f"WebSocket connected to conversation {conversation_id}")
            return True
            
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
                self.is_connected = False
                self.conversation_id = None
                
                # Notify connection handlers
                for handler in self.connection_handlers:
                    try:
                        handler(False)
                    except Exception as e:
                        print(f"Connection handler error: {e}")
    
    async def send_message(self, content: str, message_type: str = "text") -> bool:
        """
        Send message through WebSocket.
        
        Args:
            content: Message content
            message_type: Type of message (text, tool, etc.)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            message = {
                "type": "message",
                "content": content,
                "message_type": message_type,
                "conversation_id": self.conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")
            await self._handle_connection_error()
            return False
    
    async def send_tool_request(self, tool_id: str, arguments: Dict[str, Any]) -> bool:
        """
        Send tool execution request.
        
        Args:
            tool_id: Tool ID to execute
            arguments: Tool arguments
            
        Returns:
            bool: True if request sent successfully, False otherwise
        """
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            message = {
                "type": "tool_request",
                "tool_id": tool_id,
                "arguments": arguments,
                "conversation_id": self.conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            print(f"Error sending tool request: {e}")
            await self._handle_connection_error()
            return False
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                try:
                    # Parse message
                    data = json.loads(message)
                    ws_message = WebSocketMessage(
                        type=data.get("type", "unknown"),
                        data=data.get("data", {}),
                        timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                        conversation_id=data.get("conversation_id")
                    )
                    
                    # Handle message
                    await self._handle_message(ws_message)
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing WebSocket message: {e}")
                except Exception as e:
                    print(f"Error handling WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            await self._handle_connection_error()
        except Exception as e:
            print(f"WebSocket listener error: {e}")
            await self._handle_connection_error()
    
    async def _handle_message(self, message: WebSocketMessage):
        """Handle incoming WebSocket message."""
        # Notify message handlers
        for handler in self.message_handlers:
            try:
                handler(message)
            except Exception as e:
                print(f"Message handler error: {e}")
    
    async def _handle_connection_error(self):
        """Handle WebSocket connection errors."""
        self.is_connected = False
        
        # Notify error handlers
        for handler in self.error_handlers:
            try:
                handler("WebSocket connection lost")
            except Exception as e:
                print(f"Error handler error: {e}")
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            await self._attempt_reconnect()
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect to WebSocket."""
        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # Exponential backoff
        
        print(f"Attempting WebSocket reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts} in {delay}s")
        
        await asyncio.sleep(delay)
        
        # TODO: Implement reconnection logic
        # This would require storing the connection parameters
        print("Reconnection not implemented yet")
    
    def add_message_handler(self, handler: Callable[[WebSocketMessage], None]):
        """Add message handler."""
        self.message_handlers.append(handler)
    
    def add_error_handler(self, handler: Callable[[str], None]):
        """Add error handler."""
        self.error_handlers.append(handler)
    
    def add_connection_handler(self, handler: Callable[[bool], None]):
        """Add connection status handler."""
        self.connection_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable[[WebSocketMessage], None]):
        """Remove message handler."""
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
    
    def remove_error_handler(self, handler: Callable[[str], None]):
        """Remove error handler."""
        if handler in self.error_handlers:
            self.error_handlers.remove(handler)
    
    def remove_connection_handler(self, handler: Callable[[bool], None]):
        """Remove connection status handler."""
        if handler in self.connection_handlers:
            self.connection_handlers.remove(handler)


# Global WebSocket service instance
websocket_service = WebSocketService() 