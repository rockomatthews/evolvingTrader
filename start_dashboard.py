#!/usr/bin/env python3
"""
Start the real-time trading dashboard
"""
import asyncio
import subprocess
import sys
import os
import time
import threading
import requests
from datetime import datetime

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server in a separate process"""
    print("🚀 Starting API server...")
    try:
        # Start API server
        api_process = subprocess.Popen([
            sys.executable, "src/api/server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for API server to start
        print("⏳ Waiting for API server to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_api_server():
                print("✅ API server is running!")
                return api_process
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ API server failed to start")
        api_process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_dashboard():
    """Start the dashboard"""
    print("🚀 Starting dashboard...")
    try:
        # Start dashboard
        dashboard_process = subprocess.Popen([
            sys.executable, "dashboard_real_time.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Dashboard is starting...")
        print("🌐 Dashboard will be available at: http://127.0.0.1:8050")
        return dashboard_process
        
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def main():
    """Main function"""
    print("🚀 EvolvingTrader - Real-Time Dashboard")
    print("=" * 50)
    
    # Check if trading bot is running
    print("🔍 Checking if trading bot is running...")
    try:
        # Try to import trading engine to check if it's available
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.trading_engine import EvolvingTraderEngine
        print("✅ Trading engine is available")
    except Exception as e:
        print(f"⚠️  Trading engine not available: {e}")
        print("   Make sure you've run the trading bot at least once")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot start dashboard without API server")
        return
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        print("❌ Failed to start dashboard")
        api_process.terminate()
        return
    
    print("\n🎉 Dashboard is running!")
    print("=" * 50)
    print("📊 Dashboard URL: http://127.0.0.1:8050")
    print("🔌 API URL: http://127.0.0.1:8000")
    print("=" * 50)
    print("\n📋 What you'll see:")
    print("   • Real account balance and trading status")
    print("   • Live BTCUSDT price and technical indicators")
    print("   • Current trading signals")
    print("   • Trading statistics (trades, win rate, P&L)")
    print("   • Performance charts")
    print("   • Price history charts")
    print("\n⚠️  To stop the dashboard:")
    print("   Press Ctrl+C")
    print("\n🔄 The dashboard updates every 5 seconds automatically")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped")
                break
            
            if dashboard_process.poll() is not None:
                print("❌ Dashboard stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
        
        # Terminate processes
        if api_process:
            api_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()
        
        print("✅ Dashboard stopped")

if __name__ == "__main__":
    main()