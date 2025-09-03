#!/usr/bin/env python3
"""
Simple backtest runner that bypasses Pinecone for testing
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def run_simple_backtest():
    """Run a simple backtest without Pinecone"""
    try:
        print("🚀 Starting Simple Backtest (without Pinecone)...")
        
        # Import the backtester directly
        from src.backtesting.backtester import Backtester
        from datetime import datetime, timedelta
        
        # Create backtester
        backtester = Backtester(initial_capital=1000.0)
        
        # Define backtest parameters
        symbol = 'BTCUSDT'
        start_date = datetime.now() - timedelta(days=30)  # 30 days
        end_date = datetime.now()
        
        print(f"📊 Running backtest for {symbol}")
        print(f"📅 Period: {start_date.date()} to {end_date.date()}")
        print(f"💰 Initial Capital: $1,000")
        
        # Run backtest
        result = await backtester.run_backtest(symbol, start_date, end_date)
        
        # Print results
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: $1,000")
        print(f"Total Return: {result.total_return:.2f}%")
        print(f"Total Trades: {result.total_trades}")
        print(f"Win Rate: {result.win_rate:.1f}%")
        print(f"Profit Factor: {result.profit_factor:.2f}")
        print(f"Max Drawdown: {result.max_drawdown:.2f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Calmar Ratio: {result.calmar_ratio:.2f}")
        
        if result.performance_metrics:
            print("\nAdditional Metrics:")
            for key, value in result.performance_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        print("="*50)
        print("✅ Backtest completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_simple_backtest())
    if success:
        print("\n🎉 You can now try the full system with: python main.py backtest")
    else:
        print("\n❌ Please check the errors above")