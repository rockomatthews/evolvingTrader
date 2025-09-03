#!/usr/bin/env python3
"""
Diagnose why the strategy is generating zero trades
"""
import asyncio
import sys
import os
import pandas as pd
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def diagnose_zero_trades():
    """Diagnose why no trades are being generated"""
    print("🔍 Diagnosing Zero Trades Issue")
    print("=" * 50)
    
    try:
        from src.strategy.evolving_strategy import EvolvingStrategy
        from src.trading.binance_client import BinanceTradingClient
        from config import trading_config
        
        # Create strategy and client
        strategy = EvolvingStrategy(['BTCUSDT'])
        client = BinanceTradingClient()
        await client.connect()
        
        print("📊 Step 1: Testing Market Data...")
        df = await strategy.update_market_data('BTCUSDT')
        
        if df.empty:
            print("❌ No market data - this is the problem!")
            return False
        
        print(f"✅ Market data: {len(df)} rows")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
        
        # Check latest data
        latest = df.iloc[-1]
        current_price = latest['close']
        
        print(f"\n📈 Step 2: Analyzing Latest Data...")
        print(f"   Current Price: ${current_price:.2f}")
        print(f"   RSI: {latest.get('rsi', 'N/A')}")
        print(f"   MACD: {latest.get('macd', 'N/A')}")
        print(f"   MACD Signal: {latest.get('macd_signal', 'N/A')}")
        print(f"   Volume: {latest.get('volume', 'N/A'):,.0f}")
        
        # Check if technical indicators are calculated
        print(f"\n🔧 Step 3: Checking Technical Indicators...")
        indicators = ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'ema_fast', 'ema_slow']
        for indicator in indicators:
            value = latest.get(indicator, None)
            if pd.isna(value):
                print(f"   ❌ {indicator}: Not calculated")
            else:
                print(f"   ✅ {indicator}: {value:.4f}")
        
        print(f"\n🎯 Step 4: Testing Individual Strategies...")
        
        # Test momentum strategy
        print(f"\n   📊 Momentum Strategy:")
        momentum = strategy._momentum_strategy(latest, current_price)
        print(f"      Signal: {momentum['signal'].value}")
        print(f"      Confidence: {momentum['confidence']:.2f}")
        print(f"      Reasoning: {momentum['reasoning']}")
        
        # Test mean reversion
        print(f"\n   📊 Mean Reversion Strategy:")
        mean_rev = strategy._mean_reversion_strategy(latest, current_price)
        print(f"      Signal: {mean_rev['signal'].value}")
        print(f"      Confidence: {mean_rev['confidence']:.2f}")
        print(f"      Reasoning: {mean_rev['reasoning']}")
        
        # Test trend strategy
        print(f"\n   📊 Trend Strategy:")
        trend = strategy._trend_strategy(latest, current_price)
        print(f"      Signal: {trend['signal'].value}")
        print(f"      Confidence: {trend['confidence']:.2f}")
        print(f"      Reasoning: {trend['reasoning']}")
        
        # Test volume strategy
        print(f"\n   📊 Volume Strategy:")
        volume = strategy._volume_strategy(latest, current_price)
        print(f"      Signal: {volume['signal'].value}")
        print(f"      Confidence: {volume['confidence']:.2f}")
        print(f"      Reasoning: {volume['reasoning']}")
        
        print(f"\n🔄 Step 5: Testing Signal Combination...")
        combined = strategy._combine_signals(momentum, mean_rev, trend, volume)
        print(f"   Combined Signal: {combined['signal'].value}")
        print(f"   Combined Confidence: {combined['confidence']:.2f}")
        print(f"   Combined Reasoning: {combined['reasoning']}")
        
        print(f"\n⚙️ Step 6: Checking Strategy Parameters...")
        params = strategy.parameters
        print(f"   RSI Oversold: {params.rsi_oversold}")
        print(f"   RSI Overbought: {params.rsi_overbought}")
        print(f"   Min Signal Confidence: {params.min_signal_confidence}")
        print(f"   Max Position Size: {params.max_position_size}")
        
        # Check if parameters are too strict
        print(f"\n🔍 Step 7: Parameter Analysis...")
        issues = []
        
        if params.min_signal_confidence > 0.5:
            issues.append(f"Min confidence too high: {params.min_signal_confidence}")
        
        if params.rsi_oversold > 25:
            issues.append(f"RSI oversold too high: {params.rsi_oversold}")
        
        if params.rsi_overbought < 75:
            issues.append(f"RSI overbought too low: {params.rsi_overbought}")
        
        if issues:
            print(f"   ⚠️  Potential issues:")
            for issue in issues:
                print(f"      • {issue}")
        else:
            print(f"   ✅ Parameters look reasonable")
        
        # Test with relaxed parameters
        print(f"\n🧪 Step 8: Testing with Relaxed Parameters...")
        original_confidence = params.min_signal_confidence
        params.min_signal_confidence = 0.3  # Lower threshold
        
        relaxed_combined = strategy._combine_signals(momentum, mean_rev, trend, volume)
        print(f"   With relaxed confidence (0.3): {relaxed_combined['signal'].value}")
        print(f"   Confidence: {relaxed_combined['confidence']:.2f}")
        
        # Restore original
        params.min_signal_confidence = original_confidence
        
        await client.disconnect()
        
        print(f"\n💡 Recommendations:")
        if combined['confidence'] < params.min_signal_confidence:
            print(f"   • Lower min_signal_confidence from {params.min_signal_confidence} to 0.3-0.4")
        
        if all(s['signal'].value == 'HOLD' for s in [momentum, mean_rev, trend, volume]):
            print(f"   • All individual strategies are HOLD - market may be ranging")
            print(f"   • Consider adding more sensitive indicators")
            print(f"   • Try different timeframes")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnose_zero_trades())
    if success:
        print(f"\n🎯 Diagnosis complete! Check the recommendations above.")
    else:
        print(f"\n❌ Diagnosis failed!")