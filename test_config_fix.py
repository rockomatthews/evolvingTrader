#!/usr/bin/env python3
"""
Test the configuration fix
"""
def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration fix...")
    
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
        
        print("\n🎉 Configuration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_config()