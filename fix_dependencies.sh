#!/bin/bash

echo "🔧 Fixing Dependency Conflicts"
echo "=============================="

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing core packages first..."

# Install core packages one by one to avoid conflicts
pip install --upgrade pip
pip install python-dotenv
pip install pydantic
pip install httpx
pip install loguru

echo "📊 Installing data packages..."
pip install "pandas>=2.1.3,<2.3.0"
pip install "numpy>=1.24.3,<1.26.0"
pip install ta

echo "🔗 Installing database packages..."
pip install sqlalchemy
pip install alembic
pip install psycopg2-binary
pip install neon-connector

echo "🌐 Installing API packages..."
pip install python-binance
pip install openai
pip install pinecone-client

echo "💾 Installing cache packages..."
pip install redis
pip install upstash-redis

echo "📈 Installing dashboard packages..."
pip install dash
pip install dash-bootstrap-components
pip install plotly

echo "🧠 Installing AI packages (optional)..."
pip install scikit-learn || echo "⚠️  scikit-learn failed, skipping..."

echo "✅ Core packages installed!"
echo ""
echo "Testing installation..."
python -c "import pandas, numpy, ta; print('✅ Data packages working')"
python -c "import sqlalchemy, redis; print('✅ Database packages working')"
python -c "import dash, plotly; print('✅ Dashboard packages working')"
python -c "import openai, pinecone; print('✅ AI packages working')"

echo ""
echo "🎉 Dependency resolution complete!"
echo "You can now run: python main.py backtest"