#!/usr/bin/env python3
"""
Update dashboard with REAL account data from Binance.US
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trading.binance_client import BinanceTradingClient
from src.strategy.optimized_strategy import OptimizedEvolvingStrategy
from config import trading_config, binance_config

logger = logging.getLogger(__name__)

class RealDataUpdater:
    """Update dashboard with real trading data"""
    
    def __init__(self):
        self.binance_client = BinanceTradingClient()
        self.strategy = OptimizedEvolvingStrategy(['BTCUSDT'])
        
    async def get_real_account_data(self) -> Dict[str, Any]:
        """Get REAL account data from Binance.US"""
        try:
            print("🔌 Connecting to Binance.US...")
            await self.binance_client.connect()
            
            print("📊 Fetching account information...")
            account = await self.binance_client.get_account_info()
            
            # Get REAL balances
            balances = {}
            total_balance = 0.0
            
            print("💰 Calculating real balances...")
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
                    
                    # Convert to USDT equivalent
                    if asset == 'USDT':
                        total_balance += total
                        print(f"   USDT: {total:.2f}")
                    elif asset == 'BTC':
                        try:
                            btc_price = await self.binance_client.get_ticker_price('BTCUSDT')
                            usdt_value = total * btc_price
                            total_balance += usdt_value
                            print(f"   BTC: {total:.6f} (${usdt_value:.2f})")
                        except:
                            print(f"   BTC: {total:.6f} (price unavailable)")
                    else:
                        print(f"   {asset}: {total:.6f}")
            
            await self.binance_client.disconnect()
            
            return {
                'total_balance': total_balance,
                'balances': balances,
                'can_trade': account.get('canTrade', False),
                'account_type': account.get('accountType', 'Unknown'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real account data: {e}")
            return {
                'total_balance': 0.0,
                'balances': {},
                'can_trade': False,
                'account_type': 'Error',
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_real_market_data(self) -> Dict[str, Any]:
        """Get REAL market data"""
        try:
            print("📈 Fetching real market data...")
            await self.binance_client.connect()
            
            # Get current price
            btc_price = await self.binance_client.get_ticker_price('BTCUSDT')
            print(f"   BTCUSDT Price: ${btc_price:,.2f}")
            
            # Get historical data for indicators
            df = await self.binance_client.get_historical_data('BTCUSDT', '1h', 100)
            
            indicators = {}
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
                
                print(f"   RSI: {indicators['rsi']:.1f}")
                print(f"   MACD: {indicators['macd']:.4f}")
            
            await self.binance_client.disconnect()
            
            return {
                'current_price': btc_price,
                'indicators': indicators,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real market data: {e}")
            return {
                'current_price': 0.0,
                'indicators': {},
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_real_trading_signals(self) -> Dict[str, Any]:
        """Get REAL trading signals"""
        try:
            print("🎯 Generating real trading signals...")
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
            
            print(f"   Generated {len(signals)} signals")
            
            return {
                'signals': signal_data,
                'signal_count': len(signals),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real trading signals: {e}")
            return {
                'signals': [],
                'signal_count': 0,
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_real_trades_history(self) -> Dict[str, Any]:
        """Get REAL trades history"""
        try:
            trades_file = 'trades_history.json'
            
            if os.path.exists(trades_file):
                with open(trades_file, 'r') as f:
                    trades_data = json.load(f)
            else:
                trades_data = {'trades': []}
            
            trades = trades_data.get('trades', [])
            
            # Calculate REAL statistics
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
                
                print(f"   Total Trades: {total_trades}")
                print(f"   Win Rate: {win_rate:.1f}%")
                print(f"   Total P&L: ${total_pnl:.2f}")
                
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
                
                print("   No trades yet")
            
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
            logger.error(f"Failed to get real trades history: {e}")
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
    
    async def update_dashboard_with_real_data(self):
        """Update dashboard with ALL real data"""
        try:
            print("🚀 Updating dashboard with REAL trading data...")
            print("=" * 60)
            
            # Get all real data
            account_data = await self.get_real_account_data()
            market_data = await self.get_real_market_data()
            signals_data = await self.get_real_trading_signals()
            trades_data = self.get_real_trades_history()
            
            # Calculate total capital from actual account balance
            total_capital = account_data['total_balance']
            
            # Combine all data
            real_data = {
                'account': account_data,
                'market': market_data,
                'signals': signals_data,
                'trades': trades_data,
                'config': {
                    'initial_capital': total_capital,  # Use actual account balance
                    'current_capital': total_capital,  # Current balance
                    'max_position_size': trading_config.max_position_size,
                    'risk_per_trade': trading_config.risk_per_trade,
                    'testnet': binance_config.testnet
                },
                'last_updated': datetime.now().isoformat()
            }
            
            # Save for Vercel
            with open('vercel_data.json', 'w') as f:
                json.dump(real_data, f, indent=2)
            
            # Update API stats file
            with open('api/stats_data.json', 'w') as f:
                json.dump(real_data, f, indent=2)
            
            print("\n✅ Dashboard updated with REAL data!")
            print("=" * 60)
            print(f"💰 REAL Account Balance: ${account_data['total_balance']:.2f}")
            print(f"📊 REAL Trading Mode: {'LIVE' if not binance_config.testnet else 'TESTNET'}")
            print(f"📈 REAL BTC Price: ${market_data['current_price']:,.2f}")
            print(f"🎯 REAL Signals: {signals_data['signal_count']}")
            print(f"📊 REAL Trades: {trades_data['statistics']['total_trades']}")
            print(f"💵 REAL P&L: ${trades_data['statistics']['total_pnl']:.2f}")
            print("=" * 60)
            
            return real_data
            
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            return None

async def main():
    """Main function"""
    print("🚀 EvolvingTrader - REAL Data Dashboard Update")
    print("=" * 60)
    
    updater = RealDataUpdater()
    
    # Update with real data
    real_data = await updater.update_dashboard_with_real_data()
    
    if real_data:
        print("\n🎉 Dashboard updated with your REAL trading data!")
        print("\n📋 Your dashboard now shows:")
        print(f"   • REAL account balance: ${real_data['account']['total_balance']:.2f}")
        print(f"   • REAL trading mode: {'LIVE' if not real_data['config']['testnet'] else 'TESTNET'}")
        print(f"   • REAL BTC price: ${real_data['market']['current_price']:,.2f}")
        print(f"   • REAL trading signals: {real_data['signals']['signal_count']}")
        print(f"   • REAL trade statistics: {real_data['trades']['statistics']['total_trades']} trades")
        
        print("\n🚀 Next steps:")
        print("   1. Deploy to Vercel: vercel")
        print("   2. Your dashboard will show REAL data")
        print("   3. Run this script to keep data updated")
    else:
        print("\n❌ Failed to update dashboard with real data")

if __name__ == "__main__":
    asyncio.run(main())