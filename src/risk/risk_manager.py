"""
Advanced risk management system for EvolvingTrader
"""
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

from config import trading_config

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    """Risk metrics for portfolio assessment"""
    portfolio_value: float
    total_exposure: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: float
    max_position_size: float
    correlation_risk: float
    concentration_risk: float
    liquidity_risk: float

@dataclass
class RiskAssessment:
    """Risk assessment result"""
    risk_level: RiskLevel
    risk_score: float  # 0-100
    warnings: List[str]
    recommendations: List[str]
    position_adjustments: Dict[str, float]
    max_new_position_size: float

class RiskManager:
    """
    Advanced risk management system with dynamic position sizing and portfolio protection
    """
    
    def __init__(self):
        self.max_portfolio_risk = trading_config.max_daily_loss
        self.max_position_risk = trading_config.risk_per_trade
        self.max_position_size = trading_config.max_position_size
        
        # Risk tracking
        self.daily_pnl_history: List[float] = []
        self.position_history: List[Dict] = []
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        # Risk limits
        self.max_daily_loss = trading_config.max_daily_loss
        self.max_consecutive_losses = 5
        self.max_correlation_exposure = 0.7
        self.max_portfolio_volatility = 0.15
        
    async def assess_trade_risk(self, symbol: str, signal_type: str, 
                              proposed_size: float, current_price: float,
                              portfolio_value: float) -> RiskAssessment:
        """Assess risk for a proposed trade"""
        try:
            # Calculate current portfolio metrics
            portfolio_metrics = await self._calculate_portfolio_metrics(portfolio_value)
            
            # Check individual trade risk
            trade_risk = self._assess_individual_trade_risk(
                symbol, signal_type, proposed_size, current_price, portfolio_value
            )
            
            # Check portfolio-level risk
            portfolio_risk = self._assess_portfolio_risk(portfolio_metrics)
            
            # Check correlation risk
            correlation_risk = self._assess_correlation_risk(symbol, proposed_size)
            
            # Check concentration risk
            concentration_risk = self._assess_concentration_risk(symbol, proposed_size, portfolio_value)
            
            # Check drawdown risk
            drawdown_risk = self._assess_drawdown_risk()
            
            # Combine risk assessments
            risk_score = self._calculate_combined_risk_score(
                trade_risk, portfolio_risk, correlation_risk, 
                concentration_risk, drawdown_risk
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate warnings and recommendations
            warnings, recommendations = self._generate_risk_guidance(
                risk_level, trade_risk, portfolio_risk, correlation_risk,
                concentration_risk, drawdown_risk
            )
            
            # Calculate position adjustments
            position_adjustments = self._calculate_position_adjustments(
                risk_level, proposed_size, portfolio_metrics
            )
            
            # Calculate maximum new position size
            max_new_position_size = self._calculate_max_position_size(
                risk_level, portfolio_metrics
            )
            
            return RiskAssessment(
                risk_level=risk_level,
                risk_score=risk_score,
                warnings=warnings,
                recommendations=recommendations,
                position_adjustments=position_adjustments,
                max_new_position_size=max_new_position_size
            )
            
        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
            return self._create_high_risk_assessment("Error in risk assessment")
    
    def _assess_individual_trade_risk(self, symbol: str, signal_type: str,
                                    proposed_size: float, current_price: float,
                                    portfolio_value: float) -> Dict[str, Any]:
        """Assess risk for individual trade"""
        try:
            # Position size as percentage of portfolio
            position_pct = (proposed_size * current_price) / portfolio_value
            
            # Risk per trade
            risk_per_trade = position_pct * 0.02  # Assuming 2% stop loss
            
            # Volatility risk (simplified)
            volatility_risk = min(position_pct * 0.1, 0.05)  # Assume 10% volatility
            
            # Liquidity risk (simplified - would need real market data)
            liquidity_risk = 0.01 if position_pct > 0.05 else 0.005
            
            return {
                'position_pct': position_pct,
                'risk_per_trade': risk_per_trade,
                'volatility_risk': volatility_risk,
                'liquidity_risk': liquidity_risk,
                'within_limits': position_pct <= self.max_position_size and risk_per_trade <= self.max_position_risk
            }
            
        except Exception as e:
            logger.error(f"Error assessing individual trade risk: {e}")
            return {'within_limits': False}
    
    def _assess_portfolio_risk(self, portfolio_metrics: RiskMetrics) -> Dict[str, Any]:
        """Assess portfolio-level risk"""
        try:
            # Total exposure risk
            exposure_risk = portfolio_metrics.total_exposure / portfolio_metrics.portfolio_value
            
            # Drawdown risk
            drawdown_risk = portfolio_metrics.max_drawdown / portfolio_metrics.portfolio_value
            
            # Volatility risk
            volatility_risk = portfolio_metrics.portfolio_value * 0.1  # Simplified
            
            # Concentration risk
            concentration_risk = portfolio_metrics.concentration_risk
            
            return {
                'exposure_risk': exposure_risk,
                'drawdown_risk': drawdown_risk,
                'volatility_risk': volatility_risk,
                'concentration_risk': concentration_risk,
                'within_limits': (exposure_risk <= 1.0 and 
                                drawdown_risk <= self.max_daily_loss and
                                concentration_risk <= 0.3)
            }
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            return {'within_limits': False}
    
    def _assess_correlation_risk(self, symbol: str, proposed_size: float) -> Dict[str, Any]:
        """Assess correlation risk"""
        try:
            # Simplified correlation assessment
            # In production, this would use real correlation data
            
            correlation_risk = 0.0
            if symbol in self.correlation_matrix:
                correlations = self.correlation_matrix[symbol]
                high_correlation_count = sum(1 for corr in correlations.values() if abs(corr) > 0.7)
                correlation_risk = min(high_correlation_count * 0.1, 0.5)
            
            return {
                'correlation_risk': correlation_risk,
                'within_limits': correlation_risk <= self.max_correlation_exposure
            }
            
        except Exception as e:
            logger.error(f"Error assessing correlation risk: {e}")
            return {'within_limits': False}
    
    def _assess_concentration_risk(self, symbol: str, proposed_size: float, 
                                 portfolio_value: float) -> Dict[str, Any]:
        """Assess concentration risk"""
        try:
            # Calculate current concentration
            current_concentration = 0.0
            if self.position_history:
                for position in self.position_history:
                    if position['symbol'] == symbol:
                        current_concentration += position['size'] * position['price'] / portfolio_value
            
            # Add proposed position
            new_concentration = current_concentration + (proposed_size * 1.0 / portfolio_value)  # Simplified price
            
            concentration_risk = min(new_concentration, 1.0)
            
            return {
                'concentration_risk': concentration_risk,
                'within_limits': concentration_risk <= 0.2  # Max 20% in single asset
            }
            
        except Exception as e:
            logger.error(f"Error assessing concentration risk: {e}")
            return {'within_limits': False}
    
    def _assess_drawdown_risk(self) -> Dict[str, Any]:
        """Assess drawdown risk"""
        try:
            if len(self.daily_pnl_history) < 5:
                return {'within_limits': True, 'drawdown_risk': 0.0}
            
            # Calculate recent drawdown
            recent_pnl = self.daily_pnl_history[-5:]
            cumulative_pnl = np.cumsum(recent_pnl)
            max_drawdown = np.max(cumulative_pnl) - np.min(cumulative_pnl)
            
            # Check consecutive losses
            consecutive_losses = 0
            for pnl in reversed(recent_pnl):
                if pnl < 0:
                    consecutive_losses += 1
                else:
                    break
            
            drawdown_risk = max_drawdown / 1000.0  # Normalized to portfolio size
            
            return {
                'drawdown_risk': drawdown_risk,
                'consecutive_losses': consecutive_losses,
                'within_limits': (drawdown_risk <= self.max_daily_loss and 
                                consecutive_losses < self.max_consecutive_losses)
            }
            
        except Exception as e:
            logger.error(f"Error assessing drawdown risk: {e}")
            return {'within_limits': False}
    
    def _calculate_combined_risk_score(self, trade_risk: Dict, portfolio_risk: Dict,
                                     correlation_risk: Dict, concentration_risk: Dict,
                                     drawdown_risk: Dict) -> float:
        """Calculate combined risk score (0-100)"""
        try:
            score = 0.0
            
            # Individual trade risk (30% weight)
            if not trade_risk.get('within_limits', True):
                score += 30
            
            # Portfolio risk (25% weight)
            if not portfolio_risk.get('within_limits', True):
                score += 25
            
            # Correlation risk (20% weight)
            if not correlation_risk.get('within_limits', True):
                score += 20
            
            # Concentration risk (15% weight)
            if not concentration_risk.get('within_limits', True):
                score += 15
            
            # Drawdown risk (10% weight)
            if not drawdown_risk.get('within_limits', True):
                score += 10
            
            # Add risk magnitude adjustments
            score += trade_risk.get('risk_per_trade', 0) * 100
            score += portfolio_risk.get('exposure_risk', 0) * 50
            score += correlation_risk.get('correlation_risk', 0) * 100
            score += concentration_risk.get('concentration_risk', 0) * 100
            score += drawdown_risk.get('drawdown_risk', 0) * 100
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating combined risk score: {e}")
            return 100.0
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_risk_guidance(self, risk_level: RiskLevel, trade_risk: Dict,
                              portfolio_risk: Dict, correlation_risk: Dict,
                              concentration_risk: Dict, drawdown_risk: Dict) -> Tuple[List[str], List[str]]:
        """Generate risk warnings and recommendations"""
        warnings = []
        recommendations = []
        
        # Risk level warnings
        if risk_level == RiskLevel.CRITICAL:
            warnings.append("CRITICAL RISK: Trade should be avoided")
            recommendations.append("Reduce position size or avoid trade entirely")
        elif risk_level == RiskLevel.HIGH:
            warnings.append("HIGH RISK: Significant risk detected")
            recommendations.append("Consider reducing position size")
        
        # Specific risk warnings
        if not trade_risk.get('within_limits', True):
            warnings.append("Position size exceeds individual trade limits")
            recommendations.append("Reduce position size to within risk limits")
        
        if not portfolio_risk.get('within_limits', True):
            warnings.append("Portfolio risk limits exceeded")
            recommendations.append("Reduce overall portfolio exposure")
        
        if not correlation_risk.get('within_limits', True):
            warnings.append("High correlation risk detected")
            recommendations.append("Diversify across uncorrelated assets")
        
        if not concentration_risk.get('within_limits', True):
            warnings.append("Concentration risk too high")
            recommendations.append("Reduce position size in this asset")
        
        if not drawdown_risk.get('within_limits', True):
            warnings.append("Drawdown risk detected")
            recommendations.append("Consider reducing risk or taking a break")
        
        return warnings, recommendations
    
    def _calculate_position_adjustments(self, risk_level: RiskLevel, 
                                      proposed_size: float, 
                                      portfolio_metrics: RiskMetrics) -> Dict[str, float]:
        """Calculate position size adjustments"""
        adjustments = {}
        
        if risk_level == RiskLevel.CRITICAL:
            adjustments['max_position_size'] = 0.0
        elif risk_level == RiskLevel.HIGH:
            adjustments['max_position_size'] = proposed_size * 0.5
        elif risk_level == RiskLevel.MEDIUM:
            adjustments['max_position_size'] = proposed_size * 0.75
        else:
            adjustments['max_position_size'] = proposed_size
        
        # Additional adjustments based on portfolio metrics
        if portfolio_metrics.max_drawdown > 0.05:  # 5% drawdown
            adjustments['max_position_size'] *= 0.5
        
        if portfolio_metrics.concentration_risk > 0.2:  # 20% concentration
            adjustments['max_position_size'] *= 0.7
        
        return adjustments
    
    def _calculate_max_position_size(self, risk_level: RiskLevel, 
                                   portfolio_metrics: RiskMetrics) -> float:
        """Calculate maximum new position size"""
        base_size = self.max_position_size
        
        # Adjust based on risk level
        if risk_level == RiskLevel.CRITICAL:
            return 0.0
        elif risk_level == RiskLevel.HIGH:
            base_size *= 0.3
        elif risk_level == RiskLevel.MEDIUM:
            base_size *= 0.6
        else:
            base_size *= 0.8
        
        # Adjust based on portfolio metrics
        if portfolio_metrics.max_drawdown > 0.03:  # 3% drawdown
            base_size *= 0.5
        
        if portfolio_metrics.concentration_risk > 0.15:  # 15% concentration
            base_size *= 0.7
        
        return base_size
    
    async def _calculate_portfolio_metrics(self, portfolio_value: float) -> RiskMetrics:
        """Calculate portfolio risk metrics"""
        try:
            # Calculate total exposure
            total_exposure = 0.0
            if self.position_history:
                for position in self.position_history:
                    total_exposure += position['size'] * position['price']
            
            # Calculate max drawdown
            max_drawdown = 0.0
            if self.daily_pnl_history:
                cumulative_pnl = np.cumsum(self.daily_pnl_history)
                running_max = np.maximum.accumulate(cumulative_pnl)
                drawdowns = running_max - cumulative_pnl
                max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
            
            # Calculate VaR (simplified)
            var_95 = 0.0
            if len(self.daily_pnl_history) > 10:
                var_95 = np.percentile(self.daily_pnl_history, 5)
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = 0.0
            if len(self.daily_pnl_history) > 10:
                mean_return = np.mean(self.daily_pnl_history)
                std_return = np.std(self.daily_pnl_history)
                sharpe_ratio = mean_return / std_return if std_return > 0 else 0
            
            # Calculate concentration risk
            concentration_risk = 0.0
            if self.position_history:
                position_values = [pos['size'] * pos['price'] for pos in self.position_history]
                if position_values:
                    max_position = max(position_values)
                    total_value = sum(position_values)
                    concentration_risk = max_position / total_value if total_value > 0 else 0
            
            # Calculate correlation risk (simplified)
            correlation_risk = 0.0
            if len(self.position_history) > 1:
                # Simplified correlation risk calculation
                correlation_risk = min(len(self.position_history) * 0.1, 0.5)
            
            # Calculate liquidity risk (simplified)
            liquidity_risk = 0.0
            if self.position_history:
                # Assume larger positions have higher liquidity risk
                total_size = sum(pos['size'] for pos in self.position_history)
                liquidity_risk = min(total_size / portfolio_value, 0.3)
            
            return RiskMetrics(
                portfolio_value=portfolio_value,
                total_exposure=total_exposure,
                max_drawdown=max_drawdown,
                var_95=var_95,
                sharpe_ratio=sharpe_ratio,
                max_position_size=self.max_position_size,
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk
            )
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return RiskMetrics(
                portfolio_value=portfolio_value,
                total_exposure=0.0,
                max_drawdown=0.0,
                var_95=0.0,
                sharpe_ratio=0.0,
                max_position_size=self.max_position_size,
                correlation_risk=0.0,
                concentration_risk=0.0,
                liquidity_risk=0.0
            )
    
    def _create_high_risk_assessment(self, reason: str) -> RiskAssessment:
        """Create high risk assessment"""
        return RiskAssessment(
            risk_level=RiskLevel.HIGH,
            risk_score=80.0,
            warnings=[reason],
            recommendations=["Avoid trade", "Review risk parameters"],
            position_adjustments={'max_position_size': 0.0},
            max_new_position_size=0.0
        )
    
    def update_position_history(self, symbol: str, size: float, price: float, side: str):
        """Update position history for risk tracking"""
        try:
            self.position_history.append({
                'symbol': symbol,
                'size': size,
                'price': price,
                'side': side,
                'timestamp': datetime.now()
            })
            
            # Keep only recent positions (last 100)
            if len(self.position_history) > 100:
                self.position_history = self.position_history[-100:]
                
        except Exception as e:
            logger.error(f"Error updating position history: {e}")
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L history"""
        try:
            self.daily_pnl_history.append(pnl)
            
            # Keep only recent history (last 30 days)
            if len(self.daily_pnl_history) > 30:
                self.daily_pnl_history = self.daily_pnl_history[-30:]
                
        except Exception as e:
            logger.error(f"Error updating daily P&L: {e}")
    
    def update_correlation_matrix(self, symbol: str, correlations: Dict[str, float]):
        """Update correlation matrix"""
        try:
            self.correlation_matrix[symbol] = correlations
        except Exception as e:
            logger.error(f"Error updating correlation matrix: {e}")
    
    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        try:
            # Calculate current portfolio metrics
            portfolio_value = 1000.0  # Default, should be passed from strategy
            portfolio_metrics = await self._calculate_portfolio_metrics(portfolio_value)
            
            # Calculate current risk score
            current_risk_score = 0.0
            if self.daily_pnl_history:
                recent_pnl = self.daily_pnl_history[-5:] if len(self.daily_pnl_history) >= 5 else self.daily_pnl_history
                if recent_pnl:
                    avg_pnl = np.mean(recent_pnl)
                    std_pnl = np.std(recent_pnl)
                    if std_pnl > 0:
                        current_risk_score = abs(avg_pnl) / std_pnl * 10
            
            return {
                'portfolio_metrics': {
                    'total_exposure': portfolio_metrics.total_exposure,
                    'max_drawdown': portfolio_metrics.max_drawdown,
                    'var_95': portfolio_metrics.var_95,
                    'sharpe_ratio': portfolio_metrics.sharpe_ratio,
                    'concentration_risk': portfolio_metrics.concentration_risk,
                    'correlation_risk': portfolio_metrics.correlation_risk,
                    'liquidity_risk': portfolio_metrics.liquidity_risk
                },
                'current_risk_score': current_risk_score,
                'position_count': len(self.position_history),
                'daily_pnl_count': len(self.daily_pnl_history),
                'risk_limits': {
                    'max_daily_loss': self.max_daily_loss,
                    'max_position_risk': self.max_position_risk,
                    'max_position_size': self.max_position_size,
                    'max_consecutive_losses': self.max_consecutive_losses
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting risk summary: {e}")
            return {}