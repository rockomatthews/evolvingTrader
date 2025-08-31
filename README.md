# EvolvingTrader - AI-Powered Trading Strategy

EvolvingTrader is a sophisticated AI-powered trading system that uses Large Language Models (LLMs) to continuously evolve and adapt its trading strategy based on market conditions and performance feedback. The system combines multiple trading approaches with advanced risk management and real-time market analysis.

## 🚀 Key Features

### Core Strategy
- **Multi-Strategy Approach**: Combines momentum, mean reversion, trend-following, and volume-based strategies
- **Dynamic Parameter Evolution**: Strategy parameters automatically adjust based on performance
- **Real-time Market Analysis**: Advanced pattern recognition and regime detection
- **LLM-Powered Evolution**: Uses GPT-4 to analyze performance and suggest improvements

### Risk Management
- **Advanced Risk Assessment**: Multi-layered risk evaluation for each trade
- **Dynamic Position Sizing**: Position sizes adjust based on confidence and risk
- **Portfolio Protection**: Comprehensive portfolio-level risk monitoring
- **Drawdown Control**: Automatic risk reduction during adverse conditions

### Memory & Learning
- **Pinecone Vector Database**: Long-term memory storage for patterns and performance
- **Pattern Recognition**: Learns from successful and failed trading patterns
- **Strategy Evolution**: Continuous improvement based on historical performance
- **Market Regime Adaptation**: Adjusts strategy based on market conditions

### Technology Stack
- **Binance API Integration**: Real-time trading and market data
- **OpenAI GPT-4**: Strategy analysis and evolution
- **Pinecone**: Vector database for long-term memory
- **Neon.tech PostgreSQL**: Persistent data storage for trades, performance, and logs
- **Upstash Redis**: High-performance caching and real-time data streaming
- **Real-time Dashboard**: Live performance monitoring with WebSocket updates
- **Comprehensive Backtesting**: Strategy validation and optimization

## 🚀 What is Redis Used For?

Redis serves as a **high-performance caching layer** and **real-time data streaming service**:

### **Real-time Data Caching:**
- **Market Data**: Current prices, 24hr statistics, technical indicators
- **Performance Metrics**: Live P&L, win rates, position counts
- **Risk Metrics**: Real-time risk scores, exposure levels
- **Trading Signals**: Generated signals with confidence scores

### **Session State Management:**
- **Active Positions**: Current open positions and their details
- **Trading Session State**: Current balance, session status
- **Strategy Parameters**: Current strategy configuration
- **WebSocket Connections**: Real-time dashboard connections

### **Performance Optimization:**
- **API Rate Limiting**: Prevents hitting Binance API limits
- **Data Preprocessing**: Cached technical indicators and calculations
- **Fast Lookups**: Sub-millisecond access to frequently used data
- **Real-time Updates**: Instant data propagation to dashboard

### **Real-time Streaming:**
- **WebSocket Server**: Streams live data to dashboard clients
- **Pub/Sub Messaging**: Real-time communication between components
- **Live Market Data**: 5-second price updates for all symbols
- **Performance Broadcasting**: Live performance metrics to investors

## 📊 Performance Goals

