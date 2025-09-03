#!/bin/bash
echo "🔧 Fixing scikit-learn Import Error"
echo "=================================="

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing scikit-learn..."
pip install scikit-learn==1.3.2

echo "✅ Testing import..."
python -c "from sklearn.preprocessing import StandardScaler; print('✅ scikit-learn import successful!')"

echo "✅ scikit-learn fix complete!"
echo ""
echo "🚀 Now try running:"
echo "   python main.py backtest"