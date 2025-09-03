#!/bin/bash
echo "🔧 Fixing All Dependencies for EvolvingTrader"
echo "============================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing core dependencies..."
pip install scikit-learn==1.3.2
pip install pydantic-settings==2.1.0

echo "📦 Installing minimal requirements..."
pip install -r requirements-minimal.txt

echo "✅ Testing configuration..."
python -c "
try:
    from config import trading_config, binance_config, openai_config
    print('✅ Configuration loaded successfully!')
    print(f'✅ Trading config: Initial capital = ${trading_config.initial_capital}')
    print(f'✅ Binance testnet: {binance_config.testnet}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

echo "✅ Testing sklearn import..."
python -c "
try:
    from sklearn.preprocessing import StandardScaler
    print('✅ scikit-learn import successful!')
except ImportError as e:
    print(f'❌ scikit-learn import failed: {e}')
"

echo "✅ Testing market analyzer..."
python -c "
try:
    from src.analysis.market_analyzer import MarketAnalyzer
    print('✅ Market analyzer import successful!')
except Exception as e:
    print(f'❌ Market analyzer error: {e}')
"

echo ""
echo "🚀 Dependencies fixed! Now try:"
echo "   python run_backtest_simple.py"
echo "   or"
echo "   python main.py backtest"