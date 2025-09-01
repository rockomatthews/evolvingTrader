"""
Real-time dashboard for EvolvingTrader performance monitoring
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import logging

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

from src.trading_engine import EvolvingTraderEngine
from config import trading_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "EvolvingTrader Dashboard"

# Global engine instance
engine = None

def create_performance_chart(performance_data: Dict) -> go.Figure:
    """Create performance chart"""
    if not performance_data or 'trades' not in performance_data:
        return go.Figure()
    
    trades = performance_data['trades']
    if not trades:
        return go.Figure()
    
    # Create cumulative P&L chart
    df = pd.DataFrame(trades)
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['trade_number'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    # Add cumulative P&L line
    fig.add_trace(go.Scatter(
        x=df['trade_number'],
        y=df['cumulative_pnl'],
        mode='lines+markers',
        name='Cumulative P&L',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title="Cumulative P&L Over Time",
        xaxis_title="Trade Number",
        yaxis_title="Cumulative P&L (USDT)",
        hovermode='x unified'
    )
    
    return fig

def create_win_rate_chart(performance_data: Dict) -> go.Figure:
    """Create win rate chart"""
    if not performance_data or 'trades' not in performance_data:
        return go.Figure()
    
    trades = performance_data['trades']
    if not trades:
        return go.Figure()
    
    # Calculate rolling win rate
    df = pd.DataFrame(trades)
    df['is_win'] = df['pnl'] > 0
    df['rolling_win_rate'] = df['is_win'].rolling(window=20, min_periods=1).mean() * 100
    df['trade_number'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['trade_number'],
        y=df['rolling_win_rate'],
        mode='lines',
        name='Rolling Win Rate (20 trades)',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Rolling Win Rate",
        xaxis_title="Trade Number",
        yaxis_title="Win Rate (%)",
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_position_size_chart(performance_data: Dict) -> go.Figure:
    """Create position size distribution chart"""
    if not performance_data or 'trades' not in performance_data:
        return go.Figure()
    
    trades = performance_data['trades']
    if not trades:
        return go.Figure()
    
    df = pd.DataFrame(trades)
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['pnl'],
        nbinsx=20,
        name='P&L Distribution',
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title="P&L Distribution",
        xaxis_title="P&L (USDT)",
        yaxis_title="Frequency"
    )
    
    return fig

# Dashboard layout
app.layout = html.Div([
    html.H1("EvolvingTrader - AI-Powered Trading Strategy", 
            style={'textAlign': 'center', 'marginBottom': 30}),
    
    # Status cards
    html.Div([
        html.Div([
            html.H3("Engine Status", style={'textAlign': 'center'}),
            html.Div(id='engine-status', style={'textAlign': 'center', 'fontSize': 20})
        ], className='four columns'),
        
        html.Div([
            html.H3("Current Balance", style={'textAlign': 'center'}),
            html.Div(id='current-balance', style={'textAlign': 'center', 'fontSize': 20})
        ], className='four columns'),
        
        html.Div([
            html.H3("Total Return", style={'textAlign': 'center'}),
            html.Div(id='total-return', style={'textAlign': 'center', 'fontSize': 20})
        ], className='four columns')
    ], className='row', style={'marginBottom': 30}),
    
    # Performance metrics
    html.Div([
        html.Div([
            html.H3("Performance Metrics", style={'textAlign': 'center'}),
            html.Div(id='performance-metrics')
        ], className='six columns'),
        
        html.Div([
            html.H3("Active Positions", style={'textAlign': 'center'}),
            html.Div(id='active-positions')
        ], className='six columns')
    ], className='row', style={'marginBottom': 30}),
    
    # Charts
    html.Div([
        html.Div([
            dcc.Graph(id='performance-chart')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='win-rate-chart')
        ], className='six columns')
    ], className='row', style={'marginBottom': 30}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='position-size-chart')
        ], className='twelve columns')
    ], className='row', style={'marginBottom': 30}),
    
    # Strategy parameters
    html.Div([
        html.H3("Strategy Parameters", style={'textAlign': 'center'}),
        html.Div(id='strategy-parameters')
    ], style={'marginBottom': 30}),
    
    # Memory statistics
    html.Div([
        html.H3("Memory Statistics", style={'textAlign': 'center'}),
        html.Div(id='memory-stats')
    ], style={'marginBottom': 30}),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('engine-status', 'children'),
     Output('current-balance', 'children'),
     Output('total-return', 'children'),
     Output('performance-metrics', 'children'),
     Output('active-positions', 'children'),
     Output('strategy-parameters', 'children'),
     Output('memory-stats', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update dashboard data"""
    try:
        if engine is None:
            return "Not Connected", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Get dashboard data
        dashboard_data = asyncio.run(engine.get_dashboard_data())
        
        if not dashboard_data:
            return "Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Engine status
        engine_status = "Running" if dashboard_data['engine_status']['is_running'] else "Stopped"
        
        # Current balance
        current_balance = f"${dashboard_data['performance']['current_balance']:.2f}"
        
        # Total return
        total_return = f"{dashboard_data['performance']['total_return_pct']:.2f}%"
        
        # Performance metrics
        perf = dashboard_data['performance']
        performance_metrics = html.Div([
            html.P(f"Total Trades: {perf['total_trades']}"),
            html.P(f"Win Rate: {perf['win_rate']:.1f}%"),
            html.P(f"Total P&L: ${perf['total_pnl']:.2f}"),
            html.P(f"Profit Factor: {perf['profit_factor']:.2f}"),
            html.P(f"Active Positions: {perf['current_positions']}")
        ])
        
        # Active positions
        positions = dashboard_data.get('positions', {})
        if positions:
            position_list = []
            for symbol, pos in positions.items():
                position_list.append(html.P(f"{symbol}: {pos['side']} {pos['quantity']} @ ${pos['entry_price']:.2f}"))
            active_positions = html.Div(position_list)
        else:
            active_positions = html.P("No active positions")
        
        # Strategy parameters
        strategy_params = dashboard_data.get('strategy', {}).get('parameters', {})
        if strategy_params:
            param_list = []
            for key, value in strategy_params.items():
                param_list.append(html.P(f"{key}: {value}"))
            strategy_parameters = html.Div(param_list)
        else:
            strategy_parameters = html.P("No parameters available")
        
        # Memory statistics
        memory_stats = dashboard_data.get('memory', {})
        if memory_stats:
            memory_info = html.Div([
                html.P(f"Total Vectors: {memory_stats.get('total_vectors', 0)}"),
                html.P(f"Record Counts: {memory_stats.get('record_counts', {})}")
            ])
        else:
            memory_info = html.P("No memory statistics available")
        
        return (engine_status, current_balance, total_return, performance_metrics, 
                active_positions, strategy_parameters, memory_info)
        
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")
        return "Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

