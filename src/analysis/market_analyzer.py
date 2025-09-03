"""
Market data analysis pipeline for pattern recognition and regime detection
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

# Optional sklearn imports - will use dummy classes if not available
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Create dummy classes for when sklearn is not available
    class StandardScaler:
        def fit_transform(self, X):
            return X
        def transform(self, X):
            return X
        def fit(self, X):
            return self
    
    class KMeans:
        def __init__(self, n_clusters=3):
            self.n_clusters = n_clusters
        def fit(self, X):
            return self
        def predict(self, X):
            return [0] * len(X)
    
    class PCA:
        def __init__(self, n_components=2):
            self.n_components = n_components
        def fit_transform(self, X):
            return X[:, :self.n_components] if X.shape[1] > self.n_components else X

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"

@dataclass
class MarketPattern:
    """Market pattern detection result"""
    pattern_type: str
    confidence: float
    description: str
    entry_conditions: List[str]
    exit_conditions: List[str]
    historical_success_rate: float
    timestamp: datetime

@dataclass
class MarketRegimeAnalysis:
    """Market regime analysis result"""
    regime: MarketRegime
    confidence: float
    volatility_level: float
    trend_strength: float
    volume_profile: str
    support_resistance_levels: List[float]
    recommendations: List[str]

class MarketAnalyzer:
    """
    Advanced market analysis for pattern recognition and regime detection
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=5)
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.pattern_database: Dict[str, List[Dict]] = {}
        
    async def analyze_market_data(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        try:
            if df.empty or len(df) < 50:
                return {}
            
            # Calculate technical indicators
            df = self._calculate_advanced_indicators(df)
            
            # Detect market regime
            regime_analysis = self._detect_market_regime(df)
            
            # Identify patterns
            patterns = self._identify_patterns(df, symbol)
            
            # Analyze volatility
            volatility_analysis = self._analyze_volatility(df)
            
            # Analyze volume profile
            volume_analysis = self._analyze_volume_profile(df)
            
            # Support and resistance levels
            support_resistance = self._find_support_resistance(df)
            
            # Market sentiment indicators
            sentiment_indicators = self._calculate_sentiment_indicators(df)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'regime_analysis': regime_analysis,
                'patterns': patterns,
                'volatility_analysis': volatility_analysis,
                'volume_analysis': volume_analysis,
                'support_resistance': support_resistance,
                'sentiment_indicators': sentiment_indicators,
                'technical_indicators': self._get_latest_indicators(df)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze market data for {symbol}: {e}")
            return {}
    
    def _calculate_advanced_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced technical indicators"""
        try:
            # Basic indicators
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            df['macd'] = ta.trend.MACD(df['close']).macd()
            df['macd_signal'] = ta.trend.MACD(df['close']).macd_signal()
            df['macd_histogram'] = ta.trend.MACD(df['close']).macd_diff()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lower()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Moving averages
            df['ema_9'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
            df['ema_21'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
            df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
            df['sma_200'] = ta.trend.SMAIndicator(df['close'], window=200).sma_indicator()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            
            # Volatility indicators
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            df['volatility'] = df['close'].pct_change().rolling(window=20).std()
            
            # Momentum indicators
            df['stoch'] = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close']).stoch()
            df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
            
            # Trend indicators
            df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
            df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
            
            # Price action indicators
            df['price_change'] = df['close'].pct_change()
            df['price_change_5'] = df['close'].pct_change(5)
            df['price_change_10'] = df['close'].pct_change(10)
            df['price_change_20'] = df['close'].pct_change(20)
            
            # Support/Resistance levels
            df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
            df['resistance_1'] = 2 * df['pivot'] - df['low']
            df['support_1'] = 2 * df['pivot'] - df['high']
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to calculate advanced indicators: {e}")
            return df
    
    def _detect_market_regime(self, df: pd.DataFrame) -> MarketRegimeAnalysis:
        """Detect current market regime"""
        try:
            latest = df.iloc[-1]
            recent_20 = df.tail(20)
            
            # Calculate regime indicators
            volatility = recent_20['volatility'].mean()
            trend_strength = abs(latest['adx']) if not pd.isna(latest['adx']) else 0
            
            # Price trend analysis
            price_change_20 = (latest['close'] - recent_20['close'].iloc[0]) / recent_20['close'].iloc[0]
            ema_trend = latest['ema_9'] > latest['ema_21'] > latest['ema_50'] if not pd.isna(latest['ema_9']) else False
            
            # Volume analysis
            avg_volume_ratio = recent_20['volume_ratio'].mean()
            
            # Determine regime
            regime = MarketRegime.RANGING
            confidence = 0.5
            
            if volatility > 0.03:  # High volatility threshold
                regime = MarketRegime.HIGH_VOLATILITY
                confidence = 0.8
            elif volatility < 0.01:  # Low volatility threshold
                regime = MarketRegime.LOW_VOLATILITY
                confidence = 0.7
            elif trend_strength > 25 and price_change_20 > 0.05:
                regime = MarketRegime.TRENDING_UP
                confidence = 0.8
            elif trend_strength > 25 and price_change_20 < -0.05:
                regime = MarketRegime.TRENDING_DOWN
                confidence = 0.8
            elif abs(price_change_20) < 0.02:
                regime = MarketRegime.RANGING
                confidence = 0.7
            
            # Generate recommendations
            recommendations = self._generate_regime_recommendations(regime, volatility, trend_strength)
            
            return MarketRegimeAnalysis(
                regime=regime,
                confidence=confidence,
                volatility_level=volatility,
                trend_strength=trend_strength,
                volume_profile="high" if avg_volume_ratio > 1.5 else "normal" if avg_volume_ratio > 0.8 else "low",
                support_resistance_levels=self._find_support_resistance(df),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to detect market regime: {e}")
            return MarketRegimeAnalysis(
                regime=MarketRegime.RANGING,
                confidence=0.5,
                volatility_level=0.02,
                trend_strength=0,
                volume_profile="normal",
                support_resistance_levels=[],
                recommendations=["Monitor market conditions"]
            )
    
    def _identify_patterns(self, df: pd.DataFrame, symbol: str) -> List[MarketPattern]:
        """Identify trading patterns in market data"""
        patterns = []
        
        try:
            # Head and Shoulders
            hs_pattern = self._detect_head_shoulders(df)
            if hs_pattern:
                patterns.append(hs_pattern)
            
            # Double Top/Bottom
            dt_pattern = self._detect_double_top_bottom(df)
            if dt_pattern:
                patterns.append(dt_pattern)
            
            # Triangle patterns
            triangle_pattern = self._detect_triangle(df)
            if triangle_pattern:
                patterns.append(triangle_pattern)
            
            # Flag patterns
            flag_pattern = self._detect_flag(df)
            if flag_pattern:
                patterns.append(flag_pattern)
            
            # Breakout patterns
            breakout_pattern = self._detect_breakout(df)
            if breakout_pattern:
                patterns.append(breakout_pattern)
            
            # Store patterns in database
            if symbol not in self.pattern_database:
                self.pattern_database[symbol] = []
            
            for pattern in patterns:
                self.pattern_database[symbol].append({
                    'pattern_type': pattern.pattern_type,
                    'timestamp': pattern.timestamp,
                    'confidence': pattern.confidence
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to identify patterns: {e}")
            return []
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> Optional[MarketPattern]:
        """Detect head and shoulders pattern"""
        try:
            if len(df) < 50:
                return None
            
            # Look for three peaks with middle peak higher
            highs = df['high'].rolling(window=5, center=True).max()
            peaks = df[df['high'] == highs]['high'].tail(10)
            
            if len(peaks) >= 3:
                peak_values = peaks.values[-3:]
                if peak_values[1] > peak_values[0] and peak_values[1] > peak_values[2]:
                    confidence = 0.7
                    return MarketPattern(
                        pattern_type="head_shoulders",
                        confidence=confidence,
                        description="Head and Shoulders pattern detected",
                        entry_conditions=["Price breaks neckline", "Volume confirmation"],
                        exit_conditions=["Target reached", "Stop loss hit"],
                        historical_success_rate=0.65,
                        timestamp=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect head and shoulders: {e}")
            return None
    
    def _detect_double_top_bottom(self, df: pd.DataFrame) -> Optional[MarketPattern]:
        """Detect double top or double bottom pattern"""
        try:
            if len(df) < 30:
                return None
            
            recent_highs = df['high'].tail(20)
            recent_lows = df['low'].tail(20)
            
            # Check for double top
            max_high = recent_highs.max()
            high_count = (recent_highs >= max_high * 0.98).sum()
            
            if high_count >= 2:
                return MarketPattern(
                    pattern_type="double_top",
                    confidence=0.6,
                    description="Double Top pattern detected",
                    entry_conditions=["Price breaks support", "Volume confirmation"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.60,
                    timestamp=datetime.now()
                )
            
            # Check for double bottom
            min_low = recent_lows.min()
            low_count = (recent_lows <= min_low * 1.02).sum()
            
            if low_count >= 2:
                return MarketPattern(
                    pattern_type="double_bottom",
                    confidence=0.6,
                    description="Double Bottom pattern detected",
                    entry_conditions=["Price breaks resistance", "Volume confirmation"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.60,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect double top/bottom: {e}")
            return None
    
    def _detect_triangle(self, df: pd.DataFrame) -> Optional[MarketPattern]:
        """Detect triangle patterns"""
        try:
            if len(df) < 20:
                return None
            
            recent_data = df.tail(20)
            
            # Calculate trend lines
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Simple triangle detection based on converging highs and lows
            high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
            low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
            
            # Symmetrical triangle
            if abs(high_slope) < 0.1 and abs(low_slope) < 0.1:
                return MarketPattern(
                    pattern_type="symmetrical_triangle",
                    confidence=0.5,
                    description="Symmetrical Triangle pattern detected",
                    entry_conditions=["Price breaks triangle", "Volume confirmation"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.55,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect triangle: {e}")
            return None
    
    def _detect_flag(self, df: pd.DataFrame) -> Optional[MarketPattern]:
        """Detect flag patterns"""
        try:
            if len(df) < 15:
                return None
            
            recent_data = df.tail(15)
            
            # Flag detection based on consolidation after strong move
            price_range = recent_data['high'].max() - recent_data['low'].min()
            avg_price = recent_data['close'].mean()
            
            if price_range / avg_price < 0.03:  # Tight consolidation
                return MarketPattern(
                    pattern_type="flag",
                    confidence=0.6,
                    description="Flag pattern detected",
                    entry_conditions=["Price breaks flag", "Volume confirmation"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.70,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect flag: {e}")
            return None
    
    def _detect_breakout(self, df: pd.DataFrame) -> Optional[MarketPattern]:
        """Detect breakout patterns"""
        try:
            if len(df) < 20:
                return None
            
            latest = df.iloc[-1]
            recent_20 = df.tail(20)
            
            # Check for volume breakout
            volume_ratio = latest['volume_ratio'] if not pd.isna(latest['volume_ratio']) else 1
            
            # Check for price breakout
            resistance = recent_20['high'].max()
            support = recent_20['low'].min()
            
            if latest['close'] > resistance and volume_ratio > 1.5:
                return MarketPattern(
                    pattern_type="bullish_breakout",
                    confidence=0.7,
                    description="Bullish Breakout pattern detected",
                    entry_conditions=["Price above resistance", "High volume"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.65,
                    timestamp=datetime.now()
                )
            elif latest['close'] < support and volume_ratio > 1.5:
                return MarketPattern(
                    pattern_type="bearish_breakout",
                    confidence=0.7,
                    description="Bearish Breakout pattern detected",
                    entry_conditions=["Price below support", "High volume"],
                    exit_conditions=["Target reached", "Stop loss hit"],
                    historical_success_rate=0.65,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect breakout: {e}")
            return None
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market volatility"""
        try:
            recent_20 = df.tail(20)
            
            # Current volatility
            current_vol = recent_20['volatility'].iloc[-1] if not pd.isna(recent_20['volatility'].iloc[-1]) else 0
            
            # Average volatility
            avg_vol = recent_20['volatility'].mean()
            
            # Volatility trend
            vol_trend = "increasing" if current_vol > avg_vol * 1.2 else "decreasing" if current_vol < avg_vol * 0.8 else "stable"
            
            # ATR analysis
            atr = recent_20['atr'].iloc[-1] if not pd.isna(recent_20['atr'].iloc[-1]) else 0
            avg_atr = recent_20['atr'].mean()
            
            return {
                'current_volatility': current_vol,
                'average_volatility': avg_vol,
                'volatility_trend': vol_trend,
                'atr': atr,
                'atr_percentage': (atr / recent_20['close'].iloc[-1]) * 100,
                'volatility_regime': "high" if current_vol > avg_vol * 1.5 else "low" if current_vol < avg_vol * 0.5 else "normal"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze volatility: {e}")
            return {}
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume profile"""
        try:
            recent_20 = df.tail(20)
            
            # Volume statistics
            avg_volume = recent_20['volume'].mean()
            current_volume = recent_20['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume trend
            volume_trend = "increasing" if volume_ratio > 1.2 else "decreasing" if volume_ratio < 0.8 else "stable"
            
            # OBV analysis
            obv_trend = "bullish" if recent_20['obv'].iloc[-1] > recent_20['obv'].iloc[-5] else "bearish"
            
            return {
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'volume_trend': volume_trend,
                'obv_trend': obv_trend,
                'volume_regime': "high" if volume_ratio > 2.0 else "low" if volume_ratio < 0.5 else "normal"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze volume profile: {e}")
            return {}
    
    def _find_support_resistance(self, df: pd.DataFrame) -> List[float]:
        """Find key support and resistance levels"""
        try:
            if len(df) < 50:
                return []
            
            # Use recent data for levels
            recent_data = df.tail(50)
            
            # Find pivot points
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Simple support/resistance detection
            levels = []
            
            # Resistance levels (recent highs)
            resistance_levels = highs.nlargest(3).tolist()
            levels.extend(resistance_levels)
            
            # Support levels (recent lows)
            support_levels = lows.nsmallest(3).tolist()
            levels.extend(support_levels)
            
            # Remove duplicates and sort
            levels = sorted(list(set(levels)))
            
            return levels
            
        except Exception as e:
            logger.error(f"Failed to find support/resistance: {e}")
            return []
    
    def _calculate_sentiment_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate market sentiment indicators"""
        try:
            latest = df.iloc[-1]
            recent_10 = df.tail(10)
            
            # RSI sentiment
            rsi = latest['rsi'] if not pd.isna(latest['rsi']) else 50
            rsi_sentiment = "bullish" if rsi > 60 else "bearish" if rsi < 40 else "neutral"
            
            # MACD sentiment
            macd = latest['macd'] if not pd.isna(latest['macd']) else 0
            macd_signal = latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0
            macd_sentiment = "bullish" if macd > macd_signal else "bearish"
            
            # Price momentum sentiment
            price_change_5 = recent_10['close'].pct_change(5).iloc[-1] if not pd.isna(recent_10['close'].pct_change(5).iloc[-1]) else 0
            momentum_sentiment = "bullish" if price_change_5 > 0.02 else "bearish" if price_change_5 < -0.02 else "neutral"
            
            # Overall sentiment score
            sentiment_score = 0
            if rsi_sentiment == "bullish":
                sentiment_score += 1
            elif rsi_sentiment == "bearish":
                sentiment_score -= 1
            
            if macd_sentiment == "bullish":
                sentiment_score += 1
            else:
                sentiment_score -= 1
            
            if momentum_sentiment == "bullish":
                sentiment_score += 1
            elif momentum_sentiment == "bearish":
                sentiment_score -= 1
            
            overall_sentiment = "bullish" if sentiment_score > 0 else "bearish" if sentiment_score < 0 else "neutral"
            
            return {
                'rsi_sentiment': rsi_sentiment,
                'macd_sentiment': macd_sentiment,
                'momentum_sentiment': momentum_sentiment,
                'overall_sentiment': overall_sentiment,
                'sentiment_score': sentiment_score,
                'rsi': rsi,
                'macd': macd,
                'price_change_5': price_change_5
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate sentiment indicators: {e}")
            return {}
    
    def _get_latest_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get latest technical indicator values"""
        try:
            latest = df.iloc[-1]
            
            indicators = {}
            for col in ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'bb_middle', 
                       'ema_9', 'ema_21', 'ema_50', 'atr', 'volatility', 'adx', 'cci']:
                if col in latest and not pd.isna(latest[col]):
                    indicators[col] = float(latest[col])
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get latest indicators: {e}")
            return {}
    
    def _generate_regime_recommendations(self, regime: MarketRegime, 
                                       volatility: float, trend_strength: float) -> List[str]:
        """Generate recommendations based on market regime"""
        recommendations = []
        
        if regime == MarketRegime.TRENDING_UP:
            recommendations.extend([
                "Follow the trend with momentum strategies",
                "Use pullbacks as entry opportunities",
                "Set wider stop losses to avoid whipsaws"
            ])
        elif regime == MarketRegime.TRENDING_DOWN:
            recommendations.extend([
                "Consider short positions or avoid long positions",
                "Use rallies as exit opportunities",
                "Implement strict risk management"
            ])
        elif regime == MarketRegime.HIGH_VOLATILITY:
            recommendations.extend([
                "Reduce position sizes",
                "Use wider stop losses",
                "Consider volatility-based strategies"
            ])
        elif regime == MarketRegime.LOW_VOLATILITY:
            recommendations.extend([
                "Prepare for potential breakout",
                "Use range-bound strategies",
                "Monitor for volatility expansion"
            ])
        elif regime == MarketRegime.RANGING:
            recommendations.extend([
                "Use mean reversion strategies",
                "Buy support, sell resistance",
                "Avoid trend-following strategies"
            ])
        
        return recommendations