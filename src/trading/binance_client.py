"""
Binance API client for trading operations
"""
import asyncio
from typing import Dict, List, Optional, Tuple
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime, timedelta
import logging
from config import binance_config

logger = logging.getLogger(__name__)

class BinanceTradingClient:
    """Enhanced Binance client for trading operations"""
    
    def __init__(self):
        self.client: Optional[AsyncClient] = None
        self.socket_manager: Optional[BinanceSocketManager] = None
        self.is_connected = False
        
    async def connect(self):
        """Initialize connection to Binance API"""
        try:
            self.client = await AsyncClient.create(
                api_key=binance_config.api_key,
                api_secret=binance_config.secret_key,
                testnet=binance_config.testnet
            )
            self.socket_manager = BinanceSocketManager(self.client)
            self.is_connected = True
            logger.info("Connected to Binance API")
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to Binance API"""
        if self.client:
            await self.client.close_connection()
            self.is_connected = False
            logger.info("Disconnected from Binance API")
    
    async def get_account_info(self) -> Dict:
        """Get account information including balances"""
        if not self.is_connected:
            await self.connect()
        
        try:
            account = await self.client.get_account()
            return account
        except BinanceAPIException as e:
            logger.error(f"Failed to get account info: {e}")
            raise
    
    async def get_balance(self, asset: str = "USDT") -> float:
        """Get balance for specific asset"""
        account = await self.get_account_info()
        for balance in account['balances']:
            if balance['asset'] == asset:
                return float(balance['free'])
        return 0.0
    
    async def get_symbol_info(self, symbol: str) -> Dict:
        """Get trading symbol information"""
        if not self.is_connected:
            await self.connect()
        
        try:
            info = await self.client.get_symbol_info(symbol)
            return info
        except BinanceAPIException as e:
            logger.error(f"Failed to get symbol info for {symbol}: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """Get historical kline/candlestick data"""
        if not self.is_connected:
            await self.connect()
        
        try:
            klines = await self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to proper data types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = df[col].astype(float)
            
            return df
        except BinanceAPIException as e:
            logger.error(f"Failed to get klines for {symbol}: {e}")
            raise
    
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: Optional[float] = None) -> Dict:
        """Place a trading order"""
        if not self.is_connected:
            await self.connect()
        
        try:
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }
            
            if price and order_type in ['LIMIT', 'STOP_LOSS_LIMIT']:
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'
            
            order = await self.client.create_order(**order_params)
            logger.info(f"Order placed: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an existing order"""
        if not self.is_connected:
            await self.connect()
        
        try:
            result = await self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order cancelled: {result}")
            return result
        except BinanceAPIException as e:
            logger.error(f"Failed to cancel order: {e}")
            raise
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        if not self.is_connected:
            await self.connect()
        
        try:
            orders = await self.client.get_open_orders(symbol=symbol)
            return orders
        except BinanceAPIException as e:
            logger.error(f"Failed to get open orders: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get status of a specific order"""
        if not self.is_connected:
            await self.connect()
        
        try:
            order = await self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except BinanceAPIException as e:
            logger.error(f"Failed to get order status: {e}")
            raise
    
    async def get_ticker_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        if not self.is_connected:
            await self.connect()
        
        try:
            ticker = await self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Failed to get ticker price for {symbol}: {e}")
            raise
    
    async def get_24hr_ticker(self, symbol: str) -> Dict:
        """Get 24hr ticker price change statistics"""
        if not self.is_connected:
            await self.connect()
        
        try:
            ticker = await self.client.get_ticker(symbol=symbol)
            return ticker
        except BinanceAPIException as e:
            logger.error(f"Failed to get 24hr ticker for {symbol}: {e}")
            raise
    
    async def stream_klines(self, symbol: str, interval: str, callback):
        """Stream real-time kline data"""
        if not self.is_connected:
            await self.connect()
        
        try:
            async with self.socket_manager.kline_socket(symbol, interval) as stream:
                async for msg in stream:
                    await callback(msg)
        except Exception as e:
            logger.error(f"Error in kline stream: {e}")
            raise