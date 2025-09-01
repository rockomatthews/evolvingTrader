# EvolvingTrader Dashboard Deployment Guide

## 🚀 Deploy Dashboard to Vercel

### Step 1: Prepare for Deployment

1. **Install Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Navigate to your project directory
cd /Users/home/evolved/evolvingTrader

# Deploy to Vercel
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name: evolvingtrader-dashboard
# - Directory: ./
# - Override settings? No
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure build settings:
   - **Framework Preset**: Other
   - **Build Command**: `echo "No build required"`
   - **Output Directory**: `.`
   - **Install Command**: `pip install -r requirements-vercel.txt`

### Step 3: Configure Environment Variables

In your Vercel dashboard, go to Settings → Environment Variables and add:

```env
# Database (for production data)
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/evolvingtrader?sslmode=require

# Redis (for real-time data)
REDIS_URL=redis://default:password@redis-xxx.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://redis-xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token

# Optional: API keys for live data (if you want real-time updates)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### Step 4: Deploy

```bash
# Deploy to production
vercel --prod
```

Your dashboard will be available at: `https://your-project-name.vercel.app`

## 🔧 Custom Domain (Optional)

1. In Vercel dashboard, go to Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Your dashboard will be available at your custom domain

## 📊 Dashboard Features

### Real-time Updates
- **Performance Metrics**: Live P&L, win rate, trade count
- **Active Positions**: Current open positions
- **Strategy Parameters**: Current strategy configuration
- **Memory Statistics**: Pinecone database usage

### Charts and Visualizations
- **Cumulative P&L Chart**: Shows performance over time
- **Win Rate Chart**: Rolling win rate analysis
- **P&L Distribution**: Histogram of trade outcomes

### Professional Design
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Updates**: Data refreshes every 5 seconds
- **Professional Styling**: Clean, investor-ready interface

## 🔄 Updating the Dashboard

To update your deployed dashboard:

```bash
# Make changes to your code
# Then redeploy
vercel --prod
```

## 🐛 Troubleshooting

### Common Issues:

1. **Build Errors**: Check that all dependencies are in `requirements-vercel.txt`
2. **Environment Variables**: Ensure all required env vars are set in Vercel
3. **Timeout Issues**: Vercel has a 30-second timeout limit
4. **Memory Issues**: Large datasets might cause memory issues

### Debug Mode:
```bash
# Deploy with debug info
vercel --debug
```

## 📱 Mobile Responsiveness

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🔒 Security

- Environment variables are encrypted in Vercel
- No sensitive data is exposed in the frontend
- API keys are server-side only
- HTTPS is enabled by default

## 📈 Performance

- **Fast Loading**: Optimized for quick page loads
- **Real-time Updates**: 5-second refresh intervals
- **Global CDN**: Vercel's global edge network
- **Auto-scaling**: Handles traffic spikes automatically