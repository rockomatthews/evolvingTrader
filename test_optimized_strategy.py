#!/usr/bin/env python3
"""
Test the optimized strategy to see if it generates more trades
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_optimized_strategy():
    """Test the optimized strategy"""
    print("🚀 Testing Optimized Strategy")
    print("=" * 50)
    
    try:
        from src.strategy.optimized_strategy import OptimizedEvolvingStrategy
        from src.strategy.evolving_strategy import EvolvingStrategy
        from src.trading.binance_client import BinanceTradingClient
        
        # Test both strategies
        print("📊 Testing Original Strategy...")
        original_strategy = EvolvingStrategy(['BTCUSDT'])
        
        print("📊 Testing Optimized Strategy...")
        optimized_strategy = OptimizedEvolvingStrategy(['BTCUSDT'])
        
        # Get market data
        print("\n📈 Getting Market Data...")
        original_df = await original_strategy.update_market_data('BTCUSDT')
        optimized_df = await optimized_strategy.update_market_data('BTCUSDT')
        
        if original_df.empty or optimized_df.empty:
            print("❌ No market data available")
            return False
        
        print(f"✅ Market data: {len(original_df)} rows")
        
        # Test signal generation
        print("\n🎯 Testing Signal Generation...")
        
        # Original strategy
        print("\n   📊 Original Strategy:")
        original_signals = await original_strategy.generate_signals('BTCUSDT')
        print(f"      Signals: {len(original_signals)}")
        
        if original_signals:
            for i, signal in enumerate(original_signals):
                print(f"      Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                print(f"        Reasoning: {signal.reasoning}")
        else:
            print(f"      No signals generated")
        
        # Optimized strategy
        print("\n   📊 Optimized Strategy:")
        optimized_signals = await optimized_strategy.generate_signals('BTCUSDT')
        print(f"      Signals: {len(optimized_signals)}")
        
        if optimized_signals:
            for i, signal in enumerate(optimized_signals):
                print(f"      Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                print(f"        Reasoning: {signal.reasoning}")
        else:
            print(f"      No signals generated")
        
        # Compare parameters
        print(f"\n⚙️ Parameter Comparison:")
        print(f"   Original min confidence: {original_strategy.parameters.min_signal_confidence}")
        print(f"   Optimized min confidence: {optimized_strategy.parameters.min_signal_confidence}")
        print(f"   Original RSI oversold: {original_strategy.parameters.rsi_oversold}")
        print(f"   Optimized RSI oversold: {optimized_strategy.parameters.rsi_oversold}")
        print(f"   Original RSI overbought: {original_strategy.parameters.rsi_overbought}")
        print(f"   Optimized RSI overbought: {optimized_strategy.parameters.rsi_overbought}")
        
        # Test individual strategies
        print(f"\n🔍 Testing Individual Strategies (Optimized):")
        latest = optimized_df.iloc[-1]
        current_price = latest['close']
        
        # Test each strategy component
        strategies = [
            ('Momentum', optimized_strategy._momentum_strategy),
            ('Mean Reversion', optimized_strategy._mean_reversion_strategy),
            ('Trend', optimized_strategy._trend_strategy),
            ('Volume', optimized_strategy._volume_strategy),
            ('Stochastic', optimized_strategy._stochastic_strategy)
        ]
        
        for name, strategy_func in strategies:
            try:
                result = strategy_func(latest, current_price)
                print(f"   {name}: {result['signal'].value} (confidence: {result['confidence']:.2f})")
                if result['reasoning']:
                    print(f"      Reasoning: {result['reasoning']}")
            except Exception as e:
                print(f"   {name}: Error - {e}")
        
        # Test signal combination
        print(f"\n🔄 Testing Signal Combination:")
        momentum = optimized_strategy._momentum_strategy(latest, current_price)
        mean_rev = optimized_strategy._mean_reversion_strategy(latest, current_price)
        trend = optimized_strategy._trend_strategy(latest, current_price)
        volume = optimized_strategy._volume_strategy(latest, current_price)
        stochastic = optimized_strategy._stochastic_strategy(latest, current_price)
        
        combined = optimized_strategy._combine_signals(momentum, mean_rev, trend, volume, stochastic)
        print(f"   Combined Signal: {combined['signal'].value}")
        print(f"   Combined Confidence: {combined['confidence']:.2f}")
        print(f"   Combined Reasoning: {combined['reasoning']}")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Original Strategy Signals: {len(original_signals)}")
        print(f"   Optimized Strategy Signals: {len(optimized_signals)}")
        
        if len(optimized_signals) > len(original_signals):
            print(f"   ✅ Optimized strategy generates more signals!")
        elif len(optimized_signals) == len(original_signals):
            print(f"   ⚠️  Both strategies generate the same number of signals")
        else:
            print(f"   ❌ Optimized strategy generates fewer signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_optimized_strategy())
    if success:
        print(f"\n🎉 Optimized strategy test completed!")
        print(f"\n💡 If the optimized strategy generates more signals, you can:")
        print(f"   1. Use it for backtesting")
        print(f"   2. Replace the original strategy")
        print(f"   3. Run live trading with more active signals")
    else:
        print(f"\n❌ Test failed!")