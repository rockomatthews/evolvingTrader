"""
WebSocket client for real-time dashboard updates
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)

class DashboardWebSocketClient:
    """
    WebSocket client for connecting to the real-time data service
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8765"):
        self.websocket_url = websocket_url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.subscribed_streams: List[str] = []
        self.message_handlers: Dict[str, Callable] = {}
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            logger.info(f"Connected to WebSocket server at {self.websocket_url}")
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        try:
            if self.websocket:
                await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from WebSocket server")
        except Exception as e:
            logger.error(f"Error disconnecting from WebSocket server: {e}")
    
    async def _listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
            self.connected = False
    
    async def _handle_message(self, message: str):
        """Handle incoming message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            # Call registered handler if available
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                logger.debug(f"Unhandled message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    async def subscribe_to_streams(self, streams: List[str]):
        """Subscribe to specific data streams"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to WebSocket server")
            
            message = {
                'type': 'subscribe',
                'streams': streams
            }
            
            await self.websocket.send(json.dumps(message))
            self.subscribed_streams.extend(streams)
            logger.info(f"Subscribed to streams: {streams}")
            
        except Exception as e:
            logger.error(f"Error subscribing to streams: {e}")
    
    async def unsubscribe_from_streams(self, streams: List[str]):
        """Unsubscribe from specific data streams"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to WebSocket server")
            
            message = {
                'type': 'unsubscribe',
                'streams': streams
            }
            
            await self.websocket.send(json.dumps(message))
            self.subscribed_streams = [s for s in self.subscribed_streams if s not in streams]
            logger.info(f"Unsubscribed from streams: {streams}")
            
        except Exception as e:
            logger.error(f"Error unsubscribing from streams: {e}")
    
    async def send_ping(self):
        """Send ping to server"""
        try:
            if not self.connected:
                return
            
            message = {
                'type': 'ping',
                'timestamp': asyncio.get_event_loop().time()
            }
            
            await self.websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
    
    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat to keep connection alive"""
        try:
            while self.connected:
                await self.send_ping()
                await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Error in heartbeat: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to WebSocket server"""
        return self.connected and self.websocket is not None