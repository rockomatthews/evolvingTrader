#!/usr/bin/env python3
"""
Test safe live trading setup for US users
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_safe_live_trading():
    """Test safe live trading setup"""
    print("🛡️  Testing Safe Live Trading Setup")
    print("=" * 50)
    
    try:
        from src.trading.binance_client import BinanceTradingClient
        from src.trading.safe_trading_config import safe_trading_config
        from config import binance_config, trading_config
        
        print(f"📋 Configuration:")
        print(f"   Testnet setting: {binance_config.testnet}")
        print(f"   Original capital: ${trading_config.initial_capital}")
        print(f"   Safe capital: ${safe_trading_config.initial_capital}")
        print(f"   Safe position size: {safe_trading_config.max_position_size*100:.1f}%")
        print(f"   Safe risk per trade: {safe_trading_config.risk_per_trade*100:.1f}%")
        
        print(f"\n🔌 Testing connection...")
        client = BinanceTradingClient()
        await client.connect()
        print("✅ Connected successfully!")
        
        # Test account info
        print(f"\n📊 Account Information:")
        account = await client.get_account_info()
        print(f"   Account Type: {account.get('accountType', 'Unknown')}")
        print(f"   Can Trade: {account.get('canTrade', False)}")
        
        # Check balances
        balances = account.get('balances', [])
        usdt_balance = 0.0
        for balance in balances:
            if balance['asset'] == 'USDT':
                usdt_balance = float(balance['free'])
                break
        
        print(f"   USDT Balance: ${usdt_balance:.2f}")
        
        # Test safe position sizing
        print(f"\n🛡️  Safe Position Sizing:")
        safe_size = safe_trading_config.get_safe_position_size(usdt_balance)
        print(f"   Account Balance: ${usdt_balance:.2f}")
        print(f"   Safe Position Size: ${safe_size:.2f}")
        print(f"   Max Trade Amount: ${safe_trading_config.max_trade_amount:.2f}")
        
        # Test market data
        print(f"\n📈 Testing Market Data:")
        try:
            price = await client.get_ticker_price('BTCUSDT')
            print(f"   BTCUSDT Price: ${price:,.2f}")
            
            # Calculate safe trade amounts
            btc_amount = safe_size / price
            print(f"   Safe BTC Amount: {btc_amount:.6f} BTC")
            print(f"   Trade Value: ${btc_amount * price:.2f}")
            
        except Exception as e:
            print(f"   ⚠️  Market data test failed: {e}")
        
        await client.disconnect()
        
        print(f"\n🎉 Safe live trading setup verified!")
        print(f"\n⚠️  IMPORTANT SAFETY NOTES:")
        print(f"   • You're using LIVE trading with safety limits")
        print(f"   • Maximum trade size: ${safe_trading_config.max_trade_amount}")
        print(f"   • Maximum position size: {safe_trading_config.max_position_size*100:.1f}%")
        print(f"   • Maximum risk per trade: {safe_trading_config.risk_per_trade*100:.1f}%")
        print(f"   • Monitor all trades closely!")
        
        return True
        
    except Exception as e:
        print(f"❌ Safe live trading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_strategy_with_safe_config():
    """Test strategy with safe configuration"""
    print(f"\n🧠 Testing Strategy with Safe Configuration")
    print("=" * 50)
    
    try:
        from src.strategy.evolving_strategy import EvolvingStrategy
        from src.trading.safe_trading_config import safe_trading_config
        from config import trading_config
        
        # Override trading config with safe settings
        original_capital = trading_config.initial_capital
        original_position_size = trading_config.max_position_size
        original_risk = trading_config.risk_per_trade
        
        # Apply safe settings
        trading_config.initial_capital = safe_trading_config.initial_capital
        trading_config.max_position_size = safe_trading_config.max_position_size
        trading_config.risk_per_trade = safe_trading_config.risk_per_trade
        
        print(f"📊 Safe Strategy Configuration:")
        print(f"   Capital: ${trading_config.initial_capital}")
        print(f"   Position Size: {trading_config.max_position_size*100:.1f}%")
        print(f"   Risk per Trade: {trading_config.risk_per_trade*100:.1f}%")
        
        strategy = EvolvingStrategy(['BTCUSDT'])
        
        print(f"\n📈 Testing market data...")
        df = await strategy.update_market_data('BTCUSDT')
        
        if df.empty:
            print("❌ No market data retrieved!")
            return False
        
        print(f"✅ Market data: {len(df)} rows")
        print(f"   Latest close: ${df['close'].iloc[-1]:,.2f}")
        
        print(f"\n🎯 Testing signal generation...")
        signals = await strategy.generate_signals('BTCUSDT')
        print(f"   Signals generated: {len(signals)}")
        
        if signals:
            for i, signal in enumerate(signals):
                print(f"   Signal {i+1}: {signal.signal_type.value}")
                print(f"     Confidence: {signal.confidence:.2f}")
                print(f"     Position Size: {signal.position_size:.4f}")
                print(f"     Trade Value: ${signal.entry_price * signal.position_size:.2f}")
                print(f"     Reasoning: {signal.reasoning}")
        else:
            print("   No signals generated")
        
        # Restore original settings
        trading_config.initial_capital = original_capital
        trading_config.max_position_size = original_position_size
        trading_config.risk_per_trade = original_risk
        
        print(f"\n🎉 Strategy test completed with safe settings!")
        return True
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Safe Live Trading Test for US Users")
        print("=" * 60)
        
        # Test safe live trading
        safe_ok = await test_safe_live_trading()
        
        if safe_ok:
            # Test strategy
            strategy_ok = await test_strategy_with_safe_config()
            
            if strategy_ok:
                print(f"\n🎉 All tests passed! Safe live trading is ready!")
                print(f"\n🚀 You can now run:")
                print(f"   python main.py backtest")
                print(f"   python main.py live")
                print(f"\n⚠️  Remember: You're using LIVE trading with safety limits!")
            else:
                print(f"\n⚠️  Strategy test failed")
        else:
            print(f"\n❌ Safe live trading test failed")
    
    asyncio.run(main())