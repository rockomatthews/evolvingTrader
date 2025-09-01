# Binance.US Trading Guide for EvolvingTrader

## 💰 Currency Requirements for Binance.US

### **Minimum Deposit Requirements:**

#### **USD Deposits:**
- **Minimum**: $10 USD
- **Recommended for Trading**: $100+ USD
- **For EvolvingTrader**: $1,000+ USD (as configured)

#### **Cryptocurrency Deposits:**
- **Bitcoin (BTC)**: 0.0001 BTC minimum
- **Ethereum (ETH)**: 0.001 ETH minimum
- **USDT**: 10 USDT minimum
- **Other cryptos**: Varies by coin

### **Trading Pairs Available:**
- **BTC/USD**: Bitcoin to US Dollar
- **ETH/USD**: Ethereum to US Dollar
- **ADA/USD**: Cardano to US Dollar
- **SOL/USD**: Solana to US Dollar
- **DOT/USD**: Polkadot to US Dollar
- **USDT/USD**: Tether to US Dollar

## 🏦 Account Setup Process

### **Step 1: Create Binance.US Account**
1. Go to [binance.us](https://binance.us)
2. Click "Register"
3. Enter email and password
4. Verify email address
5. Complete identity verification (KYC)

### **Step 2: Identity Verification (KYC)**
**Required Documents:**
- Government-issued ID (Driver's License, Passport)
- Social Security Number
- Proof of address (utility bill, bank statement)

**Verification Levels:**
- **Basic**: $5,000 daily withdrawal limit
- **Intermediate**: $50,000 daily withdrawal limit
- **Advanced**: $500,000 daily withdrawal limit

### **Step 3: Enable API Trading**
1. Go to Account → API Management
2. Create new API key
3. Enable "Enable Trading" permission
4. **Important**: Enable "Enable Futures" if trading futures
5. Set IP restrictions for security
6. Save API key and secret

## 💳 Funding Your Account

### **Bank Transfer (ACH)**
- **Processing Time**: 1-3 business days
- **Fees**: Free
- **Minimum**: $10
- **Maximum**: $50,000 per day

### **Wire Transfer**
- **Processing Time**: 1-2 business days
- **Fees**: $15-25
- **Minimum**: $100
- **Maximum**: $500,000 per day

### **Cryptocurrency Deposit**
- **Processing Time**: 10-30 minutes
- **Fees**: Network fees only
- **Minimum**: Varies by coin
- **Maximum**: No limit

## 🔧 EvolvingTrader Configuration

### **Update Configuration for Binance.US:**

```python
# In your .env file
BINANCE_API_KEY=your_binance_us_api_key
BINANCE_SECRET_KEY=your_binance_us_secret_key
BINANCE_TESTNET=False  # Set to False for live trading

# Trading symbols for Binance.US
TRADING_SYMBOLS=BTCUSD,ETHUSD,ADAUSD,SOLUSD,DOTUSD
```

### **Supported Trading Pairs:**
```python
# Update symbols in main.py or config.py
symbols = [
    'BTCUSD',    # Bitcoin/USD
    'ETHUSD',    # Ethereum/USD
    'ADAUSD',    # Cardano/USD
    'SOLUSD',    # Solana/USD
    'DOTUSD',    # Polkadot/USD
    'LINKUSD',   # Chainlink/USD
    'UNIUSD',    # Uniswap/USD
    'AAVEUSD',   # Aave/USD
]
```

## ⚠️ Important Considerations

### **Trading Limits:**
- **Daily Trading Limit**: Based on verification level
- **Minimum Order Size**: $10 USD equivalent
- **Maximum Order Size**: Based on account balance
- **Rate Limits**: 1200 requests per minute

### **Fees:**
- **Spot Trading**: 0.1% (0.075% with BNB discount)
- **Futures Trading**: 0.02% maker, 0.04% taker
- **Withdrawal Fees**: Varies by cryptocurrency

### **Security Best Practices:**
1. **Enable 2FA**: Use Google Authenticator or SMS
2. **IP Restrictions**: Limit API access to your IP
3. **Withdrawal Whitelist**: Pre-approve withdrawal addresses
4. **Regular Monitoring**: Check account activity regularly

## 🚀 Getting Started with EvolvingTrader

### **Recommended Starting Amount:**
- **Minimum**: $1,000 USD
- **Recommended**: $5,000+ USD
- **For Serious Trading**: $10,000+ USD

### **Risk Management:**
- **Position Size**: Start with 1-2% of account per trade
- **Stop Loss**: Always use stop losses
- **Diversification**: Don't put all funds in one trade
- **Monitoring**: Check performance regularly

### **Testing Strategy:**
1. **Start with Paper Trading**: Test strategy without real money
2. **Small Amount**: Start with minimum viable amount
3. **Gradual Increase**: Increase position sizes as you gain confidence
4. **Monitor Performance**: Track results and adjust strategy

## 📊 Tax Considerations

### **Tax Reporting:**
- **Form 8949**: Report all cryptocurrency transactions
- **Capital Gains**: Short-term (<1 year) vs Long-term (>1 year)
- **Record Keeping**: Maintain detailed transaction records
- **Software**: Consider using tax software like CoinTracker or Koinly

### **Record Keeping:**
- **Transaction History**: Download from Binance.US
- **Trade Logs**: EvolvingTrader automatically logs all trades
- **Performance Reports**: Regular performance summaries
- **API Logs**: Keep records of all API calls

## 🔄 Migration from Binance.com

### **If Coming from Binance.com:**
1. **Account Transfer**: Cannot transfer directly
2. **Manual Migration**: Sell on Binance.com, buy on Binance.US
3. **Tax Implications**: Each transaction is a taxable event
4. **API Keys**: Create new API keys for Binance.US

## 📞 Support and Resources

### **Binance.US Support:**
- **Help Center**: [help.binance.us](https://help.binance.us)
- **Live Chat**: Available 24/7
- **Email Support**: support@binance.us
- **Status Page**: [status.binance.us](https://status.binance.us)

### **EvolvingTrader Support:**
- **Documentation**: Check README.md
- **Issues**: Create GitHub issues
- **Community**: Join trading communities
- **Updates**: Follow project updates

## 🎯 Success Tips

### **For Best Results:**
1. **Start Small**: Begin with minimum viable amount
2. **Monitor Closely**: Watch performance in first few weeks
3. **Adjust Strategy**: Modify parameters based on results
4. **Keep Records**: Maintain detailed performance logs
5. **Stay Informed**: Keep up with market news and updates

### **Common Mistakes to Avoid:**
- **Overtrading**: Don't trade too frequently
- **Emotional Trading**: Stick to the strategy
- **Ignoring Risk**: Always use proper risk management
- **Not Monitoring**: Check performance regularly
- **Chasing Losses**: Don't increase position sizes after losses

Remember: **Trading cryptocurrencies involves substantial risk of loss. Only invest what you can afford to lose.**