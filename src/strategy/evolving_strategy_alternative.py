"""
Alternative version of evolving strategy that works with restricted locations
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
from src.data.alternative_data_client import AlternativeDataClient
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
    
    # Volume parameters
    volume_ma_period: int = 20
    
    # Risk parameters
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    
    # Signal parameters
    min_signal_confidence: float = 0.6

class AlternativeEvolvingStrategy:
    """Alternative evolving strategy that works with restricted locations"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.data_client = AlternativeDataClient()
        self.parameters = StrategyParameters()
        self.market_data = {}
        
    async def update_market_data(self, symbol: str) -> pd.DataFrame:
        """Update market data for a symbol"""
        try:
            # Get historical data
            df = await self.data_client.get_historical_data(symbol, '1h', 1000)
            
            if df.empty:
                logger.warning(f"No data available for {symbol}")
                return pd.DataFrame()
            
            # Add technical indicators
            df = self._add_technical_indicators(df)
            
            # Store the data
            self.market_data[symbol] = df
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to update market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        try:
            if df.empty:
                return df
            
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=self.parameters.rsi_period).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'], window=self.parameters.bb_period, window_dev=self.parameters.bb_std)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            
            # EMAs
            df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=self.parameters.ema_fast).ema_indicator()
            df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=self.parameters.ema_slow).ema_indicator()
            
            # Volume indicators
            df = df.copy()  # Fix SettingWithCopyWarning
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
            current_price = await self.data_client.get_ticker_price(symbol)
            
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
        
        signal['confidence'] = confidence
        signal['reasoning'] = "; ".join(reasoning_parts) if reasoning_parts else "No momentum signals"
        
        return signal
    
    def _mean_reversion_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Mean reversion trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        # Bollinger Bands
        bb_upper = data['bb_upper']
        bb_lower = data['bb_lower']
        bb_middle = data['bb_middle']
        
        if pd.isna(bb_upper) or pd.isna(bb_lower):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # Price position relative to bands
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        if bb_position < 0.2:  # Near lower band
            confidence += 0.5
            reasoning_parts.append("Price near lower Bollinger Band")
        elif bb_position > 0.8:  # Near upper band
            confidence += 0.5
            reasoning_parts.append("Price near upper Bollinger Band")
        
        # RSI confirmation
        rsi = data['rsi']
        if not pd.isna(rsi):
            if bb_position < 0.2 and rsi < 40:
                confidence += 0.3
                reasoning_parts.append("RSI confirms oversold")
            elif bb_position > 0.8 and rsi > 60:
                confidence += 0.3
                reasoning_parts.append("RSI confirms overbought")
        
        if confidence > 0.6:
            if bb_position < 0.2:
                signal['signal'] = SignalType.BUY
            else:
                signal['signal'] = SignalType.SELL
        
        signal['confidence'] = confidence
        signal['reasoning'] = "; ".join(reasoning_parts) if reasoning_parts else "No mean reversion signals"
        
        return signal
    
    def _trend_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Trend-following trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        # EMA signals
        ema_fast = data['ema_fast']
        ema_slow = data['ema_slow']
        
        if pd.isna(ema_fast) or pd.isna(ema_slow):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # EMA crossover
        if ema_fast > ema_slow:
            confidence += 0.4
            reasoning_parts.append("EMA fast above slow (bullish)")
        else:
            confidence += 0.4
            reasoning_parts.append("EMA fast below slow (bearish)")
        
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
            else:
                signal['signal'] = SignalType.SELL
        
        signal['confidence'] = confidence
        signal['reasoning'] = "; ".join(reasoning_parts) if reasoning_parts else "No trend signals"
        
        return signal
    
    def _volume_strategy(self, data: pd.Series, current_price: float) -> Dict:
        """Volume-based trading strategy"""
        signal = {'signal': SignalType.HOLD, 'confidence': 0.0, 'reasoning': ''}
        
        # Volume analysis
        volume_ratio = data['volume_ratio']
        
        if pd.isna(volume_ratio):
            return signal
        
        confidence = 0.0
        reasoning_parts = []
        
        # High volume confirmation
        if volume_ratio > 1.5:
            confidence += 0.4
            reasoning_parts.append(f"High volume ({volume_ratio:.1f}x average)")
        elif volume_ratio < 0.5:
            confidence += 0.2
            reasoning_parts.append(f"Low volume ({volume_ratio:.1f}x average)")
        
        # Volume trend
        if volume_ratio > 2.0:
            confidence += 0.3
            reasoning_parts.append("Very high volume - potential breakout")
        
        signal['confidence'] = confidence
        signal['reasoning'] = "; ".join(reasoning_parts) if reasoning_parts else "No volume signals"
        
        return signal
    
    def _combine_signals(self, momentum: Dict, mean_reversion: Dict, 
                        trend: Dict, volume: Dict) -> Dict:
        """Combine multiple signals into a final decision"""
        
        # Weight the signals
        weights = {
            'momentum': 0.3,
            'mean_reversion': 0.25,
            'trend': 0.3,
            'volume': 0.15
        }
        
        # Calculate weighted confidence
        total_confidence = 0.0
        buy_votes = 0
        sell_votes = 0
        reasoning_parts = []
        
        for signal_name, signal_data in [('momentum', momentum), ('mean_reversion', mean_reversion),
                                       ('trend', trend), ('volume', volume)]:
            if signal_data['signal'] != SignalType.HOLD:
                weight = weights[signal_name]
                confidence = signal_data['confidence'] * weight
                total_confidence += confidence
                
                if signal_data['signal'] == SignalType.BUY:
                    buy_votes += confidence
                else:
                    sell_votes += confidence
                
                if signal_data['reasoning']:
                    reasoning_parts.append(f"{signal_name.title()}: {signal_data['reasoning']}")
        
        # Determine final signal
        if total_confidence < self.parameters.min_signal_confidence:
            final_signal = SignalType.HOLD
        elif buy_votes > sell_votes:
            final_signal = SignalType.BUY
        else:
            final_signal = SignalType.SELL
        
        # Calculate position size
        position_size = min(total_confidence * self.parameters.max_position_size, 
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
            'confidence': total_confidence,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': "; ".join(reasoning_parts) if reasoning_parts else "No clear signals"
        }