"""
Real-time data service using Redis for high-performance data streaming
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import websockets
from websockets.server import WebSocketServerProtocol

from src.cache.redis_service import redis_service
from src.trading.binance_client import BinanceTradingClient
from src.database.repository import trading_repo, performance_repo

logger = logging.getLogger(__name__)

class RealTimeDataService:
    """
    Real-time data service for streaming market data, performance metrics,
    and trading signals to connected clients via WebSocket
    """
    
    def __init__(self):
        self.connected_clients: Dict[str, WebSocketServerProtocol] = {}
        self.binance_client = BinanceTradingClient()
        self.is_running = False
        self.data_streams = {}
        
    async def initialize(self):
        """Initialize the real-time service"""
        try:
            await redis_service.initialize()
            await self.binance_client.connect()
            logger.info("Real-time data service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize real-time service: {e}")
            raise
    
    async def start_websocket_server(self, host: str = "0.0.0.0", port: int = 8765):
        """Start WebSocket server for real-time data streaming"""
        try:
            logger.info(f"Starting WebSocket server on {host}:{port}")
            
            async def handle_client(websocket: WebSocketServerProtocol, path: str):
                client_id = f"client_{datetime.now().timestamp()}"
                self.connected_clients[client_id] = websocket
                
                # Register connection in Redis
                await redis_service.register_websocket_connection(client_id)
                
                logger.info(f"Client {client_id} connected from {websocket.remote_address}")
                
                try:
                    # Send welcome message
                    await self.send_to_client(client_id, {
                        'type': 'connection',
                        'message': 'Connected to EvolvingTrader real-time data stream',
                        'client_id': client_id,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Handle client messages
                    async for message in websocket:
                        await self.handle_client_message(client_id, message)
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"Client {client_id} disconnected")
                except Exception as e:
                    logger.error(f"Error handling client {client_id}: {e}")
                finally:
                    # Clean up
                    if client_id in self.connected_clients:
                        del self.connected_clients[client_id]
                    await redis_service.unregister_websocket_connection(client_id)
            
            # Start WebSocket server
            server = await websockets.serve(handle_client, host, port)
            logger.info(f"WebSocket server started on ws://{host}:{port}")
            
            # Keep server running
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
            raise
    
    async def handle_client_message(self, client_id: str, message: str):
        """Handle incoming client messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Client wants to subscribe to specific data streams
                streams = data.get('streams', [])
                await self.subscribe_client_to_streams(client_id, streams)
                
            elif message_type == 'unsubscribe':
                # Client wants to unsubscribe from streams
                streams = data.get('streams', [])
                await self.unsubscribe_client_from_streams(client_id, streams)
                
            elif message_type == 'ping':
                # Heartbeat
                await self.send_to_client(client_id, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from client {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def subscribe_client_to_streams(self, client_id: str, streams: List[str]):
        """Subscribe client to specific data streams"""
        try:
            # Store client subscriptions in Redis
            subscription_key = f"subscriptions:{client_id}"
            await redis_service.cache_data(
                subscription_key,
                streams,
                ttl=3600,
                prefix='cache'
            )
            
            await self.send_to_client(client_id, {
                'type': 'subscription_confirmed',
                'streams': streams,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error subscribing client to streams: {e}")
    
    async def unsubscribe_client_from_streams(self, client_id: str, streams: List[str]):
        """Unsubscribe client from specific data streams"""
        try:
            # Remove streams from client subscriptions
            subscription_key = f"subscriptions:{client_id}"
            current_subscriptions = await redis_service.get_cached_data(
                subscription_key,
                prefix='cache'
            ) or []
            
            updated_subscriptions = [s for s in current_subscriptions if s not in streams]
            await redis_service.cache_data(
                subscription_key,
                updated_subscriptions,
                ttl=3600,
                prefix='cache'
            )
            
            await self.send_to_client(client_id, {
                'type': 'unsubscription_confirmed',
                'streams': streams,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error unsubscribing client from streams: {e}")
    
    async def send_to_client(self, client_id: str, data: Dict[str, Any]):
        """Send data to specific client"""
        try:
            if client_id in self.connected_clients:
                websocket = self.connected_clients[client_id]
                await websocket.send(json.dumps(data, default=str))
        except websockets.exceptions.ConnectionClosed:
            # Client disconnected, remove from list
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
        except Exception as e:
            logger.error(f"Error sending data to client {client_id}: {e}")
    
    async def broadcast_to_all(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        try:
            if not self.connected_clients:
                return
            
            message = json.dumps(data, default=str)
            disconnected_clients = []
            
            for client_id, websocket in self.connected_clients.items():
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.append(client_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                if client_id in self.connected_clients:
                    del self.connected_clients[client_id]
                await redis_service.unregister_websocket_connection(client_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting to all clients: {e}")
    
    async def start_market_data_stream(self, symbols: List[str]):
        """Start streaming market data for symbols"""
        try:
            logger.info(f"Starting market data stream for symbols: {symbols}")
            
            for symbol in symbols:
                # Start individual symbol stream
                asyncio.create_task(self._stream_symbol_data(symbol))
            
            self.is_running = True
            
        except Exception as e:
            logger.error(f"Error starting market data stream: {e}")
    
    async def _stream_symbol_data(self, symbol: str):
        """Stream data for a specific symbol"""
        try:
            while self.is_running:
                try:
                    # Get current price
                    current_price = await self.binance_client.get_ticker_price(symbol)
                    
                    # Get 24hr ticker data
                    ticker_data = await self.binance_client.get_24hr_ticker(symbol)
                    
                    # Prepare market data
                    market_data = {
                        'type': 'market_data',
                        'symbol': symbol,
                        'price': current_price,
                        'change_24h': float(ticker_data.get('priceChange', 0)),
                        'change_percent_24h': float(ticker_data.get('priceChangePercent', 0)),
                        'volume_24h': float(ticker_data.get('volume', 0)),
                        'high_24h': float(ticker_data.get('highPrice', 0)),
                        'low_24h': float(ticker_data.get('lowPrice', 0)),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Cache in Redis
                    await redis_service.cache_price_data(symbol, current_price, datetime.now())
                    
                    # Broadcast to subscribed clients
                    await self.broadcast_to_subscribers('market_data', market_data)
                    
                    # Wait before next update
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error streaming data for {symbol}: {e}")
                    await asyncio.sleep(10)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Error in symbol data stream for {symbol}: {e}")
    
    async def broadcast_to_subscribers(self, stream_type: str, data: Dict[str, Any]):
        """Broadcast data to clients subscribed to specific stream type"""
        try:
            # Get all connected clients
            active_connections = await redis_service.get_active_connections()
            
            for connection in active_connections:
                client_id = connection['connection_id']
                
                # Get client subscriptions
                subscription_key = f"subscriptions:{client_id}"
                subscriptions = await redis_service.get_cached_data(
                    subscription_key,
                    prefix='cache'
                ) or []
                
                # Check if client is subscribed to this stream type
                if stream_type in subscriptions or 'all' in subscriptions:
                    await self.send_to_client(client_id, data)
                    
        except Exception as e:
            logger.error(f"Error broadcasting to subscribers: {e}")
    
    async def start_performance_stream(self):
        """Start streaming performance metrics"""
        try:
            logger.info("Starting performance metrics stream")
            
            while self.is_running:
                try:
                    # Get current performance metrics from database
                    # This would be implemented based on your performance tracking
                    performance_data = {
                        'type': 'performance',
                        'total_pnl': 0.0,  # Get from database
                        'win_rate': 0.0,   # Get from database
                        'active_positions': 0,  # Get from database
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Cache in Redis
                    await redis_service.cache_performance_metrics(performance_data)
                    
                    # Broadcast to subscribed clients
                    await self.broadcast_to_subscribers('performance', performance_data)
                    
                    # Wait before next update
                    await asyncio.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error streaming performance data: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Error in performance stream: {e}")
    
    async def start_risk_metrics_stream(self):
        """Start streaming risk metrics"""
        try:
            logger.info("Starting risk metrics stream")
            
            while self.is_running:
                try:
                    # Get current risk metrics
                    risk_data = {
                        'type': 'risk_metrics',
                        'portfolio_value': 1000.0,  # Get from database
                        'total_exposure': 0.0,      # Get from database
                        'max_drawdown': 0.0,        # Get from database
                        'risk_score': 0.0,          # Get from database
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Cache in Redis
                    await redis_service.cache_risk_metrics(risk_data)
                    
                    # Broadcast to subscribed clients
                    await self.broadcast_to_subscribers('risk_metrics', risk_data)
                    
                    # Wait before next update
                    await asyncio.sleep(60)  # Update every minute
                    
                except Exception as e:
                    logger.error(f"Error streaming risk data: {e}")
                    await asyncio.sleep(120)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Error in risk metrics stream: {e}")
    
    async def start_trading_signals_stream(self):
        """Start streaming trading signals"""
        try:
            logger.info("Starting trading signals stream")
            
            # Subscribe to Redis pub/sub for trading signals
            await redis_service.subscribe_to_updates('trading_signals', self._handle_trading_signal)
            
        except Exception as e:
            logger.error(f"Error starting trading signals stream: {e}")
    
    async def _handle_trading_signal(self, signal_data: Dict[str, Any]):
        """Handle incoming trading signal from Redis pub/sub"""
        try:
            # Broadcast signal to subscribed clients
            await self.broadcast_to_subscribers('trading_signals', {
                'type': 'trading_signal',
                'signal': signal_data,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling trading signal: {e}")
    
    async def stop(self):
        """Stop the real-time service"""
        try:
            self.is_running = False
            
            # Close all client connections
            for client_id, websocket in self.connected_clients.items():
                try:
                    await websocket.close()
                except:
                    pass
            
            self.connected_clients.clear()
            
            # Close Redis connection
            await redis_service.close()
            
            logger.info("Real-time data service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping real-time service: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get real-time service status"""
        try:
            redis_health = await redis_service.health_check()
            
            return {
                'status': 'running' if self.is_running else 'stopped',
                'connected_clients': len(self.connected_clients),
                'active_streams': len(self.data_streams),
                'redis_health': redis_health,
                'uptime': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

# Global real-time service instance
realtime_service = RealTimeDataService()