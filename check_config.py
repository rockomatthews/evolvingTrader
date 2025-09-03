#!/usr/bin/env python3
"""
Check configuration and environment variables
"""
import os
from dotenv import load_dotenv

def check_config():
    """Check configuration and environment variables"""
    print("🔍 Checking Configuration")
    print("=" * 30)
    
    # Load .env file
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'OPENAI_API_KEY',
        'PINECONE_API_KEY'
    ]
    
    print("📋 Environment Variables:")
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:10]}...")
        else:
            print(f"   ❌ {var}: Not set")
            all_good = False
    
    # Check optional variables
    optional_vars = [
        'BINANCE_TESTNET',
        'INITIAL_CAPITAL',
        'MAX_POSITION_SIZE',
        'RISK_PER_TRADE'
    ]
    
    print(f"\n📋 Optional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Not set (using default)")
    
    # Check .env file
    print(f"\n📁 .env File:")
    if os.path.exists('.env'):
        print(f"   ✅ .env file exists")
        with open('.env', 'r') as f:
            lines = f.readlines()
            print(f"   📄 {len(lines)} lines in .env file")
    else:
        print(f"   ❌ .env file not found")
        all_good = False
    
    # Test configuration loading
    print(f"\n🔧 Testing Configuration Loading:")
    try:
        from config import binance_config, trading_config, openai_config
        
        print(f"   ✅ Trading config loaded")
        print(f"      Initial capital: ${trading_config.initial_capital}")
        print(f"      Max position size: {trading_config.max_position_size}")
        
        print(f"   ✅ Binance config loaded")
        print(f"      API key: {binance_config.api_key[:10]}...")
        print(f"      Testnet: {binance_config.testnet}")
        
        print(f"   ✅ OpenAI config loaded")
        print(f"      API key: {openai_config.api_key[:10]}...")
        print(f"      Model: {openai_config.model}")
        
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        all_good = False
    
    return all_good

def show_sample_env():
    """Show sample .env file"""
    print(f"\n📝 Sample .env file:")
    print("=" * 30)
    print("""
# Binance.US API Keys (for US users)
BINANCE_API_KEY=your_binance_us_api_key_here
BINANCE_SECRET_KEY=your_binance_us_secret_key_here
BINANCE_TESTNET=true

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone API Key
PINECONE_API_KEY=your_pinecone_api_key_here

# Trading Configuration
INITIAL_CAPITAL=1000.0
MAX_POSITION_SIZE=0.1
RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05

# Database (optional)
NEON_DATABASE_URL=your_neon_database_url_here

# Redis (optional)
REDIS_URL=your_redis_url_here
UPSTASH_REDIS_REST_URL=your_upstash_redis_rest_url_here
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_rest_token_here
""")

if __name__ == "__main__":
    print("🚀 Configuration Checker")
    print("=" * 50)
    
    config_ok = check_config()
    
    if config_ok:
        print(f"\n🎉 Configuration looks good!")
        print(f"\n🚀 Next steps:")
        print(f"   1. Test connection: python test_connection_simple.py")
        print(f"   2. Run backtest: python main.py backtest")
    else:
        print(f"\n❌ Configuration issues found!")
        print(f"\n💡 Please check the issues above")
        show_sample_env()