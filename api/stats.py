"""
Vercel API endpoint for trading statistics
"""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

def get_trading_stats():
    """Get trading statistics from local files"""
    try:
        # Try to read from local files (if available)
        stats = {
            'account': {
                'total_balance': 0.0,  # Will be updated with real data
                'can_trade': True,
                'account_type': 'SPOT',
                'last_updated': datetime.now().isoformat()
            },
            'market': {
                'current_price': 111495.08,  # Current BTC price
                'indicators': {
                    'rsi': 45.2,
                    'macd': 0.0012,
                    'macd_signal': 0.0008
                },
                'last_updated': datetime.now().isoformat()
            },
            'signals': {
                'signals': [],
                'signal_count': 0,
                'last_updated': datetime.now().isoformat()
            },
            'trades': {
                'trades': [],
                'statistics': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'max_drawdown': 0,
                    'max_drawdown_pct': 0
                },
                'last_updated': datetime.now().isoformat()
            },
            'config': {
                'initial_capital': 0.0,  # Will be updated with real data
                'current_capital': 0.0,  # Will be updated with real data
                'max_position_size': 0.05,
                'risk_per_trade': 0.01,
                'testnet': False
            },
            'last_updated': datetime.now().isoformat()
        }
        
        # Try to read real data from files if they exist
        try:
            # First try to read from the real data file
            if os.path.exists('vercel_data.json'):
                with open('vercel_data.json', 'r') as f:
                    real_data = json.load(f)
                    stats = real_data  # Use real data
                    print(f"Loaded real data: Balance=${stats['account']['total_balance']:.2f}")
            elif os.path.exists('api/stats_data.json'):
                with open('api/stats_data.json', 'r') as f:
                    real_data = json.load(f)
                    stats = real_data  # Use real data
                    print(f"Loaded real data: Balance=${stats['account']['total_balance']:.2f}")
            elif os.path.exists('trades_history.json'):
                with open('trades_history.json', 'r') as f:
                    trades_data = json.load(f)
                    stats['trades'] = trades_data
        except Exception as e:
            print(f"Error loading real data: {e}")
            pass
        
        return stats
        
    except Exception as e:
        return {
            'error': str(e),
            'last_updated': datetime.now().isoformat()
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        stats = get_trading_stats()
        self.wfile.write(json.dumps(stats).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()