Starting with $1,000, the system aims to:
- Achieve consistent positive returns through volatile market conditions
- Demonstrate strong risk-adjusted performance (Sharpe ratio > 1.5)
- Maintain maximum drawdown below 15%
- Show clear evidence of strategy evolution and learning

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd evolvingTrader
   ```

2. **Run setup script**
   ```bash
   python setup.py
   ```

3. **Configure API keys and database**
   Edit the `.env` file with your API keys:
   ```env
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET_KEY=your_binance_secret_key
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/evolvingtrader?sslmode=require
   REDIS_URL=redis://default:password@redis-xxx.upstash.io:6379
   UPSTASH_REDIS_REST_URL=https://redis-xxx.upstash.io
   UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
   ```
   
   **Database Setup (Neon.tech):**
   1. Go to [neon.tech](https://neon.tech)
   2. Create a new project
   3. Copy the connection string to `DATABASE_URL` in your `.env` file
   4. The system will automatically create all necessary tables
   
   **Redis Setup (Upstash):**
   1. Go to [upstash.com](https://upstash.com)
   2. Create a new Redis database
   3. Copy the connection details to `REDIS_URL`, `UPSTASH_REDIS_REST_URL`, and `UPSTASH_REDIS_REST_TOKEN` in your `.env` file

## 🚀 Usage

### Backtesting
Test the strategy on historical data:
```bash
python main.py backtest
```

### Parameter Optimization
Optimize strategy parameters:
```bash
python main.py optimize
```

### Live Trading
Run the live trading system:
```bash
python main.py live
```

### Dashboard
Launch the real-time dashboard:
```bash
python main.py dashboard
```

## 📈 Strategy Architecture

### Multi-Strategy Framework
The system combines four core strategies:

1. **Momentum Strategy**
   - RSI-based momentum signals
   - MACD trend confirmation
   - Price momentum analysis

2. **Mean Reversion Strategy**
   - Bollinger Bands positioning
   - Volatility-based entries
   - Support/resistance levels

3. **Trend Following Strategy**
   - EMA crossovers
   - ADX trend strength
   - Price action confirmation

4. **Volume Strategy**
   - Volume profile analysis
   - On-Balance Volume (OBV)
   - Volume breakouts

### LLM Integration
- **Performance Analysis**: GPT-4 analyzes trading performance and identifies improvement areas
- **Parameter Optimization**: Suggests parameter adjustments based on market conditions
- **Risk Assessment**: Evaluates risk levels and provides recommendations
- **Strategy Evolution**: Proposes new strategy combinations and approaches

### Memory System
- **Pattern Storage**: Stores successful and failed trading patterns in Pinecone
- **Performance Tracking**: Maintains detailed performance history
- **Strategy Parameters**: Remembers effective parameter combinations
- **Market Regimes**: Learns to identify and adapt to different market conditions

## 🔧 Configuration

### Trading Parameters
```python
# Risk Management
INITIAL_CAPITAL = 1000
MAX_POSITION_SIZE = 0.1  # 10% of portfolio
RISK_PER_TRADE = 0.02    # 2% risk per trade
MAX_DAILY_LOSS = 0.05    # 5% maximum daily loss

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2.0
```

### Evolution Settings
```python
# Strategy Evolution
STRATEGY_UPDATE_FREQUENCY = 3600      # 1 hour
LLM_ANALYSIS_FREQUENCY = 86400        # 24 hours
PERFORMANCE_REVIEW_FREQUENCY = 604800 # 7 days
```

## 📊 Dashboard Features

The real-time dashboard provides:
- **Live Performance Metrics**: Current balance, total return, win rate
- **Active Positions**: Real-time position monitoring
- **Strategy Parameters**: Current strategy configuration
- **Risk Metrics**: Portfolio risk assessment
- **Memory Statistics**: Pinecone database usage
- **Performance Charts**: Equity curve, win rate, P&L distribution

## 🧪 Backtesting

The backtesting framework includes:
- **Historical Data Simulation**: Realistic market data simulation
- **Strategy Validation**: Test strategy performance on historical data
- **Parameter Optimization**: Find optimal parameter combinations
- **Performance Metrics**: Comprehensive performance analysis
- **Risk Assessment**: Historical risk evaluation

## 🔒 Risk Management

### Multi-Layer Risk Assessment
1. **Individual Trade Risk**: Position size and stop-loss evaluation
2. **Portfolio Risk**: Overall exposure and correlation analysis
3. **Market Risk**: Volatility and regime-based adjustments
4. **Liquidity Risk**: Market depth and execution risk

### Dynamic Risk Controls
- **Position Sizing**: Adjusts based on confidence and market conditions
- **Stop Losses**: Dynamic stop-loss levels based on volatility
- **Portfolio Limits**: Maximum exposure and concentration limits
- **Drawdown Protection**: Automatic risk reduction during losses

## 🎯 Long-term Vision

### For Investors
- **Demonstrable Performance**: Clear evidence of consistent returns
- **Risk Management**: Professional-grade risk controls
- **Transparency**: Full visibility into strategy and performance
- **Scalability**: System designed to handle larger capital

### Strategy Evolution
- **Continuous Learning**: System improves over time
- **Market Adaptation**: Adjusts to changing market conditions
- **Pattern Recognition**: Learns from successful strategies
- **Risk Optimization**: Continuously improves risk management

## 📝 Monitoring & Reporting

### Real-time Monitoring
- Live performance tracking
- Risk metric monitoring
- Strategy parameter changes
- Market condition analysis

### Performance Reporting
- Daily performance summaries
- Weekly strategy evolution reports
- Monthly risk assessments
- Quarterly performance reviews

## 🤝 Contributing

This system is designed to demonstrate AI-powered trading capabilities. Key areas for enhancement:
- Additional trading strategies
- Enhanced pattern recognition
- Improved risk models
- Extended market coverage

## ⚠️ Disclaimer

This is a demonstration system for educational and research purposes. Trading cryptocurrencies involves substantial risk of loss. Past performance does not guarantee future results. Always conduct thorough testing and risk assessment before deploying capital.

## 📞 Support

For questions or support regarding the EvolvingTrader system, please refer to the documentation or create an issue in the repository.

---

**EvolvingTrader** - Where AI meets trading, and strategy evolves with the market.