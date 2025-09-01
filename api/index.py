"""
Vercel serverless function for EvolvingTrader dashboard
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "EvolvingTrader Dashboard"

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
        hovermode='x unified',
        height=400
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
        yaxis=dict(range=[0, 100]),
        height=400
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
        yaxis_title="Frequency",
        height=400
    )
    
    return fig

async def fetch_dashboard_data():
    """Fetch dashboard data from Redis/Database"""
    try:
        # This would connect to your Redis/Database in production
        # For demo purposes, return mock data
        return {
            'engine_status': {
                'is_running': True,
                'start_time': datetime.now().isoformat(),
                'runtime_hours': 24.5,
                'symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
            },
            'performance': {
                'initial_balance': 1000.0,
                'current_balance': 1250.0,
                'total_return_pct': 25.0,
                'total_pnl': 250.0,
                'total_trades': 45,
                'win_rate': 68.9,
                'profit_factor': 2.1,
                'current_positions': 3
            },
            'strategy': {
                'parameters': {
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                    'max_position_size': 0.1
                },
                'last_evolution': datetime.now().isoformat()
            },
            'memory': {
                'total_vectors': 1250,
                'record_counts': {
                    'trade': 45,
                    'strategy_params': 12,
                    'performance': 8,
                    'market_pattern': 89
                }
            },
            'positions': {
                'BTCUSDT': {
                    'side': 'BUY',
                    'quantity': 0.01,
                    'entry_price': 45000.0
                },
                'ETHUSDT': {
                    'side': 'SELL',
                    'quantity': 0.5,
                    'entry_price': 3200.0
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return {}

# Dashboard layout
app.layout = html.Div([
    html.H1("EvolvingTrader - AI-Powered Trading Strategy", 
            style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
    
    # Status cards
    html.Div([
        html.Div([
            html.H3("Engine Status", style={'textAlign': 'center', 'color': '#34495e'}),
            html.Div(id='engine-status', style={'textAlign': 'center', 'fontSize': 20, 'color': '#27ae60'})
        ], className='four columns', style={'backgroundColor': '#ecf0f1', 'padding': 20, 'borderRadius': 10, 'margin': 5}),
        
        html.Div([
            html.H3("Current Balance", style={'textAlign': 'center', 'color': '#34495e'}),
            html.Div(id='current-balance', style={'textAlign': 'center', 'fontSize': 20, 'color': '#27ae60'})
        ], className='four columns', style={'backgroundColor': '#ecf0f1', 'padding': 20, 'borderRadius': 10, 'margin': 5}),
        
        html.Div([
            html.H3("Total Return", style={'textAlign': 'center', 'color': '#34495e'}),
            html.Div(id='total-return', style={'textAlign': 'center', 'fontSize': 20, 'color': '#27ae60'})
        ], className='four columns', style={'backgroundColor': '#ecf0f1', 'padding': 20, 'borderRadius': 10, 'margin': 5})
    ], className='row', style={'marginBottom': 30}),
    
    # Performance metrics
    html.Div([
        html.Div([
            html.H3("Performance Metrics", style={'textAlign': 'center', 'color': '#34495e'}),
            html.Div(id='performance-metrics', style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 10})
        ], className='six columns', style={'margin': 5}),
        
        html.Div([
            html.H3("Active Positions", style={'textAlign': 'center', 'color': '#34495e'}),
            html.Div(id='active-positions', style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 10})
        ], className='six columns', style={'margin': 5})
    ], className='row', style={'marginBottom': 30}),
    
    # Charts
    html.Div([
        html.Div([
            dcc.Graph(id='performance-chart')
        ], className='six columns', style={'margin': 5}),
        
        html.Div([
            dcc.Graph(id='win-rate-chart')
        ], className='six columns', style={'margin': 5})
    ], className='row', style={'marginBottom': 30}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='position-size-chart')
        ], className='twelve columns', style={'margin': 5})
    ], className='row', style={'marginBottom': 30}),
    
    # Strategy parameters
    html.Div([
        html.H3("Strategy Parameters", style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='strategy-parameters', style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 10})
    ], style={'marginBottom': 30}),
    
    # Memory statistics
    html.Div([
        html.H3("Memory Statistics", style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='memory-stats', style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 10})
    ], style={'marginBottom': 30}),
    
    # Footer
    html.Div([
        html.P("EvolvingTrader - AI-Powered Trading Strategy", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 12}),
        html.P("Real-time data updates every 5 seconds", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 10})
    ], style={'marginTop': 50}),
    
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
        # Fetch data (in production, this would be async)
        dashboard_data = asyncio.run(fetch_dashboard_data())
        
        if not dashboard_data:
            return "Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Engine status
        engine_status = "🟢 Running" if dashboard_data['engine_status']['is_running'] else "🔴 Stopped"
        
        # Current balance
        current_balance = f"${dashboard_data['performance']['current_balance']:,.2f}"
        
        # Total return
        total_return = f"{dashboard_data['performance']['total_return_pct']:+.2f}%"
        
        # Performance metrics
        perf = dashboard_data['performance']
        performance_metrics = html.Div([
            html.P(f"📊 Total Trades: {perf['total_trades']}"),
            html.P(f"🎯 Win Rate: {perf['win_rate']:.1f}%"),
            html.P(f"💰 Total P&L: ${perf['total_pnl']:,.2f}"),
            html.P(f"📈 Profit Factor: {perf['profit_factor']:.2f}"),
            html.P(f"📋 Active Positions: {perf['current_positions']}")
        ])
        
        # Active positions
        positions = dashboard_data.get('positions', {})
        if positions:
            position_list = []
            for symbol, pos in positions.items():
                position_list.append(html.P(f"🔸 {symbol}: {pos['side']} {pos['quantity']} @ ${pos['entry_price']:,.2f}"))
            active_positions = html.Div(position_list)
        else:
            active_positions = html.P("No active positions")
        
        # Strategy parameters
        strategy_params = dashboard_data.get('strategy', {}).get('parameters', {})
        if strategy_params:
            param_list = []
            for key, value in strategy_params.items():
                param_list.append(html.P(f"🔧 {key}: {value}"))
            strategy_parameters = html.Div(param_list)
        else:
            strategy_parameters = html.P("No parameters available")
        
        # Memory statistics
        memory_stats = dashboard_data.get('memory', {})
        if memory_stats:
            memory_info = html.Div([
                html.P(f"🧠 Total Vectors: {memory_stats.get('total_vectors', 0):,}"),
                html.P(f"📝 Record Counts: {memory_stats.get('record_counts', {})}")
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
        # Mock performance data for demo
        mock_performance = {
            'trades': [
                {'pnl': 25.5, 'symbol': 'BTCUSDT'},
                {'pnl': -12.3, 'symbol': 'ETHUSDT'},
                {'pnl': 18.7, 'symbol': 'ADAUSDT'},
                {'pnl': 31.2, 'symbol': 'BTCUSDT'},
                {'pnl': -8.9, 'symbol': 'ETHUSDT'},
                {'pnl': 22.1, 'symbol': 'ADAUSDT'},
                {'pnl': 15.8, 'symbol': 'BTCUSDT'},
                {'pnl': -5.4, 'symbol': 'ETHUSDT'},
                {'pnl': 28.3, 'symbol': 'ADAUSDT'},
                {'pnl': 19.6, 'symbol': 'BTCUSDT'}
            ]
        }
        
        # Create charts
        perf_chart = create_performance_chart(mock_performance)
        win_rate_chart = create_win_rate_chart(mock_performance)
        position_chart = create_position_size_chart(mock_performance)
        
        return perf_chart, win_rate_chart, position_chart
        
    except Exception as e:
        logger.error(f"Error updating charts: {e}")
        return go.Figure(), go.Figure(), go.Figure()

# Vercel handler
def handler(request):
    """Vercel serverless function handler"""
    return app.server(request)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)