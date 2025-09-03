#!/bin/bash
echo "🇺🇸 Complete Binance.US Fix for US Users"
echo "========================================"

echo "📋 Step 1: Check Configuration"
echo "------------------------------"
python check_config.py

echo ""
echo "📋 Step 2: Test Connection Methods"
echo "----------------------------------"
python test_connection_simple.py

echo ""
echo "📋 Step 3: Test Strategy"
echo "------------------------"
python diagnose_strategy.py

echo ""
echo "📋 Step 4: Run Backtest"
echo "-----------------------"
python main.py backtest

echo ""
echo "🎯 Summary:"
echo "==========="
echo "If all steps pass, your system is ready!"
echo ""
echo "⚠️  Important Notes:"
echo "• Make sure your API keys are from Binance.US (not regular Binance)"
echo "• You're currently in TESTNET mode (safe for testing)"
echo "• Test thoroughly before switching to live trading"
echo ""
echo "🚀 Next Steps:"
echo "• If tests pass: python prepare_live_trading.py"
echo "• For live trading: Edit config.py to set testnet=False"
echo "• Start live trading: python main.py live"