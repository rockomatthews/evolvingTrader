"""
Database connection and session management for EvolvingTrader
"""
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os

from src.database.models import Base
from config import database_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database connection manager for Neon.tech PostgreSQL
    """
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            # Get database URL from config
            database_url = database_config.url
            
            # Create synchronous engine
            self.engine = create_engine(
                database_url,
                poolclass=NullPool,  # Use NullPool for serverless
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    "sslmode": "require",
                    "application_name": "EvolvingTrader"
                }
            )
            
            # Create async engine
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            self.async_engine = create_async_engine(
                async_url,
                poolclass=NullPool,
                echo=False,
                connect_args={
                    "ssl": "require",
                    "server_settings": {
                        "application_name": "EvolvingTrader"
                    }
                }
            )
            
            # Create session factories
            self.session_factory = sessionmaker(bind=self.engine)
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            await self._test_connection()
            
            # Create tables if they don't exist
            await self._create_tables()
            
            self.initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _test_connection(self):
        """Test database connection"""
        try:
            # Test sync connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            # Test async connection
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()
            
            logger.info("Database connection test successful")
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            # Create all tables
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session"""
        if not self.initialized:
            await self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get synchronous database session"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()
    
    @asynccontextmanager
    async def get_sync_session_context(self):
        """Get synchronous database session with context manager"""
        if not self.initialized:
            await self.initialize()
        
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    async def execute_query(self, query: str, params: dict = None):
        """Execute a raw SQL query"""
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text(query), params or {})
                return result.fetchall()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def get_database_info(self) -> dict:
        """Get database information"""
        try:
            # Get database size
            size_query = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """
            
            # Get table counts
            tables_query = """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                ORDER BY tablename
            """
            
            # Get connection info
            connections_query = """
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """
            
            async with self.get_async_session() as session:
                # Get database size
                size_result = await session.execute(text(size_query))
                db_size = size_result.fetchone()[0]
                
                # Get table statistics
                tables_result = await session.execute(text(tables_query))
                table_stats = [dict(row._mapping) for row in tables_result.fetchall()]
                
                # Get connection info
                conn_result = await session.execute(text(connections_query))
                conn_info = dict(conn_result.fetchone()._mapping)
                
                return {
                    'database_size': db_size,
                    'table_statistics': table_stats,
                    'connection_info': conn_info,
                    'database_name': os.environ.get('PGDATABASE', 'unknown'),
                    'host': os.environ.get('PGHOST', 'unknown')
                }
                
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage storage"""
        try:
            cleanup_queries = [
                # Clean up old system logs
                """
                DELETE FROM system_logs 
                WHERE created_at < NOW() - INTERVAL '%s days'
                """ % days_to_keep,
                
                # Clean up old market data (keep more recent data)
                """
                DELETE FROM market_data 
                WHERE created_at < NOW() - INTERVAL '%s days'
                AND timeframe IN ('1m', '5m')
                """ % (days_to_keep // 2),
                
                # Clean up old performance snapshots (keep daily snapshots)
                """
                DELETE FROM performance_snapshots 
                WHERE created_at < NOW() - INTERVAL '%s days'
                """ % (days_to_keep * 2),
                
                # Clean up old risk metrics
                """
                DELETE FROM risk_metrics 
                WHERE created_at < NOW() - INTERVAL '%s days'
                """ % days_to_keep
            ]
            
            async with self.get_async_session() as session:
                for query in cleanup_queries:
                    await session.execute(text(query))
                
                await session.commit()
            
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def get_performance_summary(self, session_id: str = None) -> dict:
        """Get performance summary from database"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_trades,
                    COUNT(*) FILTER (WHERE pnl > 0) as winning_trades,
                    COUNT(*) FILTER (WHERE pnl < 0) as losing_trades,
                    COALESCE(AVG(pnl), 0) as avg_pnl,
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COALESCE(MAX(pnl), 0) as best_trade,
                    COALESCE(MIN(pnl), 0) as worst_trade,
                    COALESCE(AVG(pnl) FILTER (WHERE pnl > 0), 0) as avg_win,
                    COALESCE(AVG(pnl) FILTER (WHERE pnl < 0), 0) as avg_loss
                FROM trades
                WHERE session_id = COALESCE(:session_id, session_id)
            """
            
            async with self.get_async_session() as session:
                result = await session.execute(text(query), {'session_id': session_id})
                row = result.fetchone()
                
                if row:
                    total_trades = row[0]
                    winning_trades = row[1]
                    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                    
                    return {
                        'total_trades': total_trades,
                        'winning_trades': winning_trades,
                        'losing_trades': row[2],
                        'win_rate': win_rate,
                        'total_pnl': float(row[4]),
                        'avg_pnl': float(row[3]),
                        'best_trade': float(row[5]),
                        'worst_trade': float(row[6]),
                        'avg_win': float(row[7]),
                        'avg_loss': float(row[8])
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def close(self):
        """Close database connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.engine:
                self.engine.dispose()
            
            self.initialized = False
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
async def get_db_session():
    """Get async database session"""
    async with db_manager.get_async_session() as session:
        yield session

def get_sync_db_session():
    """Get synchronous database session"""
    return db_manager.get_sync_session()