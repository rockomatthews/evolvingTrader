"""
Backtesting framework for EvolvingTrader strategy validation
"""
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json

from src.strategy.evolving_strategy import EvolvingStrategy, StrategyParameters
from src.analysis.market_analyzer import MarketAnalyzer
from src.risk.risk_manager import RiskManager
from config import trading_config

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Backtesting result"""
    total_return: float
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    trades: List[Dict]
    equity_curve: List[float]
    monthly_returns: List[float]
    strategy_parameters: Dict
    performance_metrics: Dict

class Backtester:
    """
    Comprehensive backtesting framework for strategy validation
    """
    
    def __init__(self, initial_capital: float = 1000.0):
        self.initial_capital = initial_capital
        self.strategy = None
        self.market_analyzer = MarketAnalyzer()
        self.risk_manager = RiskManager()
        
    async def run_backtest(self, symbol: str, start_date: datetime, end_date: datetime,
                          strategy_params: Optional[StrategyParameters] = None,
                          timeframe: str = '1h') -> BacktestResult:
        """Run comprehensive backtest"""
        try:
            logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # Initialize strategy
            self.strategy = EvolvingStrategy([symbol])
            if strategy_params:
                self.strategy.parameters = strategy_params
            
            # Get historical data
            historical_data = await self._get_historical_data(symbol, start_date, end_date, timeframe)
            
            if historical_data.empty:
                raise ValueError(f"No historical data available for {symbol}")
            
            # Run backtest simulation
            backtest_result = await self._simulate_trading(historical_data, symbol)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(backtest_result)
            
            # Create final result
            result = BacktestResult(
                total_return=backtest_result['total_return'],
                total_trades=backtest_result['total_trades'],
                win_rate=backtest_result['win_rate'],
                profit_factor=backtest_result['profit_factor'],
                max_drawdown=backtest_result['max_drawdown'],
                sharpe_ratio=backtest_result['sharpe_ratio'],
                calmar_ratio=backtest_result['calmar_ratio'],
                trades=backtest_result['trades'],
                equity_curve=backtest_result['equity_curve'],
                monthly_returns=backtest_result['monthly_returns'],
                strategy_parameters=self.strategy.parameters.__dict__,
                performance_metrics=performance_metrics
            )
            
            logger.info(f"Backtest completed: {result.total_return:.2f}% return, "
                       f"{result.total_trades} trades, {result.win_rate:.1f}% win rate")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise
    
    async def _get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime, timeframe: str) -> pd.DataFrame:
        """Get historical market data"""
        try:
            # In a real implementation, this would fetch data from Binance or another source
            # For now, we'll create synthetic data for demonstration
            
            # Calculate number of periods
            if timeframe == '1h':
                periods = int((end_date - start_date).total_seconds() / 3600)
            elif timeframe == '1d':
                periods = int((end_date - start_date).days)
            else:
                periods = 1000  # Default
            
            # Generate synthetic OHLCV data
            np.random.seed(42)  # For reproducible results
            
            # Generate price data with trend and volatility
            base_price = 100.0
            returns = np.random.normal(0.0001, 0.02, periods)  # 0.01% mean return, 2% volatility
            prices = [base_price]
            
            for ret in returns:
                new_price = prices[-1] * (1 + ret)
                prices.append(new_price)
            
            prices = prices[1:]  # Remove initial price
            
            # Create OHLCV data
            data = []
            for i, close in enumerate(prices):
                # Generate OHLC from close price
                volatility = abs(np.random.normal(0, 0.01))
                high = close * (1 + volatility)
                low = close * (1 - volatility)
                open_price = close * (1 + np.random.normal(0, 0.005))
                
                # Ensure OHLC relationships are valid
                high = max(high, open_price, close)
                low = min(low, open_price, close)
                
                # Generate volume
                volume = np.random.uniform(1000, 10000)
                
                timestamp = start_date + timedelta(hours=i) if timeframe == '1h' else start_date + timedelta(days=i)
                
                data.append({
                    'timestamp': timestamp,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def _simulate_trading(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Simulate trading with historical data"""
        try:
            # Initialize simulation state
            current_balance = self.initial_capital
            position = None
            trades = []
            equity_curve = [current_balance]
            
            # Process each data point
            for i in range(50, len(data)):  # Start after enough data for indicators
                current_data = data.iloc[:i+1]
                current_price = data.iloc[i]['close']
                current_time = data.iloc[i].name
                
                # Add technical indicators to current data
                current_data = self.strategy._add_technical_indicators(current_data)
                
                # Generate signals
                signals = await self._generate_signals_for_backtest(current_data, symbol, current_price)
                
                # Check for exit signals if we have a position
                if position:
                    exit_signal = await self._check_exit_signal(position, current_data, current_price)
                    if exit_signal:
                        # Close position
                        trade_pnl = self._calculate_trade_pnl(position, current_price)
                        current_balance += trade_pnl
                        
                        trades.append({
                            'entry_time': position['entry_time'],
                            'exit_time': current_time,
                            'symbol': symbol,
                            'side': position['side'],
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'quantity': position['quantity'],
                            'pnl': trade_pnl,
                            'reason': exit_signal['reason']
                        })
                        
                        position = None
                
                # Check for entry signals if we don't have a position
                if not position and signals:
                    signal = signals[0]  # Take first signal
                    if signal.confidence > 0.6:  # Minimum confidence threshold
                        # Calculate position size
                        position_value = current_balance * signal.position_size
                        quantity = position_value / current_price
                        
                        # Create position
                        position = {
                            'entry_time': current_time,
                            'symbol': symbol,
                            'side': signal.signal_type.value,
                            'entry_price': current_price,
                            'quantity': quantity,
                            'stop_loss': signal.stop_loss,
                            'take_profit': signal.take_profit
                        }
                        
                        # Deduct position value from balance
                        current_balance -= position_value
                
                # Update equity curve
                if position:
                    # Calculate unrealized P&L
                    unrealized_pnl = self._calculate_trade_pnl(position, current_price)
                    equity_curve.append(current_balance + unrealized_pnl)
                else:
                    equity_curve.append(current_balance)
            
            # Close any remaining position
            if position:
                final_price = data.iloc[-1]['close']
                final_time = data.iloc[-1].name
                trade_pnl = self._calculate_trade_pnl(position, final_price)
                current_balance += trade_pnl
                
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': final_time,
                    'symbol': symbol,
                    'side': position['side'],
                    'entry_price': position['entry_price'],
                    'exit_price': final_price,
                    'quantity': position['quantity'],
                    'pnl': trade_pnl,
                    'reason': 'End of backtest'
                })
            
            # Calculate performance metrics
            total_return = ((current_balance - self.initial_capital) / self.initial_capital) * 100
            total_trades = len(trades)
            
            if total_trades > 0:
                winning_trades = [t for t in trades if t['pnl'] > 0]
                win_rate = (len(winning_trades) / total_trades) * 100
                
                total_profit = sum(t['pnl'] for t in winning_trades)
                total_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
                profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            else:
                win_rate = 0
                profit_factor = 0
            
            # Calculate drawdown
            equity_series = pd.Series(equity_curve)
            running_max = equity_series.expanding().max()
            drawdown = (equity_series - running_max) / running_max
            max_drawdown = abs(drawdown.min()) * 100
            
            # Calculate Sharpe ratio
            if len(equity_curve) > 1:
                returns = pd.Series(equity_curve).pct_change().dropna()
                if len(returns) > 0 and returns.std() > 0:
                    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            # Calculate Calmar ratio
            calmar_ratio = (total_return / 100) / (max_drawdown / 100) if max_drawdown > 0 else 0
            
            # Calculate monthly returns
            monthly_returns = self._calculate_monthly_returns(equity_curve, data.index)
            
            return {
                'total_return': total_return,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'calmar_ratio': calmar_ratio,
                'trades': trades,
                'equity_curve': equity_curve,
                'monthly_returns': monthly_returns
            }
            
        except Exception as e:
            logger.error(f"Error in trading simulation: {e}")
            raise
    
    async def _generate_signals_for_backtest(self, data: pd.DataFrame, symbol: str, current_price: float) -> List:
        """Generate trading signals for backtest"""
        try:
            if len(data) < 50:
                return []
            
            latest = data.iloc[-1]
            
            # Generate signals using the same logic as live trading
            momentum_signal = self.strategy._momentum_strategy(latest, current_price)
            mean_reversion_signal = self.strategy._mean_reversion_strategy(latest, current_price)
            trend_signal = self.strategy._trend_strategy(latest, current_price)
            volume_signal = self.strategy._volume_strategy(latest, current_price)
            
            # Combine signals
            combined_signal = self.strategy._combine_signals(
                momentum_signal, mean_reversion_signal, trend_signal, volume_signal
            )
            
            if combined_signal['signal'].value != 'HOLD':
                from src.strategy.evolving_strategy import TradingSignal, SignalType
                
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=SignalType(combined_signal['signal'].value),
                    confidence=combined_signal['confidence'],
                    entry_price=current_price,
                    stop_loss=combined_signal.get('stop_loss'),
                    take_profit=combined_signal.get('take_profit'),
                    position_size=combined_signal['position_size'],
                    reasoning=combined_signal['reasoning'],
                    timestamp=datetime.now()
                )
                
                return [signal]
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating signals for backtest: {e}")
            return []
    
    async def _check_exit_signal(self, position: Dict, data: pd.DataFrame, current_price: float) -> Optional[Dict]:
        """Check for exit signals"""
        try:
            # Check stop loss and take profit
            if position['side'] == 'BUY':
                if position['stop_loss'] and current_price <= position['stop_loss']:
                    return {'reason': 'Stop loss hit'}
                if position['take_profit'] and current_price >= position['take_profit']:
                    return {'reason': 'Take profit hit'}
            else:  # SELL
                if position['stop_loss'] and current_price >= position['stop_loss']:
                    return {'reason': 'Stop loss hit'}
                if position['take_profit'] and current_price <= position['take_profit']:
                    return {'reason': 'Take profit hit'}
            
            # Check for exit signals from strategy
            exit_signals = await self._generate_signals_for_backtest(data, position['symbol'], current_price)
            for signal in exit_signals:
                if signal.signal_type.value == 'SELL' and position['side'] == 'BUY':
                    return {'reason': f'Exit signal: {signal.reasoning}'}
                elif signal.signal_type.value == 'BUY' and position['side'] == 'SELL':
                    return {'reason': f'Exit signal: {signal.reasoning}'}
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit signal: {e}")
            return None
    
    def _calculate_trade_pnl(self, position: Dict, exit_price: float) -> float:
        """Calculate trade P&L"""
        try:
            if position['side'] == 'BUY':
                pnl = (exit_price - position['entry_price']) * position['quantity']
            else:  # SELL
                pnl = (position['entry_price'] - exit_price) * position['quantity']
            
            return pnl
            
        except Exception as e:
            logger.error(f"Error calculating trade P&L: {e}")
            return 0.0
    
    def _calculate_monthly_returns(self, equity_curve: List[float], timestamps: pd.DatetimeIndex) -> List[float]:
        """Calculate monthly returns"""
        try:
            if len(equity_curve) != len(timestamps):
                return []
            
            # Create DataFrame with equity and timestamps
            df = pd.DataFrame({
                'equity': equity_curve,
                'timestamp': timestamps
            })
            
            # Group by month and calculate returns
            df['month'] = df['timestamp'].dt.to_period('M')
            monthly_equity = df.groupby('month')['equity'].last()
            monthly_returns = monthly_equity.pct_change().dropna() * 100
            
            return monthly_returns.tolist()
            
        except Exception as e:
            logger.error(f"Error calculating monthly returns: {e}")
            return []
    
    def _calculate_performance_metrics(self, backtest_result: Dict) -> Dict[str, Any]:
        """Calculate additional performance metrics"""
        try:
            trades = backtest_result['trades']
            equity_curve = backtest_result['equity_curve']
            
            if not trades:
                return {}
            
            # Trade statistics
            trade_pnls = [t['pnl'] for t in trades]
            winning_trades = [pnl for pnl in trade_pnls if pnl > 0]
            losing_trades = [pnl for pnl in trade_pnls if pnl < 0]
            
            # Average win/loss
            avg_win = np.mean(winning_trades) if winning_trades else 0
            avg_loss = np.mean(losing_trades) if losing_trades else 0
            
            # Largest win/loss
            largest_win = max(winning_trades) if winning_trades else 0
            largest_loss = min(losing_trades) if losing_trades else 0
            
            # Consecutive wins/losses
            consecutive_wins = self._calculate_consecutive_wins_losses(trade_pnls, True)
            consecutive_losses = self._calculate_consecutive_wins_losses(trade_pnls, False)
            
            # Recovery factor
            recovery_factor = backtest_result['total_return'] / backtest_result['max_drawdown'] if backtest_result['max_drawdown'] > 0 else 0
            
            # Expectancy
            expectancy = (backtest_result['win_rate'] / 100) * avg_win + ((100 - backtest_result['win_rate']) / 100) * avg_loss
            
            return {
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'largest_win': largest_win,
                'largest_loss': largest_loss,
                'consecutive_wins': consecutive_wins,
                'consecutive_losses': consecutive_losses,
                'recovery_factor': recovery_factor,
                'expectancy': expectancy,
                'total_profit': sum(winning_trades),
                'total_loss': abs(sum(losing_trades))
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _calculate_consecutive_wins_losses(self, trade_pnls: List[float], wins: bool) -> int:
        """Calculate maximum consecutive wins or losses"""
        try:
            max_consecutive = 0
            current_consecutive = 0
            
            for pnl in trade_pnls:
                if (wins and pnl > 0) or (not wins and pnl < 0):
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
            
        except Exception as e:
            logger.error(f"Error calculating consecutive wins/losses: {e}")
            return 0
    
    async def run_parameter_optimization(self, symbol: str, start_date: datetime, end_date: datetime,
                                       parameter_ranges: Dict[str, List]) -> Dict[str, Any]:
        """Run parameter optimization"""
        try:
            logger.info("Starting parameter optimization...")
            
            best_result = None
            best_score = -float('inf')
            optimization_results = []
            
            # Generate parameter combinations
            import itertools
            
            param_names = list(parameter_ranges.keys())
            param_values = list(parameter_ranges.values())
            
            for combination in itertools.product(*param_values):
                # Create strategy parameters
                params_dict = dict(zip(param_names, combination))
                strategy_params = StrategyParameters(**params_dict)
                
                # Run backtest
                result = await self.run_backtest(symbol, start_date, end_date, strategy_params)
                
                # Calculate optimization score (Sharpe ratio * win rate * (1 - max_drawdown))
                score = (result.sharpe_ratio * result.win_rate * (1 - result.max_drawdown / 100))
                
                optimization_results.append({
                    'parameters': params_dict,
                    'score': score,
                    'total_return': result.total_return,
                    'win_rate': result.win_rate,
                    'max_drawdown': result.max_drawdown,
                    'sharpe_ratio': result.sharpe_ratio
                })
                
                if score > best_score:
                    best_score = score
                    best_result = result
            
            logger.info(f"Parameter optimization completed. Best score: {best_score:.4f}")
            
            return {
                'best_result': best_result,
                'best_score': best_score,
                'all_results': optimization_results
            }
            
        except Exception as e:
            logger.error(f"Error in parameter optimization: {e}")
            raise
    
    def save_backtest_results(self, result: BacktestResult, filename: str):
        """Save backtest results to file"""
        try:
            # Convert result to dictionary
            result_dict = {
                'total_return': result.total_return,
                'total_trades': result.total_trades,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor,
                'max_drawdown': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'calmar_ratio': result.calmar_ratio,
                'trades': result.trades,
                'equity_curve': result.equity_curve,
                'monthly_returns': result.monthly_returns,
                'strategy_parameters': result.strategy_parameters,
                'performance_metrics': result.performance_metrics
            }
            
            # Save to JSON file
            with open(filename, 'w') as f:
                json.dump(result_dict, f, indent=2, default=str)
            
            logger.info(f"Backtest results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving backtest results: {e}")