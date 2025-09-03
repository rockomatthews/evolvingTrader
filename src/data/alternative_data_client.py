"""
Alternative data client for testing when Binance is restricted
"""
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import yfinance as yf
import ccxt

logger = logging.getLogger(__name__)

class AlternativeDataClient:
    """Alternative data client using Yahoo Finance and CCXT"""
    
    def __init__(self):
        self.yahoo_symbols = {
            'BTCUSDT': 'BTC-USD',
            'ETHUSDT': 'ETH-USD',
            'ADAUSDT': 'ADA-USD',
            'SOLUSDT': 'SOL-USD',
            'DOTUSDT': 'DOT-USD'
        }
        
        # Initialize CCXT exchange (try multiple)
        self.exchanges = []
        self._init_exchanges()
    
    def _init_exchanges(self):
        """Initialize available exchanges"""
        exchange_configs = [
            {'name': 'binance', 'testnet': True},
            {'name': 'coinbase', 'sandbox': True},
            {'name': 'kraken', 'sandbox': True},
            {'name': 'bitfinex', 'sandbox': True}
        ]
        
        for config in exchange_configs:
            try:
                exchange_class = getattr(ccxt, config['name'])
                exchange = exchange_class(config)
                self.exchanges.append(exchange)
                logger.info(f"Initialized {config['name']} exchange")
            except Exception as e:
                logger.warning(f"Failed to initialize {config['name']}: {e}")
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1h', 
                                limit: int = 1000) -> pd.DataFrame:
        """Get historical data using multiple sources"""
        
        # Try Yahoo Finance first (most reliable)
        try:
            return await self._get_yahoo_data(symbol, timeframe, limit)
        except Exception as e:
            logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
        
        # Try CCXT exchanges
        for exchange in self.exchanges:
            try:
                return await self._get_ccxt_data(exchange, symbol, timeframe, limit)
            except Exception as e:
                logger.warning(f"{exchange.id} failed for {symbol}: {e}")
        
        # Fallback to mock data
        logger.warning(f"All data sources failed for {symbol}, using mock data")
        return self._generate_mock_data(symbol, limit)
    
    async def _get_yahoo_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Get data from Yahoo Finance"""
        yahoo_symbol = self.yahoo_symbols.get(symbol, symbol.replace('USDT', '-USD'))
        
        # Convert timeframe
        interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d'
        }
        interval = interval_map.get(timeframe, '1h')
        
        # Get data
        ticker = yf.Ticker(yahoo_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=limit//24)  # Approximate
        
        data = ticker.history(start=start_date, end=end_date, interval=interval)
        
        if data.empty:
            raise ValueError(f"No data from Yahoo Finance for {yahoo_symbol}")
        
        # Convert to our format
        df = pd.DataFrame({
            'open': data['Open'],
            'high': data['High'],
            'low': data['Low'],
            'close': data['Close'],
            'volume': data['Volume']
        })
        
        # Remove timezone info
        df.index = df.index.tz_localize(None)
        
        return df.tail(limit)
    
    async def _get_ccxt_data(self, exchange, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Get data from CCXT exchange"""
        # Convert symbol format
        ccxt_symbol = symbol.replace('USDT', '/USDT')
        
        # Get OHLCV data
        ohlcv = exchange.fetch_ohlcv(ccxt_symbol, timeframe, limit=limit)
        
        if not ohlcv:
            raise ValueError(f"No data from {exchange.id} for {ccxt_symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def _generate_mock_data(self, symbol: str, limit: int) -> pd.DataFrame:
        """Generate realistic mock data for testing"""
        logger.info(f"Generating mock data for {symbol}")
        
        # Base price for different symbols
        base_prices = {
            'BTCUSDT': 45000,
            'ETHUSDT': 3000,
            'ADAUSDT': 0.5,
            'SOLUSDT': 100,
            'DOTUSDT': 7
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Generate timestamps
        end_time = datetime.now()
        timestamps = [end_time - timedelta(hours=i) for i in range(limit, 0, -1)]
        
        # Generate realistic price data
        np.random.seed(42)  # For reproducible results
        
        # Generate price movements
        returns = np.random.normal(0, 0.02, limit)  # 2% volatility
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
        
        # Generate OHLCV data
        data = []
        for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
            # Generate realistic OHLC from close price
            volatility = abs(np.random.normal(0, 0.01))
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            open_price = prices[i-1] if i > 0 else price
            
            # Generate volume
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=timestamps)
        return df
    
    async def get_ticker_price(self, symbol: str) -> float:
        """Get current ticker price"""
        try:
            # Try Yahoo Finance first
            yahoo_symbol = self.yahoo_symbols.get(symbol, symbol.replace('USDT', '-USD'))
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            return info.get('regularMarketPrice', info.get('currentPrice', 0))
        except Exception as e:
            logger.warning(f"Failed to get price for {symbol}: {e}")
            # Return mock price
            base_prices = {
                'BTCUSDT': 45000,
                'ETHUSDT': 3000,
                'ADAUSDT': 0.5,
                'SOLUSDT': 100,
                'DOTUSDT': 7
            }
            return base_prices.get(symbol, 100)
    
    async def get_account_info(self) -> Dict:
        """Mock account info for testing"""
        return {
            'accountType': 'SPOT',
            'canTrade': True,
            'canWithdraw': True,
            'canDeposit': True,
            'balances': [
                {'asset': 'USDT', 'free': '1000.0', 'locked': '0.0'},
                {'asset': 'BTC', 'free': '0.0', 'locked': '0.0'}
            ]
        }