#!/bin/bash
echo "🇺🇸 Setting up Binance.US for US Users"
echo "======================================"

echo "📋 Current configuration:"
echo "   BINANCE_API_KEY: ${BINANCE_API_KEY:0:10}..."
echo "   BINANCE_SECRET_KEY: ${BINANCE_SECRET_KEY:0:10}..."
echo "   BINANCE_TESTNET: ${BINANCE_TESTNET:-True}"

echo ""
echo "🔧 Testing Binance.US connection..."
python test_binance_us.py

echo ""
echo "📊 If connection works, test the strategy:"
echo "   python diagnose_strategy.py"

echo ""
echo "🚀 If everything works, run backtest:"
echo "   python main.py backtest"

echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "   • You're currently in TESTNET mode (safe for testing)"
echo "   • Make sure your API keys are from Binance.US (not regular Binance)"
echo "   • Test thoroughly before switching to live trading"