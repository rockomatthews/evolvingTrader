#!/usr/bin/env python3
"""
Test script to verify real data is being fetched correctly
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_real_data():
    """Test fetching real data"""
    print("🧪 Testing Real Data Fetch")
    print("=" * 40)
    
    try:
        from update_real_dashboard_data import RealDataUpdater
        
        updater = RealDataUpdater()
        
        print("📊 Testing account data...")
        account_data = await updater.get_real_account_data()
        
        print(f"\n💰 REAL Account Data:")
        print(f"   Total Balance: ${account_data['total_balance']:.2f}")
        print(f"   Can Trade: {account_data['can_trade']}")
        print(f"   Account Type: {account_data['account_type']}")
        
        if account_data['balances']:
            print(f"   Balances:")
            for asset, balance in account_data['balances'].items():
                print(f"     {asset}: {balance['total']:.6f}")
        
        print(f"\n📈 Testing market data...")
        market_data = await updater.get_real_market_data()
        
        print(f"   BTC Price: ${market_data['current_price']:,.2f}")
        print(f"   RSI: {market_data['indicators'].get('rsi', 0):.1f}")
        print(f"   MACD: {market_data['indicators'].get('macd', 0):.4f}")
        
        print(f"\n🎯 Testing signals...")
        signals_data = await updater.get_real_trading_signals()
        
        print(f"   Signals Generated: {signals_data['signal_count']}")
        for signal in signals_data['signals']:
            print(f"     {signal['signal_type']}: {signal['confidence']:.2f} confidence")
        
        print(f"\n✅ Real data test completed!")
        print(f"\n💡 Your ACTUAL account balance: ${account_data['total_balance']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_data())
    if success:
        print(f"\n🎉 Ready to update dashboard with REAL data!")
        print(f"   Run: python update_real_dashboard_data.py")
    else:
        print(f"\n❌ Fix the issues above first")