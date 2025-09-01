"""
Database models for EvolvingTrader using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class TradingSession(Base):
    """Trading session tracking"""
    __tablename__ = 'trading_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=True)
    status = Column(String, default='active')  # active, stopped, error
    symbols = Column(JSON)  # List of trading symbols
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="session")
    performance_snapshots = relationship("PerformanceSnapshot", back_populates="session")
    strategy_evolutions = relationship("StrategyEvolution", back_populates="session")

class Trade(Base):
    """Individual trade records"""
    __tablename__ = 'trades'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('trading_sessions.id'), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    exit_reason = Column(String, nullable=True)  # stop_loss, take_profit, signal, manual
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("TradingSession", back_populates="trades")

class PerformanceSnapshot(Base):
    """Performance snapshots for tracking"""
    __tablename__ = 'performance_snapshots'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('trading_sessions.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    active_positions = Column(Integer, default=0)
    daily_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("TradingSession", back_populates="performance_snapshots")

class StrategyEvolution(Base):
    """Strategy evolution tracking"""
    __tablename__ = 'strategy_evolutions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('trading_sessions.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    old_parameters = Column(JSON, nullable=True)
    new_parameters = Column(JSON, nullable=False)
    evolution_reason = Column(Text, nullable=True)
    performance_before = Column(JSON, nullable=True)
    performance_after = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    llm_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("TradingSession", back_populates="strategy_evolutions")

class MarketData(Base):
    """Market data storage"""
    __tablename__ = 'market_data'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timeframe = Column(String, nullable=False)  # 1m, 5m, 1h, 1d
    technical_indicators = Column(JSON, nullable=True)
    market_regime = Column(String, nullable=True)
    volatility = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        {'extend_existing': True}
    )

class RiskMetrics(Base):
    """Risk metrics tracking"""
    __tablename__ = 'risk_metrics'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('trading_sessions.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    portfolio_value = Column(Float, nullable=False)
    total_exposure = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    var_95 = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    concentration_risk = Column(Float, default=0.0)
    correlation_risk = Column(Float, default=0.0)
    liquidity_risk = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default='low')  # low, medium, high, critical
    warnings = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TradingSignal(Base):
    """Trading signals storage"""
    __tablename__ = 'trading_signals'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    position_size = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    executed = Column(Boolean, default=False)
    execution_time = Column(DateTime, nullable=True)
    trade_id = Column(String, ForeignKey('trades.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trade = relationship("Trade")

class SystemLog(Base):
    """System logs for debugging and monitoring"""
    __tablename__ = 'system_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    component = Column(String, nullable=False)  # strategy, risk, memory, etc.
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    """User configuration and settings"""
    __tablename__ = 'user_settings'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    trading_config = Column(JSON, nullable=True)
    risk_settings = Column(JSON, nullable=True)
    notification_settings = Column(JSON, nullable=True)
    dashboard_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BacktestResult(Base):
    """Backtest results storage"""
    __tablename__ = 'backtest_results'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    calmar_ratio = Column(Float, default=0.0)
    strategy_parameters = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    trades_data = Column(JSON, nullable=True)
    equity_curve = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)