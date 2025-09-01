"""
Repository pattern for database operations
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, func, desc, and_, or_
from sqlalchemy.orm import selectinload
import logging

from src.database.connection import db_manager
from src.database.models import (
    TradingSession, Trade, PerformanceSnapshot, StrategyEvolution,
    MarketData, RiskMetrics, TradingSignal, SystemLog, UserSettings, BacktestResult
)

logger = logging.getLogger(__name__)

class TradingRepository:
    """Repository for trading-related database operations"""
    
    async def create_trading_session(self, initial_capital: float, symbols: List[str]) -> TradingSession:
        """Create a new trading session"""
        try:
            async with db_manager.get_async_session() as session:
                trading_session = TradingSession(
                    initial_capital=initial_capital,
                    symbols=symbols,
                    status='active'
                )
                session.add(trading_session)
                await session.commit()
                await session.refresh(trading_session)
                return trading_session
        except Exception as e:
            logger.error(f"Error creating trading session: {e}")
            raise
    
    async def get_active_session(self) -> Optional[TradingSession]:
        """Get the currently active trading session"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(TradingSession)
                    .where(TradingSession.status == 'active')
                    .order_by(desc(TradingSession.created_at))
                    .limit(1)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting active session: {e}")
            return None
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """Update trading session"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    update(TradingSession)
                    .where(TradingSession.id == session_id)
                    .values(**kwargs, updated_at=datetime.utcnow())
                )
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    async def create_trade(self, trade_data: Dict[str, Any]) -> Trade:
        """Create a new trade record"""
        try:
            async with db_manager.get_async_session() as session:
                trade = Trade(**trade_data)
                session.add(trade)
                await session.commit()
                await session.refresh(trade)
                return trade
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            raise
    
    async def update_trade(self, trade_id: str, **kwargs) -> bool:
        """Update trade record"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    update(Trade)
                    .where(Trade.id == trade_id)
                    .values(**kwargs)
                )
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating trade: {e}")
            return False
    
    async def get_trades(self, session_id: str = None, limit: int = 100) -> List[Trade]:
        """Get trades for a session"""
        try:
            async with db_manager.get_async_session() as session:
                query = select(Trade)
                if session_id:
                    query = query.where(Trade.session_id == session_id)
                
                query = query.order_by(desc(Trade.entry_time)).limit(limit)
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
    
    async def get_open_trades(self, session_id: str) -> List[Trade]:
        """Get open trades for a session"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(Trade)
                    .where(and_(
                        Trade.session_id == session_id,
                        Trade.exit_time.is_(None)
                    ))
                    .order_by(desc(Trade.entry_time))
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return []
    
    async def create_performance_snapshot(self, snapshot_data: Dict[str, Any]) -> PerformanceSnapshot:
        """Create performance snapshot"""
        try:
            async with db_manager.get_async_session() as session:
                snapshot = PerformanceSnapshot(**snapshot_data)
                session.add(snapshot)
                await session.commit()
                await session.refresh(snapshot)
                return snapshot
        except Exception as e:
            logger.error(f"Error creating performance snapshot: {e}")
            raise
    
    async def get_performance_history(self, session_id: str, limit: int = 100) -> List[PerformanceSnapshot]:
        """Get performance history"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(PerformanceSnapshot)
                    .where(PerformanceSnapshot.session_id == session_id)
                    .order_by(desc(PerformanceSnapshot.timestamp))
                    .limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []

class StrategyRepository:
    """Repository for strategy-related database operations"""
    
    async def create_strategy_evolution(self, evolution_data: Dict[str, Any]) -> StrategyEvolution:
        """Create strategy evolution record"""
        try:
            async with db_manager.get_async_session() as session:
                evolution = StrategyEvolution(**evolution_data)
                session.add(evolution)
                await session.commit()
                await session.refresh(evolution)
                return evolution
        except Exception as e:
            logger.error(f"Error creating strategy evolution: {e}")
            raise
    
    async def get_strategy_evolutions(self, session_id: str, limit: int = 50) -> List[StrategyEvolution]:
        """Get strategy evolution history"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(StrategyEvolution)
                    .where(StrategyEvolution.session_id == session_id)
                    .order_by(desc(StrategyEvolution.timestamp))
                    .limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting strategy evolutions: {e}")
            return []

class MarketDataRepository:
    """Repository for market data operations"""
    
    async def store_market_data(self, market_data: Dict[str, Any]) -> MarketData:
        """Store market data"""
        try:
            async with db_manager.get_async_session() as session:
                data = MarketData(**market_data)
                session.add(data)
                await session.commit()
                await session.refresh(data)
                return data
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            raise
    
    async def get_latest_market_data(self, symbol: str, timeframe: str = '1h') -> Optional[MarketData]:
        """Get latest market data for symbol"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(MarketData)
                    .where(and_(
                        MarketData.symbol == symbol,
                        MarketData.timeframe == timeframe
                    ))
                    .order_by(desc(MarketData.timestamp))
                    .limit(1)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting latest market data: {e}")
            return None
    
    async def get_market_data_range(self, symbol: str, start_time: datetime, 
                                   end_time: datetime, timeframe: str = '1h') -> List[MarketData]:
        """Get market data for a time range"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(MarketData)
                    .where(and_(
                        MarketData.symbol == symbol,
                        MarketData.timeframe == timeframe,
                        MarketData.timestamp >= start_time,
                        MarketData.timestamp <= end_time
                    ))
                    .order_by(MarketData.timestamp)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting market data range: {e}")
            return []

class RiskRepository:
    """Repository for risk-related database operations"""
    
    async def store_risk_metrics(self, risk_data: Dict[str, Any]) -> RiskMetrics:
        """Store risk metrics"""
        try:
            async with db_manager.get_async_session() as session:
                metrics = RiskMetrics(**risk_data)
                session.add(metrics)
                await session.commit()
                await session.refresh(metrics)
                return metrics
        except Exception as e:
            logger.error(f"Error storing risk metrics: {e}")
            raise
    
    async def get_latest_risk_metrics(self, session_id: str = None) -> Optional[RiskMetrics]:
        """Get latest risk metrics"""
        try:
            async with db_manager.get_async_session() as session:
                query = select(RiskMetrics)
                if session_id:
                    query = query.where(RiskMetrics.session_id == session_id)
                
                result = await session.execute(
                    query.order_by(desc(RiskMetrics.timestamp)).limit(1)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting latest risk metrics: {e}")
            return None

class SignalRepository:
    """Repository for trading signal operations"""
    
    async def store_trading_signal(self, signal_data: Dict[str, Any]) -> TradingSignal:
        """Store trading signal"""
        try:
            async with db_manager.get_async_session() as session:
                signal = TradingSignal(**signal_data)
                session.add(signal)
                await session.commit()
                await session.refresh(signal)
                return signal
        except Exception as e:
            logger.error(f"Error storing trading signal: {e}")
            raise
    
    async def get_recent_signals(self, symbol: str = None, limit: int = 50) -> List[TradingSignal]:
        """Get recent trading signals"""
        try:
            async with db_manager.get_async_session() as session:
                query = select(TradingSignal)
                if symbol:
                    query = query.where(TradingSignal.symbol == symbol)
                
                result = await session.execute(
                    query.order_by(desc(TradingSignal.timestamp)).limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting recent signals: {e}")
            return []

class LogRepository:
    """Repository for system log operations"""
    
    async def log_system_event(self, level: str, component: str, message: str, data: Dict = None):
        """Log system event"""
        try:
            async with db_manager.get_async_session() as session:
                log_entry = SystemLog(
                    level=level,
                    component=component,
                    message=message,
                    data=data
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging system event: {e}")
    
    async def get_system_logs(self, level: str = None, component: str = None, 
                             limit: int = 100) -> List[SystemLog]:
        """Get system logs"""
        try:
            async with db_manager.get_async_session() as session:
                query = select(SystemLog)
                if level:
                    query = query.where(SystemLog.level == level)
                if component:
                    query = query.where(SystemLog.component == component)
                
                result = await session.execute(
                    query.order_by(desc(SystemLog.timestamp)).limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting system logs: {e}")
            return []

class BacktestRepository:
    """Repository for backtest operations"""
    
    async def store_backtest_result(self, result_data: Dict[str, Any]) -> BacktestResult:
        """Store backtest result"""
        try:
            async with db_manager.get_async_session() as session:
                result = BacktestResult(**result_data)
                session.add(result)
                await session.commit()
                await session.refresh(result)
                return result
        except Exception as e:
            logger.error(f"Error storing backtest result: {e}")
            raise
    
    async def get_backtest_results(self, symbol: str = None, limit: int = 20) -> List[BacktestResult]:
        """Get backtest results"""
        try:
            async with db_manager.get_async_session() as session:
                query = select(BacktestResult)
                if symbol:
                    query = query.where(BacktestResult.symbol == symbol)
                
                result = await session.execute(
                    query.order_by(desc(BacktestResult.created_at)).limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting backtest results: {e}")
            return []

# Repository instances
trading_repo = TradingRepository()
strategy_repo = StrategyRepository()
market_data_repo = MarketDataRepository()
risk_repo = RiskRepository()
signal_repo = SignalRepository()
log_repo = LogRepository()
backtest_repo = BacktestRepository()