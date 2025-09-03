#!/usr/bin/env python3
"""
Run backtest and check results
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def run_backtest():
    """Run backtest and show results"""
    print("📊 Running Backtest...")
    print("=" * 30)
    
    try:
        from src.backtesting.backtester import Backtester
        from config import trading_config
        from datetime import datetime, timedelta
        
        # Create backtester
        backtester = Backtester(initial_capital=trading_config.initial_capital)
        
        # Define backtest parameters
        symbol = 'BTCUSDT'
        start_date = datetime.now() - timedelta(days=30)  # 30 days
        end_date = datetime.now()
        
        print(f"📈 Backtest Parameters:")
        print(f"   Symbol: {symbol}")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        print(f"   Initial Capital: ${trading_config.initial_capital:,.2f}")
        
        # Run backtest
        print(f"\n🔄 Running backtest...")
        result = await backtester.run_backtest(symbol, start_date, end_date)
        
        # Print results
        print(f"\n" + "="*50)
        print(f"BACKTEST RESULTS")
        print(f"="*50)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: ${trading_config.initial_capital:,.2f}")
        print(f"Total Return: {result.total_return:.2f}%")
        print(f"Total Trades: {result.total_trades}")
        print(f"Win Rate: {result.win_rate:.1f}%")
        print(f"Profit Factor: {result.profit_factor:.2f}")
        print(f"Max Drawdown: {result.max_drawdown:.2f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Calmar Ratio: {result.calmar_ratio:.2f}")
        
        if result.performance_metrics:
            print(f"\nAdditional Metrics:")
            for key, value in result.performance_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        print(f"="*50)
        
        # Save results
        filename = f"backtest_results_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backtester.save_backtest_results(result, filename)
        print(f"📁 Results saved to: {filename}")
        
        # Analyze results
        print(f"\n📊 Analysis:")
        if result.total_trades > 0:
            print(f"   ✅ Strategy generated {result.total_trades} trades")
            if result.total_return > 0:
                print(f"   ✅ Positive return: {result.total_return:.2f}%")
            else:
                print(f"   ⚠️  Negative return: {result.total_return:.2f}%")
            
            if result.win_rate > 50:
                print(f"   ✅ Good win rate: {result.win_rate:.1f}%")
            else:
                print(f"   ⚠️  Low win rate: {result.win_rate:.1f}%")
            
            if result.max_drawdown < 10:
                print(f"   ✅ Low drawdown: {result.max_drawdown:.2f}%")
            else:
                print(f"   ⚠️  High drawdown: {result.max_drawdown:.2f}%")
        else:
            print(f"   ⚠️  No trades generated - strategy may be too conservative")
            print(f"   💡 This could be due to:")
            print(f"      • Market conditions not meeting signal criteria")
            print(f"      • Strategy parameters too strict")
            print(f"      • Insufficient market data")
        
        return result
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def check_readiness():
    """Check if system is ready for live trading"""
    print(f"\n🎯 Live Trading Readiness Check")
    print("=" * 40)
    
    try:
        from src.trading.binance_client import BinanceTradingClient
        from config import binance_config, trading_config
        
        # Test connection
        client = BinanceTradingClient()
        await client.connect()
        
        # Get account info
        account = await client.get_account_info()
        usdt_balance = 0.0
        for balance in account.get('balances', []):
            if balance['asset'] == 'USDT':
                usdt_balance = float(balance['free'])
                break
        
        print(f"📊 Account Status:")
        print(f"   USDT Balance: ${usdt_balance:.2f}")
        print(f"   Can Trade: {account.get('canTrade', False)}")
        print(f"   Testnet Mode: {binance_config.testnet}")
        
        # Check if ready
        ready = True
        issues = []
        
        if usdt_balance < 10:
            ready = False
            issues.append("Low USDT balance (need at least $10)")
        
        if not account.get('canTrade', False):
            ready = False
            issues.append("Trading not enabled on account")
        
        if binance_config.testnet:
            print(f"   ⚠️  Using live trading with testnet safety settings")
        
        await client.disconnect()
        
        if ready:
            print(f"\n🎉 System is ready for live trading!")
            print(f"\n🚀 You can start with:")
            print(f"   python main.py live")
        else:
            print(f"\n⚠️  System needs attention:")
            for issue in issues:
                print(f"   • {issue}")
        
        return ready
        
    except Exception as e:
        print(f"❌ Readiness check failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Backtest and Readiness Check")
        print("=" * 50)
        
        # Run backtest
        result = await run_backtest()
        
        if result:
            # Check readiness
            ready = await check_readiness()
            
            if ready:
                print(f"\n🎉 ALL SYSTEMS READY!")
                print(f"\n🎯 Your trading bot is ready for live trading!")
                print(f"\n⚠️  Remember:")
                print(f"   • You're using live trading with safety limits")
                print(f"   • Maximum trade size: $10")
                print(f"   • Monitor all trades closely")
                print(f"   • Start with small amounts")
            else:
                print(f"\n⚠️  System needs some adjustments before live trading")
        else:
            print(f"\n❌ Backtest failed - check the errors above")
    
    asyncio.run(main())