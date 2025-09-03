#!/usr/bin/env python3
"""
Diagnostic script to understand why the strategy isn't generating trades
"""
import asyncio
import sys
import os
import pandas as pd
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def diagnose_strategy():
    """Diagnose the trading strategy"""
    print("🔍 Diagnosing Trading Strategy...")
    print("=" * 50)
    
    try:
        from src.strategy.evolving_strategy import EvolvingStrategy
        from src.trading.binance_client import BinanceTradingClient
        from datetime import datetime, timedelta
        
        # Create strategy and client
        strategy = EvolvingStrategy(['BTCUSDT'])
        binance_client = BinanceTradingClient()
        
        print("📊 Testing market data retrieval...")
        
        # Test market data
        df = await strategy.update_market_data('BTCUSDT')
        if df.empty:
            print("❌ No market data retrieved!")
            return False
        
        print(f"✅ Market data retrieved: {len(df)} rows")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check latest data
        latest = df.iloc[-1]
        print(f"\n📈 Latest data for BTCUSDT:")
        print(f"   Close: ${latest['close']:.2f}")
        print(f"   Volume: {latest['volume']:,.0f}")
        print(f"   RSI: {latest.get('rsi', 'N/A')}")
        print(f"   MACD: {latest.get('macd', 'N/A')}")
        
        # Test signal generation
        print(f"\n🎯 Testing signal generation...")
        signals = await strategy.generate_signals('BTCUSDT')
        print(f"   Signals generated: {len(signals)}")
        
        if signals:
            for i, signal in enumerate(signals):
                print(f"   Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                print(f"     Reasoning: {signal.reasoning}")
        else:
            print("   No signals generated - investigating...")
            
            # Test individual strategies
            print(f"\n🔍 Testing individual strategies...")
            
            # Test momentum strategy
            momentum = strategy._momentum_strategy(latest, latest['close'])
            print(f"   Momentum: {momentum['signal'].value} (confidence: {momentum['confidence']:.2f})")
            print(f"     Reasoning: {momentum['reasoning']}")
            
            # Test mean reversion
            mean_rev = strategy._mean_reversion_strategy(latest, latest['close'])
            print(f"   Mean Reversion: {mean_rev['signal'].value} (confidence: {mean_rev['confidence']:.2f})")
            print(f"     Reasoning: {mean_rev['reasoning']}")
            
            # Test trend
            trend = strategy._trend_strategy(latest, latest['close'])
            print(f"   Trend: {trend['signal'].value} (confidence: {trend['confidence']:.2f})")
            print(f"     Reasoning: {trend['reasoning']}")
            
            # Test volume
            volume = strategy._volume_strategy(latest, latest['close'])
            print(f"   Volume: {volume['signal'].value} (confidence: {volume['confidence']:.2f})")
            print(f"     Reasoning: {volume['reasoning']}")
            
            # Test signal combination
            combined = strategy._combine_signals(momentum, mean_rev, trend, volume)
            print(f"   Combined: {combined['signal'].value} (confidence: {combined['confidence']:.2f})")
            print(f"     Reasoning: {combined['reasoning']}")
        
        # Check strategy parameters
        print(f"\n⚙️ Strategy Parameters:")
        params = strategy.parameters
        print(f"   RSI oversold: {params.rsi_oversold}")
        print(f"   RSI overbought: {params.rsi_overbought}")
        print(f"   BB period: {params.bb_period}")
        print(f"   BB std: {params.bb_std}")
        print(f"   Min confidence: {params.min_signal_confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnose_strategy())
    if success:
        print(f"\n🎉 Diagnosis completed!")
    else:
        print(f"\n❌ Diagnosis failed!")