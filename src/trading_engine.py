"""
Main trading engine that orchestrates the entire EvolvingTrader system
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import signal
import sys

from src.strategy.evolving_strategy import EvolvingStrategy
from src.analysis.market_analyzer import MarketAnalyzer
from src.memory.pinecone_client import PineconeMemoryClient
from src.llm.strategy_analyzer import StrategyAnalyzer
from src.database.connection import db_manager
from src.database.repository import (
    trading_repo, strategy_repo, market_data_repo, 
    risk_repo, signal_repo, log_repo
)
from src.cache.redis_service import redis_service
from config import trading_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evolving_trader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EvolvingTraderEngine:
    """
    Main trading engine that orchestrates strategy execution, analysis, and evolution
    """
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
        self.strategy = EvolvingStrategy(self.symbols)
        self.market_analyzer = MarketAnalyzer()
        self.memory_client = PineconeMemoryClient()
        self.strategy_analyzer = StrategyAnalyzer()
        
        # Engine state
        self.is_running = False
        self.last_signal_generation = datetime.now()
        self.last_position_monitoring = datetime.now()
        self.last_strategy_evolution = datetime.now()
        self.last_performance_analysis = datetime.now()
        
        # Performance tracking
        self.start_time = datetime.now()
        self.initial_balance = trading_config.initial_capital
        self.current_balance = self.initial_balance
        self.trading_session = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing EvolvingTrader Engine...")
            
            # Initialize database
            await db_manager.initialize()
            
            # Initialize Redis cache
            await redis_service.initialize()
            
            # Initialize strategy
            await self.strategy.initialize()
            
            # Initialize memory client
            await self.memory_client.initialize()
            
            # Initialize strategy analyzer
            await self.strategy_analyzer.initialize()
            
            # Get initial balance
            self.current_balance = await self.strategy.binance_client.get_balance("USDT")
            
            # Create or get trading session
            self.trading_session = await trading_repo.get_active_session()
            if not self.trading_session:
                self.trading_session = await trading_repo.create_trading_session(
                    initial_capital=self.initial_balance,
                    symbols=self.symbols
                )
                await log_repo.log_system_event(
                    "INFO", "trading_engine", 
                    f"Created new trading session: {self.trading_session.id}"
                )
            else:
                await log_repo.log_system_event(
                    "INFO", "trading_engine", 
                    f"Resumed existing trading session: {self.trading_session.id}"
                )
            
            logger.info(f"EvolvingTrader Engine initialized successfully")
            logger.info(f"Trading session: {self.trading_session.id}")
            logger.info(f"Trading symbols: {self.symbols}")
            logger.info(f"Initial balance: {self.current_balance} USDT")
            
        except Exception as e:
            logger.error(f"Failed to initialize trading engine: {e}")
            await log_repo.log_system_event("ERROR", "trading_engine", f"Initialization failed: {e}")
            raise
    
    async def start(self):
        """Start the trading engine"""
        try:
            await self.initialize()
            self.is_running = True
            
            logger.info("Starting EvolvingTrader Engine...")
            
            # Start main trading loop
            await self._main_trading_loop()
            
        except Exception as e:
            logger.error(f"Error in trading engine: {e}")
            await self.shutdown()
    
    async def _main_trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Generate trading signals (every 5 minutes)
                if (current_time - self.last_signal_generation).total_seconds() >= 300:
                    await self._generate_and_execute_signals()
                    self.last_signal_generation = current_time
                
                # Monitor existing positions (every minute)
                if (current_time - self.last_position_monitoring).total_seconds() >= 60:
                    await self._monitor_positions()
                    self.last_position_monitoring = current_time
                
                # Evolve strategy (every hour)
                if (current_time - self.last_strategy_evolution).total_seconds() >= 3600:
                    await self._evolve_strategy()
                    self.last_strategy_evolution = current_time
                
                # Performance analysis (every 6 hours)
                if (current_time - self.last_performance_analysis).total_seconds() >= 21600:
                    await self._analyze_performance()
                    self.last_performance_analysis = current_time
                
                # Update balance
                self.current_balance = await self.strategy.binance_client.get_balance("USDT")
                
                # Cache current state in Redis
                await self._cache_current_state()
                
                # Log status every 30 minutes
                if current_time.minute % 30 == 0:
                    await self._log_status()
                
                # Sleep for 10 seconds before next iteration
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in main trading loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _generate_and_execute_signals(self):
        """Generate and execute trading signals"""
        try:
            logger.info("Generating trading signals...")
            
            for symbol in self.symbols:
                try:
                    # Generate signals for symbol
                    signals = await self.strategy.generate_signals(symbol)
                    
                    # Execute signals
                    for signal in signals:
                        if signal.confidence > 0.7:  # Only execute high-confidence signals
                            success = await self.strategy.execute_signal(signal, self.trading_session.id)
                            if success:
                                logger.info(f"Executed signal for {symbol}: {signal.signal_type.value} "
                                          f"(confidence: {signal.confidence:.2f})")
                        
                except Exception as e:
                    logger.error(f"Error generating signals for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
    
    async def _monitor_positions(self):
        """Monitor existing positions"""
        try:
            await self.strategy.monitor_positions()
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    async def _evolve_strategy(self):
        """Evolve strategy based on performance"""
        try:
            logger.info("Evolving strategy...")
            await self.strategy.evolve_strategy()
        except Exception as e:
            logger.error(f"Error evolving strategy: {e}")
    
    async def _analyze_performance(self):
        """Analyze performance and store insights"""
        try:
            logger.info("Analyzing performance...")
            
            # Get performance summary
            performance_summary = await self.strategy.get_performance_summary()
            
            # Store performance in memory
            await self.memory_client.store_performance_summary(performance_summary)
            
            # Generate insights using LLM
            insights = await self.strategy_analyzer.generate_trading_insights(performance_summary)
            
            logger.info(f"Performance Analysis - Trades: {performance_summary.get('total_trades', 0)}, "
                       f"P&L: {performance_summary.get('total_pnl', 0):.2f} USDT, "
                       f"Win Rate: {performance_summary.get('win_rate', 0):.1f}%")
            
            for insight in insights:
                logger.info(f"Insight: {insight}")
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
    
    async def _cache_current_state(self):
        """Cache current trading state in Redis"""
        try:
            # Cache performance metrics
            performance_summary = await self.strategy.get_performance_summary()
            await redis_service.cache_performance_metrics(performance_summary)
            
            # Cache active positions
            await redis_service.cache_active_positions(self.strategy.current_positions)
            
            # Cache session state
            if self.trading_session:
                session_state = {
                    'session_id': self.trading_session.id,
                    'current_balance': self.current_balance,
                    'initial_balance': self.initial_balance,
                    'symbols': self.symbols,
                    'is_running': self.is_running
                }
                await redis_service.cache_session_state(
                    self.trading_session.id, 
                    session_state
                )
            
        except Exception as e:
            logger.error(f"Error caching current state: {e}")
    
    async def _log_status(self):
        """Log current status"""
        try:
            # Get current positions
            positions = self.strategy.current_positions
            
            # Calculate performance metrics
            performance = await self.strategy.get_performance_summary()
            
            # Calculate total return
            total_return = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
            
            logger.info("=== TRADING STATUS ===")
            logger.info(f"Current Balance: {self.current_balance:.2f} USDT")
            logger.info(f"Total Return: {total_return:.2f}%")
            logger.info(f"Active Positions: {len(positions)}")
            logger.info(f"Total Trades: {performance.get('total_trades', 0)}")
            logger.info(f"Win Rate: {performance.get('win_rate', 0):.1f}%")
            logger.info(f"Total P&L: {performance.get('total_pnl', 0):.2f} USDT")
            
            if positions:
                logger.info("Active Positions:")
                for symbol, position in positions.items():
                    logger.info(f"  {symbol}: {position['side']} {position['quantity']} @ {position['entry_price']}")
            
            logger.info("=====================")
            
        except Exception as e:
            logger.error(f"Error logging status: {e}")
    
    async def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        try:
            # Get performance summary
            performance = await self.strategy.get_performance_summary()
            
            # Get memory statistics
            memory_stats = await self.memory_client.get_memory_statistics()
            
            # Calculate additional metrics
            total_return = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
            runtime = datetime.now() - self.start_time
            
            return {
                'engine_status': {
                    'is_running': self.is_running,
                    'start_time': self.start_time.isoformat(),
                    'runtime_hours': runtime.total_seconds() / 3600,
                    'symbols': self.symbols
                },
                'performance': {
                    'initial_balance': self.initial_balance,
                    'current_balance': self.current_balance,
                    'total_return_pct': total_return,
                    'total_pnl': performance.get('total_pnl', 0),
                    'total_trades': performance.get('total_trades', 0),
                    'win_rate': performance.get('win_rate', 0),
                    'profit_factor': performance.get('profit_factor', 0),
                    'current_positions': len(self.strategy.current_positions)
                },
                'strategy': {
                    'parameters': performance.get('strategy_parameters', {}),
                    'last_evolution': self.last_strategy_evolution.isoformat()
                },
                'memory': memory_stats,
                'positions': self.strategy.current_positions
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    async def shutdown(self):
        """Gracefully shutdown the trading engine"""
        try:
            logger.info("Shutting down EvolvingTrader Engine...")
            
            self.is_running = False
            
            # Close all positions (optional - comment out if you want to keep positions)
            # await self._close_all_positions()
            
            # Disconnect from Binance
            await self.strategy.binance_client.disconnect()
            
            # Store final performance summary
            final_performance = await self.strategy.get_performance_summary()
            await self.memory_client.store_performance_summary(final_performance)
            
            logger.info("EvolvingTrader Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _close_all_positions(self):
        """Close all open positions"""
        try:
            logger.info("Closing all open positions...")
            
            for symbol in list(self.strategy.current_positions.keys()):
                await self.strategy._close_position(symbol, "Engine shutdown")
            
            logger.info("All positions closed")
            
        except Exception as e:
            logger.error(f"Error closing positions: {e}")

# Main entry point
async def main():
    """Main entry point for the trading engine"""
    try:
        # Create and start the trading engine
        engine = EvolvingTraderEngine()
        await engine.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        logger.info("EvolvingTrader Engine stopped")

if __name__ == "__main__":
    asyncio.run(main())