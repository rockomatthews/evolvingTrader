"""
Redis service for EvolvingTrader - High-performance caching and real-time data
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from upstash_redis import Redis as UpstashRedis

from config import redis_config

logger = logging.getLogger(__name__)

class RedisService:
    """
    Redis service for high-performance caching and real-time data management
    
    Redis is used for:
    1. Real-time market data caching (prices, indicators)
    2. Session state management (active positions, current balance)
    3. Rate limiting and API throttling
    4. Temporary signal storage and processing queues
    5. Performance metrics caching for dashboard
    6. Strategy parameter caching
    7. Risk metrics real-time updates
    8. WebSocket connection management
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.upstash_client: Optional[UpstashRedis] = None
        self.initialized = False
        
        # Key prefixes for organization
        self.prefixes = {
            'market_data': 'market:',
            'positions': 'positions:',
            'signals': 'signals:',
            'performance': 'perf:',
            'risk': 'risk:',
            'session': 'session:',
            'rate_limit': 'rate:',
            'cache': 'cache:',
            'websocket': 'ws:'
        }
    
    async def initialize(self):
        """Initialize Redis connections"""
        try:
            # Initialize standard Redis client
            self.redis_client = redis.from_url(
                redis_config.url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Initialize Upstash Redis client for REST API
            self.upstash_client = UpstashRedis(
                url=redis_config.upstash_rest_url,
                token=redis_config.upstash_rest_token
            )
            
            # Test connections
            await self.redis_client.ping()
            self.upstash_client.ping()
            
            self.initialized = True
            logger.info("Redis service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis service: {e}")
            raise
    
    async def close(self):
        """Close Redis connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            self.initialized = False
            logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")
    
    # Market Data Caching
    async def cache_market_data(self, symbol: str, data: Dict[str, Any], ttl: int = 60):
        """Cache market data for fast access"""
        try:
            key = f"{self.prefixes['market_data']}{symbol}"
            await self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching market data for {symbol}: {e}")
    
    async def get_cached_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached market data"""
        try:
            key = f"{self.prefixes['market_data']}{symbol}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached market data for {symbol}: {e}")
            return None
    
    async def cache_price_data(self, symbol: str, price: float, timestamp: datetime):
        """Cache real-time price data"""
        try:
            key = f"{self.prefixes['market_data']}price:{symbol}"
            price_data = {
                'price': price,
                'timestamp': timestamp.isoformat(),
                'symbol': symbol
            }
            await self.redis_client.setex(
                key, 
                30,  # 30 second TTL
                json.dumps(price_data)
            )
        except Exception as e:
            logger.error(f"Error caching price data for {symbol}: {e}")
    
    # Position Management
    async def cache_active_positions(self, positions: Dict[str, Any]):
        """Cache active positions for real-time access"""
        try:
            key = f"{self.prefixes['positions']}active"
            await self.redis_client.setex(
                key,
                300,  # 5 minute TTL
                json.dumps(positions, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching active positions: {e}")
    
    async def get_cached_positions(self) -> Optional[Dict[str, Any]]:
        """Get cached active positions"""
        try:
            key = f"{self.prefixes['positions']}active"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached positions: {e}")
            return None
    
    # Signal Management
    async def cache_trading_signal(self, signal: Dict[str, Any], ttl: int = 300):
        """Cache trading signal for processing"""
        try:
            signal_id = signal.get('id', f"signal_{datetime.now().timestamp()}")
            key = f"{self.prefixes['signals']}{signal_id}"
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(signal, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching trading signal: {e}")
    
    async def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get all pending trading signals"""
        try:
            pattern = f"{self.prefixes['signals']}*"
            keys = await self.redis_client.keys(pattern)
            signals = []
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    signals.append(json.loads(data))
            
            return signals
        except Exception as e:
            logger.error(f"Error getting pending signals: {e}")
            return []
    
    # Performance Metrics Caching
    async def cache_performance_metrics(self, metrics: Dict[str, Any], ttl: int = 60):
        """Cache performance metrics for dashboard"""
        try:
            key = f"{self.prefixes['performance']}current"
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(metrics, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching performance metrics: {e}")
    
    async def get_cached_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get cached performance metrics"""
        try:
            key = f"{self.prefixes['performance']}current"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached performance metrics: {e}")
            return None
    
    # Risk Metrics Caching
    async def cache_risk_metrics(self, risk_data: Dict[str, Any], ttl: int = 120):
        """Cache risk metrics for real-time monitoring"""
        try:
            key = f"{self.prefixes['risk']}current"
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(risk_data, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching risk metrics: {e}")
    
    async def get_cached_risk_metrics(self) -> Optional[Dict[str, Any]]:
        """Get cached risk metrics"""
        try:
            key = f"{self.prefixes['risk']}current"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached risk metrics: {e}")
            return None
    
    # Session State Management
    async def cache_session_state(self, session_id: str, state: Dict[str, Any], ttl: int = 3600):
        """Cache session state"""
        try:
            key = f"{self.prefixes['session']}{session_id}"
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(state, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching session state: {e}")
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached session state"""
        try:
            key = f"{self.prefixes['session']}{session_id}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return None
    
    # Rate Limiting
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if rate limit is exceeded"""
        try:
            rate_key = f"{self.prefixes['rate_limit']}{key}"
            current = await self.redis_client.incr(rate_key)
            
            if current == 1:
                await self.redis_client.expire(rate_key, window)
            
            return current <= limit
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    async def reset_rate_limit(self, key: str):
        """Reset rate limit counter"""
        try:
            rate_key = f"{self.prefixes['rate_limit']}{key}"
            await self.redis_client.delete(rate_key)
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
    
    # General Caching
    async def cache_data(self, key: str, data: Any, ttl: int = 300, prefix: str = 'cache'):
        """General purpose caching"""
        try:
            full_key = f"{self.prefixes[prefix]}{key}"
            await self.redis_client.setex(
                full_key,
                ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching data for key {key}: {e}")
    
    async def get_cached_data(self, key: str, prefix: str = 'cache') -> Optional[Any]:
        """Get cached data"""
        try:
            full_key = f"{self.prefixes[prefix]}{key}"
            data = await self.redis_client.get(full_key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached data for key {key}: {e}")
            return None
    
    # Pub/Sub for Real-time Updates
    async def publish_update(self, channel: str, message: Dict[str, Any]):
        """Publish real-time update"""
        try:
            await self.redis_client.publish(
                channel,
                json.dumps(message, default=str)
            )
        except Exception as e:
            logger.error(f"Error publishing update to {channel}: {e}")
    
    async def subscribe_to_updates(self, channel: str, callback):
        """Subscribe to real-time updates"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await callback(data)
        except Exception as e:
            logger.error(f"Error subscribing to {channel}: {e}")
    
    # WebSocket Connection Management
    async def register_websocket_connection(self, connection_id: str, user_id: str = None):
        """Register WebSocket connection"""
        try:
            key = f"{self.prefixes['websocket']}conn:{connection_id}"
            connection_data = {
                'connection_id': connection_id,
                'user_id': user_id,
                'connected_at': datetime.now().isoformat(),
                'last_ping': datetime.now().isoformat()
            }
            await self.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                json.dumps(connection_data)
            )
        except Exception as e:
            logger.error(f"Error registering WebSocket connection: {e}")
    
    async def unregister_websocket_connection(self, connection_id: str):
        """Unregister WebSocket connection"""
        try:
            key = f"{self.prefixes['websocket']}conn:{connection_id}"
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error unregistering WebSocket connection: {e}")
    
    async def get_active_connections(self) -> List[Dict[str, Any]]:
        """Get all active WebSocket connections"""
        try:
            pattern = f"{self.prefixes['websocket']}conn:*"
            keys = await self.redis_client.keys(pattern)
            connections = []
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    connections.append(json.loads(data))
            
            return connections
        except Exception as e:
            logger.error(f"Error getting active connections: {e}")
            return []
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis service health"""
        try:
            # Test standard Redis
            start_time = datetime.now()
            await self.redis_client.ping()
            redis_latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Test Upstash Redis
            start_time = datetime.now()
            self.upstash_client.ping()
            upstash_latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return {
                'status': 'healthy',
                'redis_latency_ms': redis_latency,
                'upstash_latency_ms': upstash_latency,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    # Cleanup
    async def cleanup_expired_keys(self):
        """Clean up expired keys (Redis does this automatically, but we can force it)"""
        try:
            # Redis automatically cleans up expired keys
            # This is just for manual cleanup if needed
            await self.redis_client.execute_command('MEMORY', 'PURGE')
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global Redis service instance
redis_service = RedisService()