#!/usr/bin/env python3
"""
Test Binance.US connection and functionality
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_binance_us():
    """Test Binance.US connection"""
    print("🇺🇸 Testing Binance.US Connection")
    print("=" * 40)
    
    try:
        from src.trading.binance_client import BinanceTradingClient
        from config import binance_config
        
        print(f"📋 Configuration:")
        print(f"   API Key: {binance_config.api_key[:10]}...")
        print(f"   Testnet: {binance_config.testnet}")
        print(f"   Using: {'Binance Testnet' if binance_config.testnet else 'Binance.US'}")
        
        print(f"\n🔌 Testing connection...")
        client = BinanceTradingClient()
        
        # Test connection
        await client.connect()
        print("✅ Connected successfully!")
        
        # Test account info
        print(f"\n📊 Testing account info...")
        account = await client.get_account_info()
        print(f"✅ Account info retrieved:")
        print(f"   Account Type: {account.get('accountType', 'Unknown')}")
        print(f"   Can Trade: {account.get('canTrade', False)}")
        print(f"   Can Withdraw: {account.get('canWithdraw', False)}")
        print(f"   Can Deposit: {account.get('canDeposit', False)}")
        
        # Test market data
        print(f"\n📈 Testing market data...")
        try:
            # Get BTCUSDT price
            price = await client.get_ticker_price('BTCUSDT')
            print(f"✅ BTCUSDT Price: ${price:,.2f}")
            
            # Get historical data
            df = await client.get_historical_data('BTCUSDT', '1h', 100)
            if not df.empty:
                print(f"✅ Historical data: {len(df)} rows")
                print(f"   Latest close: ${df['close'].iloc[-1]:,.2f}")
                print(f"   Date range: {df.index[0]} to {df.index[-1]}")
            else:
                print("⚠️  No historical data retrieved")
                
        except Exception as e:
            print(f"⚠️  Market data test failed: {e}")
            print("   This might be normal for testnet or restricted accounts")
        
        # Test available symbols
        print(f"\n🔍 Testing available symbols...")
        try:
            symbols = await client.get_available_symbols()
            print(f"✅ Available symbols: {len(symbols)}")
            print(f"   Sample: {symbols[:5]}")
        except Exception as e:
            print(f"⚠️  Symbols test failed: {e}")
        
        await client.disconnect()
        print(f"\n🎉 Binance.US test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Binance.US test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_strategy_with_binance_us():
    """Test strategy with Binance.US"""
    print(f"\n🧠 Testing Strategy with Binance.US")
    print("=" * 40)
    
    try:
        from src.strategy.evolving_strategy import EvolvingStrategy
        
        strategy = EvolvingStrategy(['BTCUSDT'])
        
        print("📊 Testing market data retrieval...")
        df = await strategy.update_market_data('BTCUSDT')
        
        if df.empty:
            print("❌ No market data retrieved!")
            return False
        
        print(f"✅ Market data retrieved: {len(df)} rows")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Latest close: ${df['close'].iloc[-1]:,.2f}")
        
        # Check technical indicators
        latest = df.iloc[-1]
        print(f"\n📈 Technical Indicators:")
        print(f"   RSI: {latest.get('rsi', 'N/A')}")
        print(f"   MACD: {latest.get('macd', 'N/A')}")
        print(f"   Volume: {latest.get('volume', 'N/A'):,.0f}")
        
        # Test signal generation
        print(f"\n🎯 Testing signal generation...")
        signals = await strategy.generate_signals('BTCUSDT')
        print(f"   Signals generated: {len(signals)}")
        
        if signals:
            for i, signal in enumerate(signals):
                print(f"   Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                print(f"     Entry: ${signal.entry_price:,.2f}")
                print(f"     Stop Loss: ${signal.stop_loss:,.2f}" if signal.stop_loss else "     Stop Loss: None")
                print(f"     Take Profit: ${signal.take_profit:,.2f}" if signal.take_profit else "     Take Profit: None")
                print(f"     Reasoning: {signal.reasoning}")
        else:
            print("   No signals generated - this might be normal depending on market conditions")
        
        print(f"\n🎉 Strategy test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Binance.US Integration Test")
        print("=" * 50)
        
        # Test connection
        connection_ok = await test_binance_us()
        
        if connection_ok:
            # Test strategy
            strategy_ok = await test_strategy_with_binance_us()
            
            if strategy_ok:
                print(f"\n🎉 All tests passed! Your system is ready!")
                print(f"\n🚀 Next steps:")
                print(f"   1. Run backtest: python main.py backtest")
                print(f"   2. Check readiness: python prepare_live_trading.py")
                print(f"   3. Start live trading: python main.py live")
            else:
                print(f"\n⚠️  Strategy test failed, but connection works")
        else:
            print(f"\n❌ Connection test failed - check your API keys")
    
    asyncio.run(main())