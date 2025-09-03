#!/bin/bash

echo "🔧 Fixing Pydantic Import Error"
echo "==============================="

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing pydantic-settings..."
pip install pydantic-settings==2.1.0

echo "✅ Pydantic fix complete!"
echo ""
echo "Testing import..."
python -c "from pydantic_settings import BaseSettings; print('✅ BaseSettings import working')"

echo ""
echo "🎉 You can now run: python main.py backtest"