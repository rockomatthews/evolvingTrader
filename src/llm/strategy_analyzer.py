"""
LLM-powered strategy analyzer for evolving trading strategies
"""
import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

import openai
from config import openai_config

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for strategy analysis"""
    total_trades: int
    total_pnl: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    recent_performance: List[float]  # Last 20 trades P&L

@dataclass
class StrategyAnalysis:
    """Result of strategy analysis"""
    should_evolve: bool
    confidence: float
    reasoning: str
    new_parameters: Dict[str, Any]
    risk_assessment: str
    recommendations: List[str]

class StrategyAnalyzer:
    """
    LLM-powered analyzer for evolving trading strategies
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=openai_config.api_key)
        self.initialized = False
        
    async def initialize(self):
        """Initialize the analyzer"""
        try:
            # Test OpenAI connection
            await self.client.models.list()
            self.initialized = True
            logger.info("Strategy analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize strategy analyzer: {e}")
            raise
    
    def _calculate_performance_metrics(self, trade_history: List[Dict]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if not trade_history:
            return PerformanceMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, [])
        
        pnl_values = [trade['pnl'] for trade in trade_history]
        total_trades = len(trade_history)
        total_pnl = sum(pnl_values)
        
        # Win rate
        winning_trades = [pnl for pnl in pnl_values if pnl > 0]
        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = np.mean(winning_trades) if winning_trades else 0
        losing_trades = [pnl for pnl in pnl_values if pnl < 0]
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # Profit factor
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        # Max drawdown
        cumulative_pnl = np.cumsum(pnl_values)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdowns = running_max - cumulative_pnl
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
        
        # Sharpe ratio (simplified)
        if len(pnl_values) > 1:
            sharpe_ratio = np.mean(pnl_values) / np.std(pnl_values) if np.std(pnl_values) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Recent performance (last 20 trades)
        recent_performance = pnl_values[-20:] if len(pnl_values) >= 20 else pnl_values
        
        return PerformanceMetrics(
            total_trades=total_trades,
            total_pnl=total_pnl,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            recent_performance=recent_performance
        )
    
    async def analyze_performance(self, trade_history: List[Dict], 
                                current_params: Any) -> Optional[StrategyAnalysis]:
        """Analyze trading performance and suggest strategy evolution"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Calculate performance metrics
            metrics = self._calculate_performance_metrics(trade_history)
            
            # Prepare analysis prompt
            analysis_prompt = self._create_analysis_prompt(metrics, current_params, trade_history)
            
            # Get LLM analysis
            response = await self.client.chat.completions.create(
                model=openai_config.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert quantitative trading strategist and risk manager. 
                        Your job is to analyze trading performance and suggest improvements to trading strategies.
                        
                        Focus on:
                        1. Risk management and position sizing
                        2. Market regime adaptation
                        3. Parameter optimization
                        4. Strategy diversification
                        
                        Always provide specific, actionable recommendations with clear reasoning."""
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse LLM response
            analysis_text = response.choices[0].message.content
            analysis_result = self._parse_analysis_response(analysis_text, metrics)
            
            logger.info(f"Strategy analysis completed: {analysis_result.reasoning}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return None
    
    def _create_analysis_prompt(self, metrics: PerformanceMetrics, 
                              current_params: Any, trade_history: List[Dict]) -> str:
        """Create analysis prompt for LLM"""
        
        # Recent trades context
        recent_trades = trade_history[-10:] if len(trade_history) >= 10 else trade_history
        recent_trades_text = ""
        for trade in recent_trades:
            recent_trades_text += f"  {trade['symbol']} {trade['side']}: P&L={trade['pnl']:.2f}, Reason={trade['reason']}\n"
        
        prompt = f"""
        Analyze the following trading strategy performance and provide recommendations:

        PERFORMANCE METRICS:
        - Total Trades: {metrics.total_trades}
        - Total P&L: {metrics.total_pnl:.2f} USDT
        - Win Rate: {metrics.win_rate:.1f}%
        - Average Win: {metrics.avg_win:.2f} USDT
        - Average Loss: {metrics.avg_loss:.2f} USDT
        - Profit Factor: {metrics.profit_factor:.2f}
        - Max Drawdown: {metrics.max_drawdown:.2f} USDT
        - Sharpe Ratio: {metrics.sharpe_ratio:.2f}

        CURRENT STRATEGY PARAMETERS:
        - RSI Period: {current_params.rsi_period}
        - RSI Oversold: {current_params.rsi_oversold}
        - RSI Overbought: {current_params.rsi_overbought}
        - Bollinger Bands Period: {current_params.bb_period}
        - Bollinger Bands Std: {current_params.bb_std}
        - EMA Fast: {current_params.ema_fast}
        - EMA Slow: {current_params.ema_slow}
        - MACD Signal: {current_params.macd_signal}
        - Max Position Size: {current_params.max_position_size}
        - Stop Loss %: {current_params.stop_loss_pct}
        - Take Profit %: {current_params.take_profit_pct}
        - Strategy Weights: Momentum={current_params.momentum_weight}, Mean Reversion={current_params.mean_reversion_weight}, Trend={current_params.trend_weight}, Volume={current_params.volume_weight}

        RECENT TRADES (Last 10):
        {recent_trades_text}

        Please provide analysis in the following JSON format:
        {{
            "should_evolve": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "Detailed explanation of analysis",
            "new_parameters": {{
                "parameter_name": "new_value",
                ...
            }},
            "risk_assessment": "Risk level and concerns",
            "recommendations": ["Recommendation 1", "Recommendation 2", ...]
        }}

        Focus on:
        1. Is the strategy performing well enough to continue?
        2. What parameters should be adjusted and why?
        3. Are there risk management improvements needed?
        4. Should we change the strategy weights?
        5. Any market regime adaptations needed?
        """
        
        return prompt
    
    def _parse_analysis_response(self, response_text: str, metrics: PerformanceMetrics) -> StrategyAnalysis:
        """Parse LLM response into structured analysis"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                analysis_data = json.loads(json_text)
                
                return StrategyAnalysis(
                    should_evolve=analysis_data.get('should_evolve', False),
                    confidence=analysis_data.get('confidence', 0.5),
                    reasoning=analysis_data.get('reasoning', 'No reasoning provided'),
                    new_parameters=analysis_data.get('new_parameters', {}),
                    risk_assessment=analysis_data.get('risk_assessment', 'No risk assessment'),
                    recommendations=analysis_data.get('recommendations', [])
                )
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse_analysis(response_text, metrics)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            return self._fallback_parse_analysis(response_text, metrics)
    
    def _fallback_parse_analysis(self, response_text: str, metrics: PerformanceMetrics) -> StrategyAnalysis:
        """Fallback parsing when JSON parsing fails"""
        
        # Simple heuristics for strategy evolution
        should_evolve = False
        confidence = 0.5
        reasoning = "Fallback analysis based on performance metrics"
        new_parameters = {}
        
        # Determine if evolution is needed based on metrics
        if metrics.win_rate < 40 or metrics.profit_factor < 1.2 or metrics.max_drawdown > 100:
            should_evolve = True
            confidence = 0.8
            reasoning = f"Poor performance detected: Win rate {metrics.win_rate:.1f}%, Profit factor {metrics.profit_factor:.2f}, Max drawdown {metrics.max_drawdown:.2f}"
            
            # Suggest parameter adjustments
            if metrics.win_rate < 40:
                new_parameters['rsi_oversold'] = 25  # More conservative
                new_parameters['rsi_overbought'] = 75
            if metrics.profit_factor < 1.2:
                new_parameters['take_profit_pct'] = 0.06  # Higher take profit
                new_parameters['stop_loss_pct'] = 0.015  # Tighter stop loss
        elif metrics.win_rate > 60 and metrics.profit_factor > 2.0:
            should_evolve = True
            confidence = 0.7
            reasoning = f"Good performance, optimizing for better results: Win rate {metrics.win_rate:.1f}%, Profit factor {metrics.profit_factor:.2f}"
            
            # Optimize parameters
            new_parameters['max_position_size'] = min(0.15, metrics.max_position_size * 1.1)
        
        return StrategyAnalysis(
            should_evolve=should_evolve,
            confidence=confidence,
            reasoning=reasoning,
            new_parameters=new_parameters,
            risk_assessment="Standard risk assessment",
            recommendations=["Monitor performance closely", "Consider parameter adjustments"]
        )
    
    async def analyze_market_regime(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market regime using LLM"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Prepare market regime analysis prompt
            regime_prompt = f"""
            Analyze the current market regime based on the following data:
            
            MARKET DATA:
            {json.dumps(market_data, indent=2)}
            
            Determine:
            1. Market regime (trending, ranging, volatile, calm)
            2. Recommended strategy adjustments
            3. Risk level assessment
            
            Respond in JSON format:
            {{
                "regime": "trending/ranging/volatile/calm",
                "confidence": 0.0-1.0,
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "risk_level": "low/medium/high",
                "strategy_adjustments": {{
                    "parameter": "value"
                }}
            }}
            """
            
            response = await self.client.chat.completions.create(
                model=openai_config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a market regime analyst. Analyze market conditions and provide trading strategy recommendations."
                    },
                    {
                        "role": "user",
                        "content": regime_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                return json.loads(json_text)
            else:
                return {
                    "regime": "unknown",
                    "confidence": 0.5,
                    "recommendations": ["Monitor market conditions"],
                    "risk_level": "medium",
                    "strategy_adjustments": {}
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze market regime: {e}")
            return {
                "regime": "unknown",
                "confidence": 0.5,
                "recommendations": ["Error in analysis"],
                "risk_level": "high",
                "strategy_adjustments": {}
            }
    
    async def generate_trading_insights(self, performance_data: Dict) -> List[str]:
        """Generate trading insights using LLM"""
        if not self.initialized:
            await self.initialize()
        
        try:
            insights_prompt = f"""
            Based on the following trading performance data, generate actionable insights:
            
            {json.dumps(performance_data, indent=2)}
            
            Provide 3-5 specific, actionable insights for improving trading performance.
            Focus on concrete recommendations that can be implemented.
            """
            
            response = await self.client.chat.completions.create(
                model=openai_config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a trading performance analyst. Provide specific, actionable insights for improving trading results."
                    },
                    {
                        "role": "user",
                        "content": insights_prompt
                    }
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            insights_text = response.choices[0].message.content
            
            # Extract insights (simple parsing)
            insights = []
            lines = insights_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    insights.append(line)
            
            return insights if insights else ["Monitor performance closely", "Consider strategy adjustments"]
            
        except Exception as e:
            logger.error(f"Failed to generate trading insights: {e}")
            return ["Error generating insights", "Monitor performance closely"]