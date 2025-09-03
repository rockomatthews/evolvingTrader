"""
Real-time dashboard that connects to actual database and Redis
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
app.title = "EvolvingTrader Dashboard - Real Data"

# Global data cache
dashboard_data_cache = {}

async def fetch_real_dashboard_data():
    """Fetch real dashboard data from database and Redis"""
    try:
        # Import here to avoid issues if not available
        from src.database.connection import db_manager
        from src.cache.redis_service import redis_service
        from src.database.repository import trading_repo, performance_repo
        
        # Initialize connections
        await db_manager.initialize()
        await redis_service.initialize()
        
        # Get active trading session
        active_session = await trading_repo.get_active_session()
        if not active_session:
            return {}
        
        # Get performance summary from database
        performance_summary = await db_manager.get_performance_summary(active_session.id)
        
        # Get cached performance metrics from Redis
        cached_performance = await redis_service.get_cached_performance_metrics()
        
        # Get cached positions from Redis
        cached_positions = await redis_service.get_cached_positions()
        
        # Get recent trades from database
        recent_trades = await trading_repo.get_trades(active_session.id, limit=50)
        
        # Get performance history
        performance_history = await trading_repo.get_performance_history(active_session.id, limit=20)
        
        return {
            'engine_status': {
                'is_running': True,  # Assume running if we can connect
                'start_time': active_session.start_time.isoformat(),
                'runtime_hours': (datetime.now() - active_session.start_time).total_seconds() / 3600,
                'symbols': active_session.symbols or ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
            },
            'performance': {
                'initial_balance': active_session.initial_capital,
                'current_balance': cached_performance.get('current_balance', active_session.initial_capital) if cached_performance else active_session.initial_capital,
                'total_return_pct': performance_summary.get('total_return_pct', 0),
                'total_pnl': performance_summary.get('total_pnl', 0),
                'total_trades': performance_summary.get('total_trades', 0),
                'win_rate': performance_summary.get('win_rate', 0),
                'profit_factor': performance_summary.get('profit_factor', 0),
                'current_positions': len(cached_positions) if cached_positions else 0
            },
            'strategy': {
                'parameters': cached_performance.get('strategy_parameters', {}) if cached_performance else {},
                'last_evolution': datetime.now().isoformat()
            },
            'memory': {
                'total_vectors': 0,  # Would need to query Pinecone
                'record_counts': {
                    'trade': performance_summary.get('total_trades', 0),
                    'strategy_params': 0,
                    'performance': len(performance_history),
                    'market_pattern': 0
                }
            },
            'positions': cached_positions or {},
            'recent_trades': [{
                'symbol': trade.symbol,
                'side': trade.side,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'pnl': trade.pnl,
                'entry_time': trade.entry_time.isoformat(),
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None
            } for trade in recent_trades]
        }
        
    except Exception as e:
        logger.error(f"Error fetching real dashboard data: {e}")
        return {}

def create_performance_chart(trades_data: list) -> go.Figure:
    """Create performance chart from real trade data"""
    if not trades_data:
        return go.Figure()
    
    # Create cumulative P&L chart
    df = pd.DataFrame(trades_data)
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
        title="Cumulative P&L Over Time (Real Data)",
        xaxis_title="Trade Number",
        yaxis_title="Cumulative P&L (USDT)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_win_rate_chart(trades_data: list) -> go.Figure:
    """Create win rate chart from real trade data"""
    if not trades_data:
        return go.Figure()
    
    # Calculate rolling win rate
    df = pd.DataFrame(trades_data)
    df['is_win'] = df['pnl'] > 0
    df['rolling_win_rate'] = df['is_win'].rolling(window=10, min_periods=1).mean() * 100
    df['trade_number'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['trade_number'],
        y=df['rolling_win_rate'],
        mode='lines',
        name='Rolling Win Rate (10 trades)',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Rolling Win Rate (Real Data)",
        xaxis_title="Trade Number",
        yaxis_title="Win Rate (%)",
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    return fig

def create_position_size_chart(trades_data: list) -> go.Figure:
    """Create position size distribution chart from real trade data"""
    if not trades_data:
        return go.Figure()
    
    df = pd.DataFrame(trades_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['pnl'],
        nbinsx=20,
        name='P&L Distribution',
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title="P&L Distribution (Real Data)",
        xaxis_title="P&L (USDT)",
        yaxis_title="Frequency",
        height=400
    )
    
    return fig

# Dashboard layout
app.layout = html.Div([
    html.H1("EvolvingTrader - AI-Powered Trading Strategy (Real Data)", 
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
    
    # Recent trades
    html.Div([
        html.H3("Recent Trades", style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='recent-trades', style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 10})
    ], style={'marginBottom': 30}),
    
    # Footer
    html.Div([
        html.P("EvolvingTrader - AI-Powered Trading Strategy (Real Data)", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 12}),
        html.P("Real-time data from live trading system", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 10})
    ], style={'marginTop': 50}),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update every 10 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('engine-status', 'children'),
     Output('current-balance', 'children'),
     Output('total-return', 'children'),
     Output('performance-metrics', 'children'),
     Output('active-positions', 'children'),
     Output('recent-trades', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update dashboard with real data"""
    try:
        # Fetch real data
        dashboard_data = asyncio.run(fetch_real_dashboard_data())
        
        if not dashboard_data:
            return "No Data", "N/A", "N/A", "No Data Available", "No Data Available", "No Data Available"
        
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
        
        # Recent trades
        recent_trades = dashboard_data.get('recent_trades', [])
        if recent_trades:
            trade_list = []
            for trade in recent_trades[-10:]:  # Show last 10 trades
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                trade_list.append(html.P([
                    f"🔸 {trade['symbol']} {trade['side']}: ",
                    f"Entry: ${trade['entry_price']:,.2f}, ",
                    f"Exit: ${trade['exit_price']:,.2f}, ",
                    html.Span(f"P&L: ${trade['pnl']:,.2f}", style={'color': pnl_color})
                ]))
            recent_trades_display = html.Div(trade_list)
        else:
            recent_trades_display = html.P("No trades yet")
        
        return (engine_status, current_balance, total_return, performance_metrics, 
                active_positions, recent_trades_display)
        
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")
        return "Error", "N/A", "N/A", "Error", "Error", "Error"

@app.callback(
    [Output('performance-chart', 'figure'),
     Output('win-rate-chart', 'figure'),
     Output('position-size-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_charts(n):
    """Update charts with real trade data"""
    try:
        # Fetch real data
        dashboard_data = asyncio.run(fetch_real_dashboard_data())
        trades_data = dashboard_data.get('recent_trades', [])
        
        # Create charts from real data
        perf_chart = create_performance_chart(trades_data)
        win_rate_chart = create_win_rate_chart(trades_data)
        position_chart = create_position_size_chart(trades_data)
        
        return perf_chart, win_rate_chart, position_chart
        
    except Exception as e:
        logger.error(f"Error updating charts: {e}")
        return go.Figure(), go.Figure(), go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)