# API Setup Guide for EvolvingTrader

This guide will walk you through setting up all the required API keys and services for EvolvingTrader.

## 🔑 Required API Keys

### 1. **Binance API Keys** (for trading)

#### **For Binance.US (US Residents):**
1. Go to [binance.us](https://binance.us)
2. Create account and complete KYC verification
3. Go to **Account** → **API Management**
4. Click **Create API**
5. Enable **"Enable Trading"** permission
6. Set IP restrictions for security
7. Copy the **API Key** and **Secret Key**

```env
BINANCE_API_KEY=your_binance_us_api_key_here
BINANCE_SECRET_KEY=your_binance_us_secret_key_here
BINANCE_TESTNET=False
```

#### **For Binance.com (International):**
1. Go to [binance.com](https://binance.com)
2. Create account and complete verification
3. Go to **Account** → **API Management**
4. Create new API key with trading permissions
5. Copy the **API Key** and **Secret Key**

```env
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=False
```

### 2. **OpenAI API Key** (for LLM analysis)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)

```env
OPENAI_API_KEY=sk-your_openai_api_key_here
```

**Note:** You'll need to add payment method to your OpenAI account to use the API. GPT-5 is the latest and most advanced model.

### 3. **Pinecone API Key** (for vector database)

1. Go to [pinecone.io](https://pinecone.io)
2. Sign up for free account
3. Go to **API Keys** section
4. Copy your **API Key**

```env
PINECONE_API_KEY=your_pinecone_api_key_here
```

**Note:** No environment variable needed - Pinecone now uses a single API key.

### 4. **Neon.tech Database URL** (for PostgreSQL)

1. Go to [neon.tech](https://neon.tech)
2. Sign up for free account
3. Click **Create Project**
4. Choose a project name (e.g., "evolvingtrader")
5. Select **US East (N. Virginia)** region
6. Click **Create Project**
7. Go to **Dashboard** → **Connection Details**
8. Copy the **Connection String**

```env
NEON_DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/evolvingtrader?sslmode=require
```

**Example format:**
```
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-1.aws.neon.tech/evolvingtrader?sslmode=require
```

### 5. **Upstash Redis Keys** (for caching)

1. Go to [upstash.com](https://upstash.com)
2. Sign up for free account
3. Click **Create Database**
4. Choose **Global** region
5. Click **Create**
6. Go to **Details** tab
7. Copy the following values:

```env
REDIS_URL=redis://default:password@redis-xxx.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://redis-xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
```

**Example format:**
```
REDIS_URL=redis://default:AbC123dEf456@redis-12345.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://redis-12345.upstash.io
UPSTASH_REDIS_REST_TOKEN=AbC123dEf456GhI789JkL012MnO345PqR678StU901VwX234YzA567BcD890EfG123HiJ456KlM789NoP012QrS345TuV678WxY901ZaB234CdE567FgH890IjK123LmN456OpQ789RsT012UvW345XyZ678
```

## 📝 Complete .env File Example

Create a `.env` file in your project root with all the keys:

```env
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=True

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here

# Database Configuration (Neon.tech)
NEON_DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/evolvingtrader?sslmode=require

# Redis Configuration (Upstash Redis)
REDIS_URL=redis://default:password@redis-xxx.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://redis-xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token

# Trading Configuration
INITIAL_CAPITAL=1000
MAX_POSITION_SIZE=0.1
RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05

# Strategy Configuration
STRATEGY_UPDATE_FREQUENCY=3600
LLM_ANALYSIS_FREQUENCY=86400
PERFORMANCE_REVIEW_FREQUENCY=604800
```

## 🚀 Quick Setup Commands

```bash
# 1. Copy the example .env file
cp .env.example .env

# 2. Edit the .env file with your actual API keys
nano .env  # or use your preferred editor

# 3. Run the setup script
python setup.py

# 4. Test the configuration
python main.py backtest
```

## 💰 Cost Estimates

### **Free Tiers Available:**
- **Pinecone**: 100,000 vectors free
- **Neon.tech**: 0.5GB storage free
- **Upstash Redis**: 10,000 requests/day free
- **OpenAI**: $5 free credit for new accounts

### **Estimated Monthly Costs (for active trading):**
- **OpenAI GPT-5**: $15-75 (depending on usage - GPT-5 is more advanced and may cost more)
- **Pinecone**: $0-25 (if you exceed free tier)
- **Neon.tech**: $0-10 (if you exceed free tier)
- **Upstash Redis**: $0-5 (if you exceed free tier)

**Total estimated cost: $15-115/month** for a fully operational system with GPT-5.

## 🔒 Security Best Practices

1. **Never commit .env file to git**
2. **Use IP restrictions on API keys**
3. **Enable 2FA on all accounts**
4. **Use testnet for initial testing**
5. **Start with small amounts**
6. **Monitor API usage regularly**

## 🧪 Testing Your Setup

```bash
# Test database connection
python -c "from src.database.connection import db_manager; import asyncio; asyncio.run(db_manager.initialize())"

# Test Redis connection
python -c "from src.cache.redis_service import redis_service; import asyncio; asyncio.run(redis_service.initialize())"

# Test Pinecone connection
python -c "from src.memory.pinecone_client import PineconeMemoryClient; import asyncio; client = PineconeMemoryClient(); asyncio.run(client.initialize())"

# Test OpenAI connection
python -c "from src.llm.strategy_analyzer import StrategyAnalyzer; import asyncio; analyzer = StrategyAnalyzer(); asyncio.run(analyzer.initialize())"
```

## 🆘 Troubleshooting

### **Common Issues:**

1. **"Invalid API key"**: Check that you copied the key correctly
2. **"Connection refused"**: Check your internet connection
3. **"Rate limit exceeded"**: Wait a few minutes and try again
4. **"Database connection failed"**: Check your NEON_DATABASE_URL format
5. **"Redis connection failed"**: Check your REDIS_URL format

### **Getting Help:**
- Check the logs in `evolving_trader.log`
- Run individual component tests
- Verify API keys in respective dashboards
- Check service status pages

## 📞 Support Resources

- **Binance Support**: [help.binance.us](https://help.binance.us) or [help.binance.com](https://help.binance.com)
- **OpenAI Support**: [help.openai.com](https://help.openai.com)
- **Pinecone Support**: [docs.pinecone.io](https://docs.pinecone.io)
- **Neon Support**: [neon.tech/docs](https://neon.tech/docs)
- **Upstash Support**: [docs.upstash.com](https://docs.upstash.com)