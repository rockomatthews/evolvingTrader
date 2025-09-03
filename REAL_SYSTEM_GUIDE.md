# Running EvolvingTrader with REAL Data (No Simulations)

## 🎯 **System Architecture**

### **Local Trading Engine** (Your Computer)
- Runs the actual trading strategy
- Connects to Binance with real API keys
- Stores all data in Neon.tech database
- Caches real-time data in Upstash Redis

### **Vercel Dashboard** (Web)
- Displays real data from your database/Redis
- No trading keys needed (secure)
- Updates every 10 seconds with real performance

## 🔑 **API Keys Required**

### **For Local Trading Engine (ALL KEYS NEEDED):**
```env
# Trading (REQUIRED for real trading)
BINANCE_API_KEY=your_real_binance_api_key
BINANCE_SECRET_KEY=your_real_binance_secret_key
BINANCE_TESTNET=False  # Set to False for real trading

# AI Analysis (REQUIRED for strategy evolution)
OPENAI_API_KEY=sk-your_real_openai_key

# Memory System (REQUIRED for learning)
PINECONE_API_KEY=your_real_pinecone_key

# Data Storage (REQUIRED for persistence)
NEON_DATABASE_URL=postgresql://your_real_neon_url
REDIS_URL=redis://your_real_redis_url
UPSTASH_REDIS_REST_URL=https://your_real_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_real_upstash_token
```

### **For Vercel Dashboard (ONLY DATA KEYS):**
```env
# Only these for Vercel (to display real data)
NEON_DATABASE_URL=postgresql://your_real_neon_url
REDIS_URL=redis://your_real_redis_url
UPSTASH_REDIS_REST_URL=https://your_real_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_real_upstash_token
```

**⚠️ NEVER put trading keys in Vercel - that would be a security risk!**

## 🚀 **Step-by-Step Setup**

### **Step 1: Setup Local Trading System**

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 2. Install requirements
pip install -r requirements.txt

# 3. Create .env file with ALL your real API keys
cp .env.example .env
nano .env  # Edit with your real keys

# 4. Run setup
python setup.py

# 5. Test with backtest first
python main.py backtest
```

### **Step 2: Start Real Trading**

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Start real trading (this will use real money!)
python main.py live
```

### **Step 3: Deploy Dashboard to Vercel**

```bash
# 1. Create a separate .env file for Vercel (NO trading keys!)
cat > .env.vercel << EOF
NEON_DATABASE_URL=postgresql://your_real_neon_url
REDIS_URL=redis://your_real_redis_url
UPSTASH_REDIS_REST_URL=https://your_real_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_real_upstash_token
EOF

# 2. Use the real data dashboard
cp dashboard_real.py dashboard_vercel.py

# 3. Deploy to Vercel
vercel --prod
```

## 💰 **Real Trading Configuration**

### **Important Settings for Real Trading:**

```env
# In your local .env file
BINANCE_TESTNET=False  # CRITICAL: Set to False for real trading
INITIAL_CAPITAL=1000   # Your starting amount
MAX_POSITION_SIZE=0.1  # 10% max per trade
RISK_PER_TRADE=0.02    # 2% risk per trade
MAX_DAILY_LOSS=0.05    # 5% max daily loss
```

### **Trading Symbols (Update for your region):**

```python
# For Binance.US (US residents)
symbols = ['BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD', 'DOTUSD']

# For Binance.com (International)
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
```

## 🔒 **Security Best Practices**

### **Local Trading System:**
1. **Keep .env file secure** - never commit to git
2. **Use IP restrictions** on Binance API keys
3. **Enable 2FA** on all accounts
4. **Start with small amounts** for testing
5. **Monitor closely** in the first few days

### **Vercel Dashboard:**
1. **Only use data keys** - no trading keys
2. **Use environment variables** in Vercel dashboard
3. **Enable HTTPS** (automatic with Vercel)
4. **Monitor access logs** regularly

## 📊 **Real Data Flow**

### **Trading Engine → Database:**
1. **Trades**: Every trade stored in Neon.tech
2. **Performance**: Real-time metrics in database
3. **Strategy Evolution**: LLM analysis results stored
4. **Market Data**: Price data and indicators stored

### **Database → Redis Cache:**
1. **Real-time Updates**: Performance metrics cached
2. **Active Positions**: Current positions cached
3. **Market Data**: Recent prices cached
4. **Session State**: Trading session state cached

### **Redis → Vercel Dashboard:**
1. **Live Updates**: Dashboard reads from Redis
2. **Real Charts**: Based on actual trade data
3. **Performance Metrics**: Real P&L and statistics
4. **Position Tracking**: Live position updates

## 🎯 **Testing Before Going Live**

### **Step 1: Paper Trading**
```bash
# Test with paper trading first
BINANCE_TESTNET=True python main.py live
```

### **Step 2: Small Amount**
```bash
# Start with small amount
INITIAL_CAPITAL=100 python main.py live
```

### **Step 3: Monitor Performance**
- Watch the dashboard for 24-48 hours
- Check that trades are being recorded
- Verify performance metrics are accurate
- Ensure risk management is working

## 🚨 **Important Warnings**

### **Real Money Trading:**
- ⚠️ **You can lose money** - only trade what you can afford to lose
- ⚠️ **Start small** - test with $100-500 first
- ⚠️ **Monitor closely** - check performance daily
- ⚠️ **Set stop losses** - the system has built-in risk management
- ⚠️ **Keep backups** - export your data regularly

### **API Key Security:**
- 🔒 **Never share API keys** - keep them private
- 🔒 **Use IP restrictions** - limit API access to your IP
- 🔒 **Monitor usage** - check for unauthorized access
- 🔒 **Rotate keys** - change them periodically

## 📈 **Expected Performance**

### **Realistic Expectations:**
- **Win Rate**: 60-70% (good for crypto trading)
- **Daily Returns**: 1-5% (highly variable)
- **Drawdowns**: 5-15% (normal for active trading)
- **Sharpe Ratio**: 1.0-2.0 (good risk-adjusted returns)

### **Risk Management:**
- **Position Sizing**: Automatic based on confidence
- **Stop Losses**: Built-in risk controls
- **Daily Limits**: Maximum loss protection
- **Portfolio Limits**: Diversification controls

## 🆘 **Troubleshooting**

### **Common Issues:**
1. **"Invalid API key"**: Check Binance API permissions
2. **"Insufficient balance"**: Add more funds to account
3. **"Rate limit exceeded"**: Wait and retry
4. **"Database connection failed"**: Check Neon.tech URL
5. **"Redis connection failed"**: Check Upstash credentials

### **Emergency Stop:**
```bash
# Stop trading immediately
pkill -f "python main.py live"

# Or press Ctrl+C in the terminal
```

## 📞 **Support**

- **Binance Support**: [help.binance.us](https://help.binance.us)
- **System Logs**: Check `evolving_trader.log`
- **Database Issues**: Check Neon.tech dashboard
- **Redis Issues**: Check Upstash dashboard

Remember: **This is real money trading. Start small, test thoroughly, and never risk more than you can afford to lose!**