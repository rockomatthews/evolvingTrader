#!/usr/bin/env python3
"""
Basic import test to verify the system is working
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing critical imports...")
    
    try:
        # Test configuration
        print("📋 Testing configuration...")
        from config import trading_config, binance_config, openai_config
        print("✅ Configuration imports successful")
        
        # Test basic trading components
        print("📈 Testing trading components...")
        from src.trading.binance_client import BinanceTradingClient
        print("✅ Binance client import successful")
        
        # Test strategy
        print("🧠 Testing strategy...")
        from src.strategy.evolving_strategy import EvolvingStrategy
        print("✅ Strategy import successful")
        
        # Test backtester
        print("📊 Testing backtester...")
        from src.backtesting.backtester import Backtester
        print("✅ Backtester import successful")
        
        # Test market analyzer (with optional sklearn)
        print("🔍 Testing market analyzer...")
        from src.analysis.market_analyzer import MarketAnalyzer
        print("✅ Market analyzer import successful")
        
        print("\n🎉 All critical imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import trading_config, binance_config, openai_config
        
        print(f"✅ Trading config loaded:")
        print(f"   - Initial capital: ${trading_config.initial_capital}")
        print(f"   - Max position size: {trading_config.max_position_size}")
        print(f"   - Risk per trade: {trading_config.risk_per_trade}")
        
        print(f"✅ Binance config loaded:")
        print(f"   - API key: {binance_config.api_key[:10]}...")
        print(f"   - Testnet: {binance_config.testnet}")
        
        print(f"✅ OpenAI config loaded:")
        print(f"   - API key: {openai_config.api_key[:10]}...")
        print(f"   - Model: {openai_config.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EvolvingTrader - Basic Import Test")
    print("=" * 40)
    
    imports_ok = test_imports()
    config_ok = test_configuration()
    
    if imports_ok and config_ok:
        print("\n🎉 All tests passed! The system is ready.")
        print("\n🚀 Next steps:")
        print("   1. Run simple backtest: python run_backtest_simple.py")
        print("   2. Run full backtest: python main.py backtest")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")