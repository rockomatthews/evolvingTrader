#!/usr/bin/env python3
"""
Script to prepare the system for live trading
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_live_trading_readiness():
    """Check if the system is ready for live trading"""
    print("🚀 Live Trading Readiness Check")
    print("=" * 40)
    
    checks = []
    
    # Check 1: Configuration
    print("1️⃣ Checking configuration...")
    try:
        from config import binance_config, trading_config
        
        if binance_config.testnet:
            print("   ⚠️  Currently in TESTNET mode (safe for testing)")
            checks.append(("Testnet Mode", True, "Safe for testing"))
        else:
            print("   🔴 LIVE TRADING MODE - Real money at risk!")
            checks.append(("Live Mode", True, "Real money at risk"))
        
        print(f"   ✅ API Key: {binance_config.api_key[:10]}...")
        print(f"   ✅ Initial Capital: ${trading_config.initial_capital}")
        checks.append(("Configuration", True, "Loaded successfully"))
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        checks.append(("Configuration", False, str(e)))
    
    # Check 2: API Connection
    print("\n2️⃣ Testing API connection...")
    try:
        import asyncio
        from src.trading.binance_client import BinanceTradingClient
        
        async def test_api():
            client = BinanceTradingClient()
            try:
                # Test connection
                account = await client.get_account_info()
                print(f"   ✅ API connection successful")
                print(f"   ✅ Account type: {account.get('accountType', 'Unknown')}")
                print(f"   ✅ Can trade: {account.get('canTrade', False)}")
                return True
            except Exception as e:
                print(f"   ❌ API connection failed: {e}")
                return False
        
        api_ok = asyncio.run(test_api())
        checks.append(("API Connection", api_ok, "Connection test"))
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        checks.append(("API Connection", False, str(e)))
    
    # Check 3: Strategy Performance
    print("\n3️⃣ Checking strategy performance...")
    try:
        # This would check recent backtest results
        print("   ⚠️  Run backtest first to verify strategy performance")
        print("   💡 Command: python main.py backtest")
        checks.append(("Strategy Performance", False, "Run backtest first"))
        
    except Exception as e:
        print(f"   ❌ Strategy check failed: {e}")
        checks.append(("Strategy Performance", False, str(e)))
    
    # Check 4: Risk Management
    print("\n4️⃣ Checking risk management...")
    try:
        from config import trading_config
        
        risk_checks = []
        
        # Check position size
        if trading_config.max_position_size <= 0.1:
            print(f"   ✅ Max position size: {trading_config.max_position_size*100:.1f}% (conservative)")
            risk_checks.append(True)
        else:
            print(f"   ⚠️  Max position size: {trading_config.max_position_size*100:.1f}% (consider reducing)")
            risk_checks.append(False)
        
        # Check risk per trade
        if trading_config.risk_per_trade <= 0.02:
            print(f"   ✅ Risk per trade: {trading_config.risk_per_trade*100:.1f}% (conservative)")
            risk_checks.append(True)
        else:
            print(f"   ⚠️  Risk per trade: {trading_config.risk_per_trade*100:.1f}% (consider reducing)")
            risk_checks.append(False)
        
        # Check daily loss limit
        if trading_config.max_daily_loss <= 0.05:
            print(f"   ✅ Max daily loss: {trading_config.max_daily_loss*100:.1f}% (conservative)")
            risk_checks.append(True)
        else:
            print(f"   ⚠️  Max daily loss: {trading_config.max_daily_loss*100:.1f}% (consider reducing)")
            risk_checks.append(False)
        
        risk_ok = all(risk_checks)
        checks.append(("Risk Management", risk_ok, f"{sum(risk_checks)}/3 checks passed"))
        
    except Exception as e:
        print(f"   ❌ Risk management check failed: {e}")
        checks.append(("Risk Management", False, str(e)))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 READINESS SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(checks)
    
    for check_name, status, details in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}: {details}")
        if status:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 System appears ready for live trading!")
        print("\n⚠️  IMPORTANT REMINDERS:")
        print("   • Start with small amounts")
        print("   • Monitor the system closely")
        print("   • Have stop-losses in place")
        print("   • Test thoroughly in testnet first")
    else:
        print(f"\n⚠️  System needs attention before live trading")
        print("   • Fix the failed checks above")
        print("   • Run more backtests")
        print("   • Test in testnet mode first")
    
    return passed == total

def show_live_trading_commands():
    """Show commands for live trading"""
    print("\n🚀 LIVE TRADING COMMANDS")
    print("=" * 30)
    print("1. Test in testnet first:")
    print("   python main.py backtest")
    print("   python diagnose_strategy.py")
    print()
    print("2. Switch to live trading (edit config.py):")
    print("   binance_testnet: bool = False")
    print()
    print("3. Start live trading:")
    print("   python main.py live")
    print()
    print("4. Monitor with dashboard:")
    print("   python main.py dashboard")

if __name__ == "__main__":
    ready = check_live_trading_readiness()
    show_live_trading_commands()
    
    if not ready:
        print("\n❌ Not ready for live trading yet. Please address the issues above.")
    else:
        print("\n✅ System appears ready, but proceed with caution!")