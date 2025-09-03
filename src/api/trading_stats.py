"""
Trading statistics API for real-time dashboard
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

from src.trading.binance_client import BinanceTradingClient
from src.strategy.optimized_strategy import OptimizedEvolvingStrategy
from config import trading_config, binance_config

logger = logging.getLogger(__name__)

class TradingStatsAPI:
    """API for getting real trading statistics"""
    
    def __init__(self):
        self.binance_client = BinanceTradingClient()
        self.strategy = OptimizedEvolvingStrategy(['BTCUSDT'])
        self.trades_file = 'trades_history.json'
        self.performance_file = 'performance_history.json'
        
    async def get_account_stats(self) -> Dict[str, Any]:
        """Get real account statistics"""
        try:
            await self.binance_client.connect()
            account = await self.binance_client.get_account_info()
            
            # Get balances
            balances = {}
            total_balance = 0.0
            for balance in account.get('balances', []):
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    balances[asset] = {
                        'free': free,
                        'locked': locked,
                        'total': total
                    }
                    # Convert to USDT equivalent (simplified)
                    if asset == 'USDT':
                        total_balance += total
                    elif asset == 'BTC':
                        try:
                            btc_price = await self.binance_client.get_ticker_price('BTCUSDT')
                            total_balance += total * btc_price
                        except:
                            pass
            
            await self.binance_client.disconnect()
            
            return {
                'total_balance': total_balance,
                'balances': balances,
                'can_trade': account.get('canTrade', False),
                'account_type': account.get('accountType', 'Unknown'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account stats: {e}")
            return {
                'total_balance': 0.0,
                'balances': {},
                'can_trade': False,
                'account_type': 'Error',
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_market_data(self) -> Dict[str, Any]:
        """Get real market data"""
        try:
            await self.binance_client.connect()
            
            # Get current price
            btc_price = await self.binance_client.get_ticker_price('BTCUSDT')
            
            # Get historical data for chart
            df = await self.binance_client.get_historical_data('BTCUSDT', '1h', 24)
            
            # Get technical indicators
            if not df.empty:
                df = self.strategy._add_technical_indicators(df)
                latest = df.iloc[-1]
                
                indicators = {
                    'rsi': float(latest.get('rsi', 0)) if not pd.isna(latest.get('rsi')) else 0,
                    'macd': float(latest.get('macd', 0)) if not pd.isna(latest.get('macd')) else 0,
                    'macd_signal': float(latest.get('macd_signal', 0)) if not pd.isna(latest.get('macd_signal')) else 0,
                    'bb_upper': float(latest.get('bb_upper', 0)) if not pd.isna(latest.get('bb_upper')) else 0,
                    'bb_lower': float(latest.get('bb_lower', 0)) if not pd.isna(latest.get('bb_lower')) else 0,
                    'ema_fast': float(latest.get('ema_fast', 0)) if not pd.isna(latest.get('ema_fast')) else 0,
                    'ema_slow': float(latest.get('ema_slow', 0)) if not pd.isna(latest.get('ema_slow')) else 0,
                }
            else:
                indicators = {}
            
            # Get price history for chart
            price_history = []
            if not df.empty:
                for _, row in df.tail(24).iterrows():
                    price_history.append({
                        'timestamp': row.name.isoformat(),
                        'price': float(row['close']),
                        'volume': float(row['volume'])
                    })
            
            await self.binance_client.disconnect()
            
            return {
                'current_price': btc_price,
                'price_history': price_history,
                'indicators': indicators,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return {
                'current_price': 0.0,
                'price_history': [],
                'indicators': {},
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_trading_signals(self) -> Dict[str, Any]:
        """Get current trading signals"""
        try:
            signals = await self.strategy.generate_signals('BTCUSDT')
            
            signal_data = []
            for signal in signals:
                signal_data.append({
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'position_size': signal.position_size,
                    'reasoning': signal.reasoning,
                    'timestamp': signal.timestamp.isoformat()
                })
            
            return {
                'signals': signal_data,
                'signal_count': len(signals),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get trading signals: {e}")
            return {
                'signals': [],
                'signal_count': 0,
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_trades_history(self) -> Dict[str, Any]:
        """Get trades history from file"""
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    trades_data = json.load(f)
            else:
                trades_data = {'trades': []}
            
            trades = trades_data.get('trades', [])
            
            # Calculate statistics
            if trades:
                total_trades = len(trades)
                winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
                losing_trades = len([t for t in trades if t.get('pnl', 0) < 0])
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                total_pnl = sum(t.get('pnl', 0) for t in trades)
                avg_win = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0) / max(winning_trades, 1)
                avg_loss = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0) / max(losing_trades, 1)
                
                profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
                
                # Calculate max drawdown
                cumulative_pnl = []
                running_total = 0
                for trade in trades:
                    running_total += trade.get('pnl', 0)
                    cumulative_pnl.append(running_total)
                
                max_drawdown = 0
                peak = 0
                for pnl in cumulative_pnl:
                    if pnl > peak:
                        peak = pnl
                    drawdown = peak - pnl
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                
                max_drawdown_pct = (max_drawdown / trading_config.initial_capital * 100) if trading_config.initial_capital > 0 else 0
                
            else:
                total_trades = 0
                winning_trades = 0
                losing_trades = 0
                win_rate = 0
                total_pnl = 0
                avg_win = 0
                avg_loss = 0
                profit_factor = 0
                max_drawdown = 0
                max_drawdown_pct = 0
            
            return {
                'trades': trades,
                'statistics': {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_pnl': total_pnl,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'profit_factor': profit_factor,
                    'max_drawdown': max_drawdown,
                    'max_drawdown_pct': max_drawdown_pct
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get trades history: {e}")
            return {
                'trades': [],
                'statistics': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'max_drawdown': 0,
                    'max_drawdown_pct': 0
                },
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_performance_history(self) -> Dict[str, Any]:
        """Get performance history for charts"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    performance_data = json.load(f)
            else:
                performance_data = {'performance': []}
            
            return {
                'performance': performance_data.get('performance', []),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return {
                'performance': [],
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get all statistics in one call"""
        try:
            account_stats = await self.get_account_stats()
            market_data = await self.get_market_data()
            trading_signals = await self.get_trading_signals()
            trades_history = self.get_trades_history()
            performance_history = self.get_performance_history()
            
            return {
                'account': account_stats,
                'market': market_data,
                'signals': trading_signals,
                'trades': trades_history,
                'performance': performance_history,
                'config': {
                    'initial_capital': trading_config.initial_capital,
                    'max_position_size': trading_config.max_position_size,
                    'risk_per_trade': trading_config.risk_per_trade,
                    'testnet': binance_config.testnet
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get all stats: {e}")
            return {
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }

# Global instance
trading_stats_api = TradingStatsAPI()