"""
Core evolving trading strategy that adapts using LLM analysis
"""
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

import ta
from src.trading.binance_client import BinanceTradingClient
from src.memory.pinecone_client import PineconeMemoryClient
from src.llm.strategy_analyzer import StrategyAnalyzer
from src.database.repository import trading_repo, signal_repo, log_repo
from config import trading_config

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    confidence: float
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    position_size: float
    reasoning: str
    timestamp: datetime

@dataclass
class StrategyParameters:
    """Dynamic strategy parameters that evolve over time"""
    # Momentum parameters
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    
    # Volatility parameters
    bb_period: int = 20
    bb_std: float = 2.0
    
    # Trend parameters
    ema_fast: int = 12
    ema_slow: int = 26
    macd_signal: int = 9
    
    # Volume parameters
    volume_ma_period: int = 20
    volume_threshold: float = 1.5
    
    # Risk parameters
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    
    # Strategy weights
    momentum_weight: float = 0.3
    mean_reversion_weight: float = 0.3
    trend_weight: float = 0.2
    volume_weight: float = 0.2

class EvolvingStrategy:
    """
    AI-powered trading strategy that evolves based on market conditions
    and performance feedback using LLM analysis
    """
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.binance_client = BinanceTradingClient()
        self.memory_client = PineconeMemoryClient()
        self.strategy_analyzer = StrategyAnalyzer()
        
        # Strategy state
        self.parameters = StrategyParameters()
        self.current_positions: Dict[str, Dict] = {}
        self.performance_history: List[Dict] = []
        self.last_analysis_time = datetime.now()
        
        # Market data cache
        self.market_data: Dict[str, pd.DataFrame] = {}
        
    async def initialize(self):
        """Initialize the strategy"""
        await self.binance_client.connect()
        await self.memory_client.initialize()
        await self.strategy_analyzer.initialize()
        
        # Load historical performance from memory
        await self._load_strategy_memory()
        
        logger.info("EvolvingStrategy initialized")
    
    async def _load_strategy_memory(self):
        """Load strategy parameters and performance from Pinecone"""
        try:
            # Query for recent strategy parameters
            recent_params = await self.memory_client.query_strategy_parameters(
                limit=1
            )
            
            if recent_params:
                # Update parameters with most recent successful configuration
                param_data = recent_params[0]['metadata']
                for key, value in param_data.items():
                    if hasattr(self.parameters, key):
                        setattr(self.parameters, key, value)
                
                logger.info("Loaded strategy parameters from memory")
            
            # Load performance history
            performance_data = await self.memory_client.query_performance_history(
                limit=100
            )
            
            if performance_data:
                self.performance_history = [
                    item['metadata'] for item in performance_data
                ]
                logger.info(f"Loaded {len(self.performance_history)} performance records")
                
        except Exception as e:
            logger.warning(f"Failed to load strategy memory: {e}")
    
    async def update_market_data(self, symbol: str) -> pd.DataFrame:
        """Update market data for a symbol"""
        try:
            # Get multiple timeframes for comprehensive analysis
            timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
            all_data = {}
            
            for tf in timeframes:
                data = await self.binance_client.get_klines(symbol, tf, 500)
                all_data[tf] = data
            
            # Use 1h as primary timeframe
            primary_data = all_data['1h'].copy()
            
            # Add technical indicators
            primary_data = self._add_technical_indicators(primary_data)
            
            # Store in cache
            self.market_data[symbol] = primary_data
            
            return primary_data
            
        except Exception as e:
            logger.error(f"Failed to update market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to market data"""
        try:
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=self.parameters.rsi_period).rsi()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'], window=self.parameters.bb_period, window_dev=self.parameters.bb_std)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # MACD
            macd = ta.trend.MACD(df['close'], window_fast=self.parameters.ema_fast, 
                               window_slow=self.parameters.ema_slow, window_sign=self.parameters.macd_signal)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # EMAs
            df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=self.parameters.ema_fast).ema_indicator()
            df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=self.parameters.ema_slow).ema_indicator()
            
            # Volume indicators
            df['volume_ma'] = df['volume'].rolling(window=self.parameters.volume_ma_period).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            # Volatility
            df['volatility'] = df['close'].pct_change().rolling(window=20).std()
            
            # Price momentum
            df['momentum_5'] = df['close'].pct_change(5)
            df['momentum_10'] = df['close'].pct_change(10)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to add technical indicators: {e}")
            return df
    
    async def generate_signals(self, symbol: str) -> List[TradingSignal]:
        """Generate trading signals for a symbol"""
        try:
            # Update market data
            df = await self.update_market_data(symbol)
            if df.empty:
                return []
            
            signals = []
            latest = df.iloc[-1]
            
            # Get current price
            current_price = await self.binance_client.get_ticker_price(symbol)
            
            # Generate signals based on multiple strategies
            momentum_signal = self._momentum_strategy(latest, current_price)
            mean_reversion_signal = self._mean_reversion_strategy(latest, current_price)
            trend_signal = self._trend_strategy(latest, current_price)
            volume_signal = self._volume_strategy(latest, current_price)
            
            # Combine signals with weights
            combined_signal = self._combine_signals(
                momentum_signal, mean_reversion_signal, 
                trend_signal, volume_signal
            )
            
            if combined_signal['signal'] != SignalType.HOLD:
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=combined_signal['signal'],
                    confidence=combined_signal['confidence'],
                    entry_price=current_price,
                    stop_loss=combined_signal.get('stop_loss'),
                    take_profit=combined_signal.get('take_profit'),
                    position_size=combined_signal['position_size'],
                    reasoning=combined_signal['reasoning'],
                    timestamp=datetime.now()
                )
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Failed to generate signals for {symbol}: {e}")
            return []
    
    def _momentum_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Momentum-based trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        # RSI momentum
        rsi = data['rsi']
        if pd.isna(rsi):
            return signal
        
        # MACD momentum
        macd = data['macd']
        macd_signal = data['macd_signal']
        macd_hist = data['macd_histogram']
        
        confidence = 0.0
        reasoning_parts = []
        
        # RSI signals
        if rsi < self.parameters.rsi_oversold:
            confidence += 0.3
            reasoning_parts.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > self.parameters.rsi_overbought:
            confidence += 0.3
            reasoning_parts.append(f"RSI overbought ({rsi:.1f})")
        
        # MACD signals
        if not pd.isna(macd) and not pd.isna(macd_signal):
            if macd > macd_signal and macd_hist > 0:
                confidence += 0.4
                reasoning_parts.append("MACD bullish crossover")
            elif macd < macd_signal and macd_hist < 0:
                confidence += 0.4
                reasoning_parts.append("MACD bearish crossover")
        
        # Price momentum
        momentum_5 = data['momentum_5']
        if not pd.isna(momentum_5):
            if momentum_5 > 0.02:  # 2% positive momentum
                confidence += 0.3
                reasoning_parts.append("Strong 5-period momentum")
            elif momentum_5 < -0.02:  # 2% negative momentum
                confidence += 0.3
                reasoning_parts.append("Strong 5-period negative momentum")
        
        if confidence > 0.6:
            if rsi < self.parameters.rsi_oversold or (not pd.isna(macd) and macd > macd_signal):
                signal['signal'] = SignalType.BUY
            else:
                signal['signal'] = SignalType.SELL
        
        signal['confidence'] = min(confidence, 1.0)
        signal['reasoning'] = "Momentum: " + ", ".join(reasoning_parts)
        
        return signal
    
    def _mean_reversion_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Mean reversion trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        bb_upper = data['bb_upper']
        bb_lower = data['bb_lower']
        bb_middle = data['bb_middle']
        
        if pd.isna(bb_upper) or pd.isna(bb_lower) or pd.isna(bb_middle):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # Bollinger Band signals
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        if bb_position < 0.1:  # Near lower band
            confidence += 0.6
            reasoning_parts.append("Price near BB lower band")
        elif bb_position > 0.9:  # Near upper band
            confidence += 0.6
            reasoning_parts.append("Price near BB upper band")
        
        # Volatility expansion
        bb_width = data['bb_width']
        if not pd.isna(bb_width):
            if bb_width > 0.1:  # High volatility
                confidence += 0.2
                reasoning_parts.append("High volatility (mean reversion setup)")
        
        if confidence > 0.5:
            if bb_position < 0.1:
                signal['signal'] = SignalType.BUY
            else:
                signal['signal'] = SignalType.SELL
        
        signal['confidence'] = min(confidence, 1.0)
        signal['reasoning'] = "Mean Reversion: " + ", ".join(reasoning_parts)
        
        return signal
    
    def _trend_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Trend-following trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        ema_fast = data['ema_fast']
        ema_slow = data['ema_slow']
        
        if pd.isna(ema_fast) or pd.isna(ema_slow):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # EMA crossover
        if ema_fast > ema_slow:
            confidence += 0.5
            reasoning_parts.append("EMA fast > EMA slow (uptrend)")
        else:
            confidence += 0.5
            reasoning_parts.append("EMA fast < EMA slow (downtrend)")
        
        # Price relative to EMAs
        if current_price > ema_fast > ema_slow:
            confidence += 0.3
            reasoning_parts.append("Price above both EMAs")
        elif current_price < ema_fast < ema_slow:
            confidence += 0.3
            reasoning_parts.append("Price below both EMAs")
        
        if confidence > 0.6:
            if ema_fast > ema_slow and current_price > ema_fast:
                signal['signal'] = SignalType.BUY
            elif ema_fast < ema_slow and current_price < ema_fast:
                signal['signal'] = SignalType.SELL
        
        signal['confidence'] = min(confidence, 1.0)
        signal['reasoning'] = "Trend: " + ", ".join(reasoning_parts)
        
        return signal
    
    def _volume_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Volume-based trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        volume_ratio = data['volume_ratio']
        
        if pd.isna(volume_ratio):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # High volume confirmation
        if volume_ratio > self.parameters.volume_threshold:
            confidence += 0.4
            reasoning_parts.append(f"High volume ({volume_ratio:.1f}x average)")
        
        # Volume trend
        if volume_ratio > 2.0:
            confidence += 0.3
            reasoning_parts.append("Very high volume")
        
        signal['confidence'] = min(confidence, 1.0)
        signal['reasoning'] = "Volume: " + ", ".join(reasoning_parts)
        
        return signal
    
    def _combine_signals(self, momentum: Dict, mean_reversion: Dict, 
                        trend: Dict, volume: Dict) -> Dict:
        """Combine multiple signals with weighted scoring"""
        
        # Calculate weighted confidence scores
        buy_score = 0.0
        sell_score = 0.0
        all_reasoning = []
        
        # Momentum signals
        if momentum['signal'] == SignalType.BUY:
            buy_score += momentum['confidence'] * self.parameters.momentum_weight
        elif momentum['signal'] == SignalType.SELL:
            sell_score += momentum['confidence'] * self.parameters.momentum_weight
        all_reasoning.append(momentum['reasoning'])
        
        # Mean reversion signals
        if mean_reversion['signal'] == SignalType.BUY:
            buy_score += mean_reversion['confidence'] * self.parameters.mean_reversion_weight
        elif mean_reversion['signal'] == SignalType.SELL:
            sell_score += mean_reversion['confidence'] * self.parameters.mean_reversion_weight
        all_reasoning.append(mean_reversion['reasoning'])
        
        # Trend signals
        if trend['signal'] == SignalType.BUY:
            buy_score += trend['confidence'] * self.parameters.trend_weight
        elif trend['signal'] == SignalType.SELL:
            sell_score += trend['confidence'] * self.parameters.trend_weight
        all_reasoning.append(trend['reasoning'])
        
        # Volume signals (confirmation only)
        volume_boost = volume['confidence'] * self.parameters.volume_weight
        if buy_score > sell_score:
            buy_score += volume_boost
        else:
            sell_score += volume_boost
        all_reasoning.append(volume['reasoning'])
        
        # Determine final signal
        final_signal = SignalType.HOLD
        final_confidence = 0.0
        
        if buy_score > sell_score and buy_score > 0.6:
            final_signal = SignalType.BUY
            final_confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.6:
            final_signal = SignalType.SELL
            final_confidence = sell_score
        
        # Calculate position size based on confidence
        position_size = min(final_confidence * self.parameters.max_position_size, 
                          self.parameters.max_position_size)
        
        # Calculate stop loss and take profit
        stop_loss = None
        take_profit = None
        
        if final_signal != SignalType.HOLD:
            if final_signal == SignalType.BUY:
                stop_loss = current_price * (1 - self.parameters.stop_loss_pct)
                take_profit = current_price * (1 + self.parameters.take_profit_pct)
            else:
                stop_loss = current_price * (1 + self.parameters.stop_loss_pct)
                take_profit = current_price * (1 - self.parameters.take_profit_pct)
        
        return {
            'signal': final_signal,
            'confidence': final_confidence,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': " | ".join([r for r in all_reasoning if r])
        }
    
    async def execute_signal(self, signal: TradingSignal, session_id: str = None) -> bool:
        """Execute a trading signal"""
        try:
            # Check if we already have a position
            if signal.symbol in self.current_positions:
                logger.info(f"Position already exists for {signal.symbol}, skipping signal")
                return False
            
            # Get current balance
            balance = await self.binance_client.get_balance("USDT")
            
            # Calculate position size in USDT
            position_value = balance * signal.position_size
            
            # Get symbol info for quantity calculation
            symbol_info = await self.binance_client.get_symbol_info(signal.symbol)
            
            # Calculate quantity based on lot size
            step_size = float([f['stepSize'] for f in symbol_info['filters'] 
                             if f['filterType'] == 'LOT_SIZE'][0])
            
            quantity = (position_value / signal.entry_price)
            quantity = round(quantity / step_size) * step_size
            
            if quantity <= 0:
                logger.warning(f"Invalid quantity calculated: {quantity}")
                return False
            
            # Place order
            side = "BUY" if signal.signal_type == SignalType.BUY else "SELL"
            order = await self.binance_client.place_order(
                symbol=signal.symbol,
                side=side,
                order_type="MARKET",
                quantity=quantity
            )
            
            # Store position information
            self.current_positions[signal.symbol] = {
                'order_id': order['orderId'],
                'side': side,
                'quantity': quantity,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'timestamp': signal.timestamp,
                'reasoning': signal.reasoning
            }
            
            # Store trade in database
            if session_id:
                trade_data = {
                    'session_id': session_id,
                    'symbol': signal.symbol,
                    'side': side,
                    'entry_price': signal.entry_price,
                    'quantity': quantity,
                    'entry_time': signal.timestamp,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'order_id': str(order['orderId'])
                }
                await trading_repo.create_trade(trade_data)
            
            # Store signal in database
            signal_data = {
                'symbol': signal.symbol,
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'position_size': signal.position_size,
                'reasoning': signal.reasoning,
                'executed': True,
                'execution_time': datetime.now()
            }
            await signal_repo.store_trading_signal(signal_data)
            
            logger.info(f"Executed {side} order for {signal.symbol}: {quantity} @ {signal.entry_price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute signal for {signal.symbol}: {e}")
            await log_repo.log_system_event("ERROR", "strategy", f"Signal execution failed: {e}")
            return False
    
    async def monitor_positions(self):
        """Monitor existing positions for exit signals"""
        try:
            positions_to_close = []
            
            for symbol, position in self.current_positions.items():
                current_price = await self.binance_client.get_ticker_price(symbol)
                
                # Check stop loss and take profit
                should_close = False
                close_reason = ""
                
                if position['side'] == "BUY":
                    if position['stop_loss'] and current_price <= position['stop_loss']:
                        should_close = True
                        close_reason = "Stop loss hit"
                    elif position['take_profit'] and current_price >= position['take_profit']:
                        should_close = True
                        close_reason = "Take profit hit"
                else:  # SELL
                    if position['stop_loss'] and current_price >= position['stop_loss']:
                        should_close = True
                        close_reason = "Stop loss hit"
                    elif position['take_profit'] and current_price <= position['take_profit']:
                        should_close = True
                        close_reason = "Take profit hit"
                
                # Check for exit signals from strategy
                if not should_close:
                    exit_signals = await self.generate_signals(symbol)
                    for signal in exit_signals:
                        if signal.signal_type == SignalType.SELL and position['side'] == "BUY":
                            should_close = True
                            close_reason = f"Exit signal: {signal.reasoning}"
                        elif signal.signal_type == SignalType.BUY and position['side'] == "SELL":
                            should_close = True
                            close_reason = f"Exit signal: {signal.reasoning}"
                
                if should_close:
                    positions_to_close.append((symbol, close_reason))
            
            # Close positions
            for symbol, reason in positions_to_close:
                await self._close_position(symbol, reason)
                
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    async def _close_position(self, symbol: str, reason: str):
        """Close a position"""
        try:
            position = self.current_positions[symbol]
            
            # Place opposite order to close
            close_side = "SELL" if position['side'] == "BUY" else "BUY"
            
            order = await self.binance_client.place_order(
                symbol=symbol,
                side=close_side,
                order_type="MARKET",
                quantity=position['quantity']
            )
            
            # Calculate P&L
            current_price = await self.binance_client.get_ticker_price(symbol)
            if position['side'] == "BUY":
                pnl = (current_price - position['entry_price']) * position['quantity']
            else:
                pnl = (position['entry_price'] - current_price) * position['quantity']
            
            # Record trade
            trade_record = {
                'symbol': symbol,
                'side': position['side'],
                'entry_price': position['entry_price'],
                'exit_price': current_price,
                'quantity': position['quantity'],
                'pnl': pnl,
                'reason': reason,
                'timestamp': datetime.now(),
                'reasoning': position['reasoning']
            }
            
            self.performance_history.append(trade_record)
            
            # Remove from current positions
            del self.current_positions[symbol]
            
            logger.info(f"Closed position for {symbol}: P&L = {pnl:.2f} USDT, Reason: {reason}")
            
            # Store trade in memory
            await self.memory_client.store_trade_record(trade_record)
            
        except Exception as e:
            logger.error(f"Failed to close position for {symbol}: {e}")
    
    async def evolve_strategy(self):
        """Evolve strategy parameters based on performance analysis"""
        try:
            # Check if it's time for analysis
            time_since_analysis = datetime.now() - self.last_analysis_time
            if time_since_analysis.total_seconds() < trading_config.llm_analysis_frequency:
                return
            
            logger.info("Starting strategy evolution analysis...")
            
            # Analyze recent performance
            analysis_result = await self.strategy_analyzer.analyze_performance(
                self.performance_history,
                self.parameters
            )
            
            if analysis_result and analysis_result.get('should_evolve'):
                # Update strategy parameters
                new_params = analysis_result.get('new_parameters', {})
                for key, value in new_params.items():
                    if hasattr(self.parameters, key):
                        setattr(self.parameters, key, value)
                
                # Store updated parameters in memory
                await self.memory_client.store_strategy_parameters(
                    self.parameters.__dict__,
                    analysis_result.get('reasoning', '')
                )
                
                logger.info(f"Strategy evolved: {analysis_result.get('reasoning', '')}")
            
            self.last_analysis_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to evolve strategy: {e}")
    
    async def get_performance_summary(self) -> Dict:
        """Get performance summary for reporting"""
        try:
            if not self.performance_history:
                return {'total_trades': 0, 'total_pnl': 0.0, 'win_rate': 0.0}
            
            total_trades = len(self.performance_history)
            total_pnl = sum(trade['pnl'] for trade in self.performance_history)
            winning_trades = sum(1 for trade in self.performance_history if trade['pnl'] > 0)
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # Calculate additional metrics
            pnl_values = [trade['pnl'] for trade in self.performance_history]
            avg_win = np.mean([pnl for pnl in pnl_values if pnl > 0]) if any(pnl > 0 for pnl in pnl_values) else 0
            avg_loss = np.mean([pnl for pnl in pnl_values if pnl < 0]) if any(pnl < 0 for pnl in pnl_values) else 0
            
            return {
                'total_trades': total_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
                'current_positions': len(self.current_positions),
                'strategy_parameters': self.parameters.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}