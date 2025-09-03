"""
Trade logging utility for dashboard
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TradeLogger:
    """Log trades for dashboard display"""
    
    def __init__(self, trades_file: str = 'trades_history.json'):
        self.trades_file = trades_file
        self.performance_file = 'performance_history.json'
        
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Load existing trades
            trades = self.load_trades()
            
            # Add new trade
            trades.append(trade_data)
            
            # Save trades
            self.save_trades(trades)
            
            # Update performance history
            self.update_performance_history(trades)
            
            logger.info(f"Logged trade: {trade_data.get('symbol', 'Unknown')} {trade_data.get('side', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to log trade: {e}")
    
    def load_trades(self) -> List[Dict[str, Any]]:
        """Load trades from file"""
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    data = json.load(f)
                    return data.get('trades', [])
            return []
        except Exception as e:
            logger.error(f"Failed to load trades: {e}")
            return []
    
    def save_trades(self, trades: List[Dict[str, Any]]):
        """Save trades to file"""
        try:
            data = {
                'trades': trades,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.trades_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save trades: {e}")
    
    def update_performance_history(self, trades: List[Dict[str, Any]]):
        """Update performance history for charts"""
        try:
            if not trades:
                return
            
            # Calculate cumulative P&L
            cumulative_pnl = 0
            performance_data = []
            
            for i, trade in enumerate(trades):
                pnl = trade.get('pnl', 0)
                cumulative_pnl += pnl
                
                performance_data.append({
                    'timestamp': trade.get('timestamp', datetime.now().isoformat()),
                    'trade_number': i + 1,
                    'pnl': pnl,
                    'cumulative_pnl': cumulative_pnl,
                    'symbol': trade.get('symbol', 'Unknown'),
                    'side': trade.get('side', 'Unknown')
                })
            
            # Save performance data
            data = {
                'performance': performance_data,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update performance history: {e}")
    
    def create_sample_trade(self, symbol: str = "BTCUSDT", side: str = "BUY", 
                          entry_price: float = 50000.0, quantity: float = 0.001,
                          exit_price: float = None, pnl: float = None) -> Dict[str, Any]:
        """Create a sample trade for testing"""
        
        if exit_price is None:
            # Simulate a random exit price
            import random
            if side == "BUY":
                exit_price = entry_price * (1 + random.uniform(-0.02, 0.05))  # -2% to +5%
            else:
                exit_price = entry_price * (1 + random.uniform(-0.05, 0.02))  # -5% to +2%
        
        if pnl is None:
            # Calculate P&L
            if side == "BUY":
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
        
        return {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': pnl,
            'timestamp': datetime.now().isoformat(),
            'trade_id': f"{symbol}_{side}_{int(datetime.now().timestamp())}"
        }

# Global instance
trade_logger = TradeLogger()