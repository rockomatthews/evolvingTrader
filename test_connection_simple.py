#!/usr/bin/env python3
"""
Simple connection test to diagnose Binance.US issues
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_connection():
    """Test different connection methods"""
    print("🔍 Testing Binance Connection Methods")
    print("=" * 50)
    
    try:
        from binance import AsyncClient
        from config import binance_config
        
        print(f"📋 Configuration:")
        print(f"   API Key: {binance_config.api_key[:10]}...")
        print(f"   Testnet: {binance_config.testnet}")
        print()
        
        # Test 1: Regular Binance (should fail in US)
        print("1️⃣ Testing regular Binance...")
        try:
            client = await AsyncClient.create(
                api_key=binance_config.api_key,
                api_secret=binance_config.secret_key,
                testnet=binance_config.testnet
            )
            account = await client.get_account()
            print("   ✅ Regular Binance works (unexpected!)")
            await client.close_connection()
        except Exception as e:
            print(f"   ❌ Regular Binance failed (expected): {e}")
        
        # Test 2: Binance.US
        print("\n2️⃣ Testing Binance.US...")
        try:
            client = await AsyncClient.create(
                api_key=binance_config.api_key,
                api_secret=binance_config.secret_key,
                testnet=binance_config.testnet,
                tld='us'
            )
            account = await client.get_account()
            print("   ✅ Binance.US works!")
            print(f"   Account Type: {account.get('accountType', 'Unknown')}")
            await client.close_connection()
            return True
        except Exception as e:
            print(f"   ❌ Binance.US failed: {e}")
        
        # Test 3: Try with different testnet settings
        print("\n3️⃣ Testing different testnet configurations...")
        test_configs = [
            {"testnet": True, "tld": "us", "name": "Binance.US Testnet"},
            {"testnet": True, "tld": "com", "name": "Binance Testnet"},
            {"testnet": False, "tld": "us", "name": "Binance.US Live"},
        ]
        
        for config in test_configs:
            try:
                print(f"   Testing {config['name']}...")
                client = await AsyncClient.create(
                    api_key=binance_config.api_key,
                    api_secret=binance_config.secret_key,
                    testnet=config['testnet'],
                    tld=config['tld']
                )
                account = await client.get_account()
                print(f"   ✅ {config['name']} works!")
                await client.close_connection()
                return True
            except Exception as e:
                print(f"   ❌ {config['name']} failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_market_data():
    """Test market data retrieval"""
    print(f"\n📊 Testing Market Data Retrieval")
    print("=" * 40)
    
    try:
        from binance import AsyncClient
        from config import binance_config
        
        # Try Binance.US first
        try:
            client = await AsyncClient.create(
                api_key=binance_config.api_key,
                api_secret=binance_config.secret_key,
                testnet=binance_config.testnet,
                tld='us'
            )
            
            # Test ticker price
            ticker = await client.get_symbol_ticker(symbol="BTCUSDT")
            print(f"✅ BTCUSDT Price: ${float(ticker['price']):,.2f}")
            
            # Test historical data
            klines = await client.get_historical_klines("BTCUSDT", "1h", "1 day ago UTC")
            if klines:
                print(f"✅ Historical data: {len(klines)} candles")
                latest = klines[-1]
                print(f"   Latest close: ${float(latest[4]):,.2f}")
            else:
                print("⚠️  No historical data")
            
            await client.close_connection()
            return True
            
        except Exception as e:
            print(f"❌ Market data test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Binance Connection Diagnostic")
        print("=" * 50)
        
        # Test connection
        connection_ok = await test_connection()
        
        if connection_ok:
            # Test market data
            market_ok = await test_market_data()
            
            if market_ok:
                print(f"\n🎉 All tests passed! Your Binance.US connection works!")
                print(f"\n🚀 You can now run:")
                print(f"   python main.py backtest")
            else:
                print(f"\n⚠️  Connection works but market data failed")
        else:
            print(f"\n❌ Connection tests failed")
            print(f"\n💡 Possible solutions:")
            print(f"   1. Check your API keys are from Binance.US")
            print(f"   2. Make sure API keys have trading permissions")
            print(f"   3. Try creating new API keys")
            print(f"   4. Check if your account is verified")
    
    asyncio.run(main())