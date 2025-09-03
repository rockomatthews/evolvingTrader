#!/usr/bin/env python3
"""
Switch to live trading mode and test the strategy
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_strategy_before_live():
    """Test strategy to make sure it generates trades"""
    print("🧪 Quick Strategy Test Before Going Live")
    print("=" * 50)
    
    try:
        from src.strategy.optimized_strategy import OptimizedEvolvingStrategy
        from src.trading.binance_client import BinanceTradingClient
        
        # Test optimized strategy
        strategy = OptimizedEvolvingStrategy(['BTCUSDT'])
        client = BinanceTradingClient()
        await client.connect()
        
        print("📊 Testing Optimized Strategy...")
        signals = await strategy.generate_signals('BTCUSDT')
        
        print(f"   Signals generated: {len(signals)}")
        
        if signals:
            for i, signal in enumerate(signals):
                print(f"   Signal {i+1}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                print(f"     Entry: ${signal.entry_price:,.2f}")
                print(f"     Stop Loss: ${signal.stop_loss:,.2f}" if signal.stop_loss else "     Stop Loss: None")
                print(f"     Take Profit: ${signal.take_profit:,.2f}" if signal.take_profit else "     Take Profit: None")
                print(f"     Reasoning: {signal.reasoning}")
        
        await client.disconnect()
        
        if signals:
            print(f"\n✅ Strategy is generating signals - ready for live trading!")
            return True
        else:
            print(f"\n⚠️  Strategy not generating signals - let's check why...")
            
            # Quick diagnostic
            df = await strategy.update_market_data('BTCUSDT')
            if not df.empty:
                latest = df.iloc[-1]
                print(f"   Latest RSI: {latest.get('rsi', 'N/A')}")
                print(f"   Latest MACD: {latest.get('macd', 'N/A')}")
                print(f"   Min confidence needed: {strategy.parameters.min_signal_confidence}")
            
            return False
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False

def switch_to_live_mode():
    """Switch configuration to live trading mode"""
    print("\n🚀 Switching to Live Trading Mode")
    print("=" * 40)
    
    try:
        # Read current config
        with open('config.py', 'r') as f:
            config_content = f.read()
        
        # Update testnet setting
        if 'binance_testnet: bool = Field(default=True' in config_content:
            config_content = config_content.replace(
                'binance_testnet: bool = Field(default=True',
                'binance_testnet: bool = Field(default=False'
            )
            print("✅ Switched to live trading mode (testnet=False)")
        else:
            print("⚠️  Testnet setting not found or already set to live")
        
        # Update trading config for live trading
        if 'initial_capital: float = Field(default=1000.0' in config_content:
            config_content = config_content.replace(
                'initial_capital: float = Field(default=1000.0',
                'initial_capital: float = Field(default=10.0'  # Start with $10
            )
            print("✅ Set initial capital to $10 for live trading")
        
        if 'max_position_size: float = Field(default=0.1' in config_content:
            config_content = config_content.replace(
                'max_position_size: float = Field(default=0.1',
                'max_position_size: float = Field(default=0.05'  # 5% max position
            )
            print("✅ Set max position size to 5% for live trading")
        
        if 'risk_per_trade: float = Field(default=0.02' in config_content:
            config_content = config_content.replace(
                'risk_per_trade: float = Field(default=0.02',
                'risk_per_trade: float = Field(default=0.01'  # 1% risk per trade
            )
            print("✅ Set risk per trade to 1% for live trading")
        
        # Write updated config
        with open('config.py', 'w') as f:
            f.write(config_content)
        
        print("\n🎯 Live Trading Configuration:")
        print("   • Testnet: False (LIVE TRADING)")
        print("   • Initial Capital: $10")
        print("   • Max Position Size: 5%")
        print("   • Risk per Trade: 1%")
        print("   • Max Daily Loss: 5%")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to switch to live mode: {e}")
        return False

async def test_live_connection():
    """Test live trading connection"""
    print("\n🔌 Testing Live Trading Connection")
    print("=" * 40)
    
    try:
        from src.trading.binance_client import BinanceTradingClient
        from config import binance_config
        
        print(f"📋 Configuration:")
        print(f"   Testnet: {binance_config.testnet}")
        print(f"   API Key: {binance_config.api_key[:10]}...")
        
        client = BinanceTradingClient()
        await client.connect()
        
        # Get account info
        account = await client.get_account_info()
        usdt_balance = 0.0
        for balance in account.get('balances', []):
            if balance['asset'] == 'USDT':
                usdt_balance = float(balance['free'])
                break
        
        print(f"\n📊 Account Status:")
        print(f"   USDT Balance: ${usdt_balance:.2f}")
        print(f"   Can Trade: {account.get('canTrade', False)}")
        print(f"   Account Type: {account.get('accountType', 'Unknown')}")
        
        # Test market data
        price = await client.get_ticker_price('BTCUSDT')
        print(f"   BTCUSDT Price: ${price:,.2f}")
        
        await client.disconnect()
        
        if usdt_balance > 0:
            print(f"\n✅ Ready for live trading with ${usdt_balance:.2f} USDT!")
            return True
        else:
            print(f"\n⚠️  No USDT balance - deposit some USDT to start trading")
            return False
        
    except Exception as e:
        print(f"❌ Live connection test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 GOING LIVE - EvolvingTrader")
        print("=" * 50)
        
        # Test strategy first
        strategy_ok = await test_strategy_before_live()
        
        if strategy_ok:
            # Switch to live mode
            config_ok = switch_to_live_mode()
            
            if config_ok:
                # Test live connection
                live_ok = await test_live_connection()
                
                if live_ok:
                    print(f"\n🎉 READY FOR LIVE TRADING!")
                    print(f"\n🚀 Start live trading with:")
                    print(f"   python main.py live")
                    print(f"\n⚠️  IMPORTANT:")
                    print(f"   • You're now using REAL MONEY")
                    print(f"   • Monitor all trades closely")
                    print(f"   • Start with small amounts")
                    print(f"   • The bot will trade automatically")
                else:
                    print(f"\n⚠️  Live connection test failed")
            else:
                print(f"\n❌ Failed to switch to live mode")
        else:
            print(f"\n⚠️  Strategy not generating signals - may need adjustment")
            print(f"   You can still go live, but the bot might not trade much")
    
    asyncio.run(main())