@app.callback(
    [Output('performance-chart', 'figure'),
     Output('win-rate-chart', 'figure'),
     Output('position-size-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_charts(n):
    """Update charts"""
    try:
        if engine is None:
            return go.Figure(), go.Figure(), go.Figure()
        
        # Get performance data
        performance_summary = asyncio.run(engine.strategy.get_performance_summary())
        
        # Create charts
        perf_chart = create_performance_chart(performance_summary)
        win_rate_chart = create_win_rate_chart(performance_summary)
        position_chart = create_position_size_chart(performance_summary)
        
        return perf_chart, win_rate_chart, position_chart
        
    except Exception as e:
        logger.error(f"Error updating charts: {e}")
        return go.Figure(), go.Figure(), go.Figure()

async def start_dashboard():
    """Start the dashboard server"""
    global engine
    
    try:
        # Initialize engine
        engine = EvolvingTraderEngine()
        await engine.initialize()
        
        # Start engine in background
        asyncio.create_task(engine._main_trading_loop())
        
        logger.info("Dashboard server starting...")
        
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")

def run_dashboard():
    """Run the dashboard"""
    try:
        # Start engine in background
        asyncio.run(start_dashboard())
        
        # Start Dash server
        app.run_server(debug=True, host='0.0.0.0', port=8050)
        
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")

if __name__ == '__main__':
    run_dashboard()