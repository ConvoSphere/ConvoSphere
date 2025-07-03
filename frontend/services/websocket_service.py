"""
WebSocket service for real-time communication with the backend.

This module provides WebSocket client functionality for real-time
chat, notifications, and live updates.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    websockets = None
    WebSocketClientProtocol = None


class WebSocketEventType(Enum):
    """WebSocket event types."""
    MESSAGE = "message"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@dataclass
class WebSocketEvent:
    """WebSocket event wrapper."""
    event_type: WebSocketEventType
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None


class WebSocketService:
    """WebSocket service for real-time communication."""
    
    def __init__(self, backend_url: str = "ws://localhost:8000"):
        self.backend_url = backend_url.replace("http://", "ws://").replace("https://", "wss://")
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0
        
        # Event handlers
        self.event_handlers: Dict[WebSocketEventType, List[Callable]] = {
            event_type: [] for event_type in WebSocketEventType
        }
        
        # Connection state
        self.connection_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def add_event_handler(self, event_type: WebSocketEventType, handler: Callable):
        """Add event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: WebSocketEventType, handler: Callable):
        """Remove event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
    
    async def connect(self, token: Optional[str] = None):
        """Connect to WebSocket server."""
        if not websockets:
            self.logger.error("WebSocket library not available")
            return False
        
        try:
            # Prepare connection URL
            ws_url = f"{self.backend_url}/ws"
            if token:
                ws_url += f"?token={token}"
            
            self.logger.info(f"Connecting to WebSocket: {ws_url}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connected = True
            self.reconnect_attempts = 0
            
            # Start message handling
            self.connection_task = asyncio.create_task(self._handle_messages())
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
            
            # Emit connected event
            await self._emit_event(WebSocketEventType.CONNECTED, {"status": "connected"})
            
            self.logger.info("WebSocket connected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            await self._emit_event(WebSocketEventType.ERROR, {"error": str(e)})
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server."""
        self.connected = False
        
        # Cancel tasks
        if self.connection_task:
            self.connection_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
        
        # Emit disconnected event
        await self._emit_event(WebSocketEventType.DISCONNECTED, {"status": "disconnected"})
        
        self.logger.info("WebSocket disconnected")
    
    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message through WebSocket."""
        if not self.connected or not self.websocket:
            self.logger.error("WebSocket not connected")
            return False
        
        try:
            message = {
                "type": message_type,
                "data": data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def send_chat_message(self, conversation_id: str, content: str, message_type: str = "text"):
        """Send chat message."""
        return await self.send_message("chat_message", {
            "conversation_id": conversation_id,
            "content": content,
            "message_type": message_type
        })
    
    async def send_typing_indicator(self, conversation_id: str, is_typing: bool):
        """Send typing indicator."""
        return await self.send_message("typing_indicator", {
            "conversation_id": conversation_id,
            "is_typing": is_typing
        })
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get("type", "message")
                    event_data = data.get("data", {})
                    
                    # Map event type to enum
                    if event_type == "message":
                        ws_event_type = WebSocketEventType.MESSAGE
                    elif event_type == "notification":
                        ws_event_type = WebSocketEventType.NOTIFICATION
                    elif event_type == "status_update":
                        ws_event_type = WebSocketEventType.STATUS_UPDATE
                    elif event_type == "error":
                        ws_event_type = WebSocketEventType.ERROR
                    else:
                        ws_event_type = WebSocketEventType.MESSAGE
                    
                    # Create event
                    event = WebSocketEvent(
                        event_type=ws_event_type,
                        data=event_data,
                        timestamp=data.get("timestamp")
                    )
                    
                    # Emit event
                    await self._emit_event(ws_event_type, event_data)
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON message: {e}")
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
            await self._handle_disconnection()
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            await self._handle_disconnection()
    
    async def _handle_disconnection(self):
        """Handle WebSocket disconnection."""
        self.connected = False
        
        # Emit disconnected event
        await self._emit_event(WebSocketEventType.DISCONNECTED, {"status": "disconnected"})
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            
            await asyncio.sleep(self.reconnect_delay)
            await self.connect()
        else:
            self.logger.error("Max reconnection attempts reached")
    
    async def _heartbeat(self):
        """Send heartbeat to keep connection alive."""
        while self.connected:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                if self.connected:
                    await self.send_message("heartbeat", {"timestamp": asyncio.get_event_loop().time()})
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break
    
    async def _emit_event(self, event_type: WebSocketEventType, data: Dict[str, Any]):
        """Emit event to all handlers."""
        event = WebSocketEvent(
            event_type=event_type,
            data=data,
            timestamp=asyncio.get_event_loop().time()
        )
        
        # Call all handlers for this event type
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler: {e}")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected and self.websocket is not None
    
    async def wait_for_connection(self, timeout: float = 10.0):
        """Wait for WebSocket connection."""
        start_time = asyncio.get_event_loop().time()
        while not self.connected:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("WebSocket connection timeout")
            await asyncio.sleep(0.1)


# Global WebSocket service instance
websocket_service = WebSocketService() 