#!/bin/bash

# EvolvingTrader Virtual Environment Activation Script

echo "🚀 Activating EvolvingTrader Virtual Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python setup.py' first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo ""
echo "You can now run:"
echo "  python main.py backtest    # Run backtest"
echo "  python main.py live        # Run live trading"
echo "  python main.py dashboard   # Run dashboard"
echo ""
echo "To deactivate, run: deactivate"
echo ""

# Keep the shell active
exec bash