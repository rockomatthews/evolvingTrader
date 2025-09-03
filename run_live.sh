#!/bin/bash

echo "🚀 Starting EvolvingTrader Live Trading..."

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    echo "Copy .env.example to .env and edit it with your real API keys."
    exit 1
fi

# Run live trading
echo "🎯 Starting live trading (REAL MONEY!)..."
echo "⚠️  WARNING: This will use real money. Make sure you've configured everything correctly."
echo "Press Ctrl+C to stop trading at any time."
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python main.py live
else
    echo "❌ Live trading cancelled."
fi

echo "✅ Live trading stopped!"