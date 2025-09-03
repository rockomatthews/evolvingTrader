#!/bin/bash

echo "🚀 Complete EvolvingTrader Setup"
echo "================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
echo "Trying full requirements first..."
pip install -r requirements.txt || {
    echo "⚠️  Full requirements failed, trying minimal requirements..."
    pip install -r requirements-minimal.txt
}

# Create directories
echo "📁 Creating directories..."
mkdir -p logs data results backtests

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your API keys: nano .env"
echo "3. Run backtest: python main.py backtest"
echo "4. Run live trading: python main.py live"
echo ""
echo "Or use the run scripts:"
echo "- ./run_backtest.sh"
echo "- ./run_live.sh"
echo "- ./run_dashboard.sh"