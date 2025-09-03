#!/usr/bin/env python3
"""
Test script to verify configuration is working
"""

def test_config():
    """Test all configuration classes"""
    try:
        print("🔍 Testing configuration...")
        
        # Test trading config
        from config import trading_config
        print(f"✅ Trading config: initial_capital = {trading_config.initial_capital}")
        
        # Test binance config
        from config import binance_config
        print(f"✅ Binance config: api_key = {binance_config.api_key[:10]}...")
        print(f"✅ Binance config: testnet = {binance_config.testnet}")
        
        # Test OpenAI config
        from config import openai_config
        print(f"✅ OpenAI config: api_key = {openai_config.api_key[:10]}...")
        print(f"✅ OpenAI config: model = {openai_config.model}")
        
        # Test Pinecone config
        from config import pinecone_config
        print(f"✅ Pinecone config: api_key = {pinecone_config.api_key[:10]}...")
        
        # Test database config
        from config import database_config
        print(f"✅ Database config: url = {database_config.url[:20]}...")
        
        # Test Redis config
        from config import redis_config
        print(f"✅ Redis config: url = {redis_config.url[:20]}...")
        
        print("\n🎉 All configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test all imports"""
    try:
        print("\n🔍 Testing imports...")
        
        # Test basic imports
        import numpy as np
        print("✅ numpy imported")
        
        import pandas as pd
        print("✅ pandas imported")
        
        import ta
        print("✅ ta imported")
        
        # Test trading imports
        from src.trading.binance_client import BinanceTradingClient
        print("✅ BinanceTradingClient imported")
        
        # Test strategy imports
        from src.strategy.evolving_strategy import EvolvingStrategy
        print("✅ EvolvingStrategy imported")
        
        # Test memory imports
        from src.memory.pinecone_client import PineconeMemoryClient
        print("✅ PineconeMemoryClient imported")
        
        print("\n🎉 All import tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EvolvingTrader Configuration Test")
    print("=" * 40)
    
    config_ok = test_config()
    imports_ok = test_imports()
    
    if config_ok and imports_ok:
        print("\n✅ All tests passed! You can now run:")
        print("   python main.py backtest")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")