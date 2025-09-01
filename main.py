"""
EvolvingTrader - AI-Powered Trading Strategy
Main entry point for the trading system
"""
import asyncio
import argparse
import logging
import sys
from datetime import datetime, timedelta

from src.trading_engine import EvolvingTraderEngine
from src.backtesting.backtester import Backtester
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

async def run_live_trading():
    """Run live trading"""
    try:
        logger.info("Starting EvolvingTrader in LIVE TRADING mode")
        
        # Create and start the trading engine
        engine = EvolvingTraderEngine()
        await engine.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in live trading: {e}")
    finally:
        logger.info("Live trading stopped")

async def run_backtest():
    """Run backtest"""
    try:
        logger.info("Starting EvolvingTrader in BACKTEST mode")
        
        # Create backtester
        backtester = Backtester(initial_capital=trading_config.initial_capital)
        
        # Define backtest parameters
        symbol = 'BTCUSDT'
        start_date = datetime.now() - timedelta(days=90)  # 3 months
        end_date = datetime.now()
        
        # Run backtest
        result = await backtester.run_backtest(symbol, start_date, end_date)
        
        # Print results
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: ${trading_config.initial_capital:,.2f}")
        print(f"Total Return: {result.total_return:.2f}%")
        print(f"Total Trades: {result.total_trades}")
        print(f"Win Rate: {result.win_rate:.1f}%")
        print(f"Profit Factor: {result.profit_factor:.2f}")
        print(f"Max Drawdown: {result.max_drawdown:.2f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Calmar Ratio: {result.calmar_ratio:.2f}")
        
        if result.performance_metrics:
            print("\nAdditional Metrics:")
            for key, value in result.performance_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        print("="*50)
        
        # Save results
        filename = f"backtest_results_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backtester.save_backtest_results(result, filename)
        
    except Exception as e:
        logger.error(f"Error in backtest: {e}")

async def run_optimization():
    """Run parameter optimization"""
    try:
        logger.info("Starting EvolvingTrader in OPTIMIZATION mode")
        
        # Create backtester
        backtester = Backtester(initial_capital=trading_config.initial_capital)
        
        # Define optimization parameters
        symbol = 'BTCUSDT'
        start_date = datetime.now() - timedelta(days=60)  # 2 months
        end_date = datetime.now()
        
        # Define parameter ranges to optimize
        parameter_ranges = {
            'rsi_period': [10, 14, 20],
            'rsi_oversold': [25, 30, 35],
            'rsi_overbought': [65, 70, 75],
            'bb_period': [15, 20, 25],
            'bb_std': [1.5, 2.0, 2.5],
            'max_position_size': [0.05, 0.1, 0.15],
            'stop_loss_pct': [0.015, 0.02, 0.025],
            'take_profit_pct': [0.03, 0.04, 0.05]
        }
        
        # Run optimization
        optimization_result = await backtester.run_parameter_optimization(
            symbol, start_date, end_date, parameter_ranges
        )
        
        # Print results
        print("\n" + "="*50)
        print("OPTIMIZATION RESULTS")
        print("="*50)
        print(f"Best Score: {optimization_result['best_score']:.4f}")
        print(f"Best Parameters:")
        for key, value in optimization_result['best_result'].strategy_parameters.items():
            print(f"  {key}: {value}")
        
        print(f"\nBest Performance:")
        print(f"  Total Return: {optimization_result['best_result'].total_return:.2f}%")
        print(f"  Win Rate: {optimization_result['best_result'].win_rate:.1f}%")
        print(f"  Max Drawdown: {optimization_result['best_result'].max_drawdown:.2f}%")
        print(f"  Sharpe Ratio: {optimization_result['best_result'].sharpe_ratio:.2f}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error in optimization: {e}")

def run_dashboard():
    """Run dashboard"""
    try:
        logger.info("Starting EvolvingTrader DASHBOARD")
        
        # Import and run dashboard
        from dashboard import run_dashboard
        run_dashboard()
        
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='EvolvingTrader - AI-Powered Trading Strategy')
    parser.add_argument('mode', choices=['live', 'backtest', 'optimize', 'dashboard'], 
                       help='Mode to run the system in')
    parser.add_argument('--symbols', nargs='+', default=['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],
                       help='Trading symbols (for live mode)')
    parser.add_argument('--initial-capital', type=float, default=1000.0,
                       help='Initial capital for backtesting')
    
    args = parser.parse_args()
    
    # Update trading config if needed
    if args.initial_capital != 1000.0:
        trading_config.initial_capital = args.initial_capital
    
    try:
        if args.mode == 'live':
            asyncio.run(run_live_trading())
        elif args.mode == 'backtest':
            asyncio.run(run_backtest())
        elif args.mode == 'optimize':
            asyncio.run(run_optimization())
        elif args.mode == 'dashboard':
            run_dashboard()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()