"""
Safe trading configuration for when testnet is not available
"""
from config import trading_config

class SafeTradingConfig:
    """Safe trading configuration that limits risk when using live trading"""
    
    def __init__(self):
        self.is_safe_mode = True  # Always use safe mode when testnet fails
        
    @property
    def initial_capital(self) -> float:
        """Very small initial capital for safety"""
        return min(trading_config.initial_capital, 10.0)  # Max $10
    
    @property
    def max_position_size(self) -> float:
        """Very small position size for safety"""
        return min(trading_config.max_position_size, 0.01)  # Max 1%
    
    @property
    def risk_per_trade(self) -> float:
        """Very small risk per trade for safety"""
        return min(trading_config.risk_per_trade, 0.005)  # Max 0.5%
    
    @property
    def max_daily_loss(self) -> float:
        """Very small daily loss limit for safety"""
        return min(trading_config.max_daily_loss, 0.01)  # Max 1%
    
    @property
    def min_trade_amount(self) -> float:
        """Minimum trade amount to avoid dust"""
        return 2.0  # $2 minimum for $10 account
    
    @property
    def max_trade_amount(self) -> float:
        """Maximum trade amount for safety"""
        return 5.0  # $5 maximum for $10 account
    
    def get_safe_position_size(self, account_balance: float) -> float:
        """Calculate safe position size based on account balance"""
        # Use the smaller of: max position size or max trade amount
        max_by_percentage = account_balance * self.max_position_size
        max_by_amount = self.max_trade_amount
        
        return min(max_by_percentage, max_by_amount, account_balance * 0.1)  # Never more than 10% of balance

# Global safe trading config
safe_trading_config = SafeTradingConfig()