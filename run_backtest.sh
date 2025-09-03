#!/bin/bash

echo "🚀 Starting EvolvingTrader Backtest..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python setup.py' first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if packages are installed
echo "🔍 Checking if packages are installed..."
python -c "import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Packages not installed. Installing requirements..."
    pip install -r requirements.txt
fi

# Run backtest
echo "🎯 Running backtest..."
python main.py backtest

echo "✅ Backtest completed!"