"""
FastAPI server for real-time trading dashboard
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from src.api.trading_stats import trading_stats_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="EvolvingTrader API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "EvolvingTrader API", "status": "running", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats")
async def get_all_stats():
    """Get all trading statistics"""
    try:
        stats = await trading_stats_api.get_all_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account")
async def get_account_stats():
    """Get account statistics"""
    try:
        stats = await trading_stats_api.get_account_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting account stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market")
async def get_market_data():
    """Get market data"""
    try:
        data = await trading_stats_api.get_market_data()
        return data
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals")
async def get_trading_signals():
    """Get trading signals"""
    try:
        signals = await trading_stats_api.get_trading_signals()
        return signals
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def get_trades_history():
    """Get trades history"""
    try:
        trades = trading_stats_api.get_trades_history()
        return trades
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance")
async def get_performance_history():
    """Get performance history"""
    try:
        performance = trading_stats_api.get_performance_history()
        return performance
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def run_api_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the API server"""
    logger.info(f"Starting EvolvingTrader API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_api_server()