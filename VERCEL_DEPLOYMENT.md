# 🚀 Vercel Dashboard Deployment Guide

## 📋 Files for Vercel Deployment

### Required Files:
1. `vercel.json` - Vercel configuration
2. `dashboard_vercel.py` - Main dashboard page
3. `api/stats.py` - API endpoint for trading data
4. `vercel_data.json` - Trading data (updated by sync script)

## 🚀 Deployment Steps

### 1. Prepare Your Files
```bash
# Make sure you have these files in your project root:
# - vercel.json
# - dashboard_vercel.py
# - api/stats.py
# - vercel_data.json (created by sync script)
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Or deploy from GitHub
# 1. Push your code to GitHub
# 2. Connect your repo to Vercel
# 3. Deploy automatically
```

### 3. Update Trading Data
```bash
# Run the sync script to update dashboard data
python sync_dashboard_data.py
```

## 📊 What the Dashboard Shows

### Real-Time Data:
- ✅ **Account Balance** - Your actual USDT balance
- ✅ **Trading Mode** - Live/Testnet status
- ✅ **Trading Statistics** - Trades, win rate, P&L
- ✅ **Market Data** - BTC price, RSI, MACD
- ✅ **Trading Signals** - Current buy/sell signals
- ✅ **Performance Chart** - Cumulative P&L over time

### Auto-Refresh:
- Dashboard updates every 30 seconds
- Shows real data from your trading bot
- Responsive design for mobile/desktop

## 🔄 Keeping Data Updated

### Option 1: Manual Sync
```bash
# Run this whenever you want to update the dashboard
python sync_dashboard_data.py
```

### Option 2: Automatic Sync
```bash
# Add to your trading bot to sync after each trade
from sync_dashboard_data import DashboardSyncer

syncer = DashboardSyncer()
await syncer.sync_data()
```

### Option 3: Scheduled Sync
```bash
# Set up a cron job to sync every 5 minutes
*/5 * * * * cd /path/to/your/project && python sync_dashboard_data.py
```

## 🎯 Dashboard Features

### Account Overview:
- Total balance in USDT
- Trading mode (Live/Testnet)
- Trading permissions
- Initial capital

### Trading Statistics:
- Total number of trades
- Win rate percentage
- Total profit/loss
- Profit factor

### Market Data:
- Current BTCUSDT price
- RSI indicator
- MACD indicator
- Technical analysis

### Trading Signals:
- Current buy/sell signals
- Signal confidence
- Reasoning for signals
- Entry prices

### Performance Chart:
- Cumulative P&L over time
- Trade-by-trade performance
- Visual profit/loss tracking

## 🔧 Customization

### Update API Endpoint:
Edit `api/stats.py` to change how data is fetched.

### Modify Dashboard:
Edit `dashboard_vercel.py` to change the layout or add features.

### Change Refresh Rate:
Edit the JavaScript in `dashboard_vercel.py` to change auto-refresh interval.

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ All modern browsers

## 🎉 Your Dashboard URL

After deployment, your dashboard will be available at:
```
https://your-project-name.vercel.app
```

## 🔄 Workflow

1. **Start Trading Bot**: `python main.py live`
2. **Sync Data**: `python sync_dashboard_data.py`
3. **View Dashboard**: Open your Vercel URL
4. **Monitor Performance**: Dashboard updates automatically

## 💡 Tips

- **Bookmark your dashboard URL** for easy access
- **Check dashboard regularly** to monitor performance
- **Sync data after important trades** for real-time updates
- **Use mobile dashboard** to monitor trades on the go

---

**Your live trading dashboard is ready! 🚀**