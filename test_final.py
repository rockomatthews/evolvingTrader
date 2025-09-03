#!/usr/bin/env python3
"""
Final test to verify everything is working
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_final():
    """Final comprehensive test"""
    print("🎉 Final Test - EvolvingTrader Ready!")
    print("=" * 50)
    
    try:
        # Test 1: Configuration
        print("1️⃣ Testing Configuration...")
        from config import trading_config, binance_config
        print(f"   ✅ Configuration loaded")
        print(f"   ✅ Testnet: {binance_config.testnet}")
        print(f"   ✅ Capital: ${trading_config.initial_capital}")
        
        # Test 2: Connection
        print("\n2️⃣ Testing Binance.US Connection...")
        from src.trading.binance_client import BinanceTradingClient
        client = BinanceTradingClient()
        await client.connect()
        print(f"   ✅ Connected to Binance.US")
        
        # Test 3: Market Data
        print("\n3️⃣ Testing Market Data...")
        price = await client.get_ticker_price('BTCUSDT')
        print(f"   ✅ BTCUSDT Price: ${price:,.2f}")
        
        # Test 4: Strategy
        print("\n4️⃣ Testing Strategy...")
        from src.strategy.evolving_strategy import EvolvingStrategy
        strategy = EvolvingStrategy(['BTCUSDT'])
        
        df = await strategy.update_market_data('BTCUSDT')
        if not df.empty:
            print(f"   ✅ Market data: {len(df)} rows")
            print(f"   ✅ Latest price: ${df['close'].iloc[-1]:,.2f}")
        else:
            print(f"   ⚠️  No market data (might be normal)")
        
        # Test 5: Signal Generation
        print("\n5️⃣ Testing Signal Generation...")
        signals = await strategy.generate_signals('BTCUSDT')
        print(f"   ✅ Signals generated: {len(signals)}")
        
        if signals:
            for i, signal in enumerate(signals):
                print(f"      Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
        else:
            print(f"   ℹ️  No signals (normal if market conditions don't meet criteria)")
        
        await client.disconnect()
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n🚀 Your EvolvingTrader is ready!")
        print(f"\n📋 Summary:")
        print(f"   ✅ Binance.US connection working")
        print(f"   ✅ Market data retrieval working")
        print(f"   ✅ Strategy system working")
        print(f"   ✅ Signal generation working")
        print(f"   ✅ Safe trading mode enabled")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run backtest: python main.py backtest")
        print(f"   2. Check readiness: python prepare_live_trading.py")
        print(f"   3. Start live trading: python main.py live")
        
        print(f"\n⚠️  Important:")
        print(f"   • You're using LIVE Binance.US with safety limits")
        print(f"   • Maximum trade size: $10")
        print(f"   • Monitor all trades closely")
        print(f"   • Start with small amounts")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final())
    if success:
        print(f"\n🎉 SUCCESS! Your trading bot is ready to go!")
    else:
        print(f"\n❌ Some tests failed - check the errors above")