"""
Real-time dashboard with actual trading data
"""
import asyncio
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

import dash
from dash import dcc, html, Input, Output, callback, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "EvolvingTrader - Live Dashboard"

# API base URL
API_BASE_URL = "http://127.0.0.1:8000/api"

def fetch_api_data(endpoint: str) -> Dict[str, Any]:
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching {endpoint}: {e}")
        return {}

def create_account_overview(data: Dict[str, Any]) -> html.Div:
    """Create account overview section"""
    account = data.get('account', {})
    config = data.get('config', {})
    
    total_balance = account.get('total_balance', 0)
    can_trade = account.get('can_trade', False)
    testnet = config.get('testnet', True)
    
    return html.Div([
        html.H3("💰 Account Overview", className="text-center mb-4"),
        html.Div([
            html.Div([
                html.H4(f"${total_balance:.2f}", className="text-success"),
                html.P("Total Balance", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4("LIVE" if not testnet else "TESTNET", 
                       className="text-danger" if not testnet else "text-warning"),
                html.P("Trading Mode", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4("✅" if can_trade else "❌", 
                       className="text-success" if can_trade else "text-danger"),
                html.P("Can Trade", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4(f"${config.get('initial_capital', 0):.2f}", className="text-info"),
                html.P("Initial Capital", className="text-muted")
            ], className="col-md-3 text-center"),
        ], className="row"),
    ], className="card mb-4")

def create_trading_stats(data: Dict[str, Any]) -> html.Div:
    """Create trading statistics section"""
    trades = data.get('trades', {})
    stats = trades.get('statistics', {})
    
    total_trades = stats.get('total_trades', 0)
    win_rate = stats.get('win_rate', 0)
    total_pnl = stats.get('total_pnl', 0)
    profit_factor = stats.get('profit_factor', 0)
    
    return html.Div([
        html.H3("📊 Trading Statistics", className="text-center mb-4"),
        html.Div([
            html.Div([
                html.H4(f"{total_trades}", className="text-primary"),
                html.P("Total Trades", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4(f"{win_rate:.1f}%", 
                       className="text-success" if win_rate > 50 else "text-danger"),
                html.P("Win Rate", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4(f"${total_pnl:.2f}", 
                       className="text-success" if total_pnl > 0 else "text-danger"),
                html.P("Total P&L", className="text-muted")
            ], className="col-md-3 text-center"),
            html.Div([
                html.H4(f"{profit_factor:.2f}", 
                       className="text-success" if profit_factor > 1 else "text-danger"),
                html.P("Profit Factor", className="text-muted")
            ], className="col-md-3 text-center"),
        ], className="row"),
    ], className="card mb-4")

def create_market_data(data: Dict[str, Any]) -> html.Div:
    """Create market data section"""
    market = data.get('market', {})
    current_price = market.get('current_price', 0)
    indicators = market.get('indicators', {})
    
    rsi = indicators.get('rsi', 0)
    macd = indicators.get('macd', 0)
    
    return html.Div([
        html.H3("📈 Market Data", className="text-center mb-4"),
        html.Div([
            html.Div([
                html.H4(f"${current_price:,.2f}", className="text-primary"),
                html.P("BTCUSDT Price", className="text-muted")
            ], className="col-md-4 text-center"),
            html.Div([
                html.H4(f"{rsi:.1f}", 
                       className="text-danger" if rsi > 70 else "text-success" if rsi < 30 else "text-warning"),
                html.P("RSI", className="text-muted")
            ], className="col-md-4 text-center"),
            html.Div([
                html.H4(f"{macd:.4f}", 
                       className="text-success" if macd > 0 else "text-danger"),
                html.P("MACD", className="text-muted")
            ], className="col-md-4 text-center"),
        ], className="row"),
    ], className="card mb-4")

def create_signals_section(data: Dict[str, Any]) -> html.Div:
    """Create trading signals section"""
    signals = data.get('signals', {})
    signal_list = signals.get('signals', [])
    
    if not signal_list:
        return html.Div([
            html.H3("🎯 Trading Signals", className="text-center mb-4"),
            html.Div([
                html.P("No active signals", className="text-center text-muted")
            ], className="card-body")
        ], className="card mb-4")
    
    signal_cards = []
    for signal in signal_list:
        signal_type = signal.get('signal_type', 'HOLD')
        confidence = signal.get('confidence', 0)
        reasoning = signal.get('reasoning', '')
        
        color_class = "success" if signal_type == "BUY" else "danger" if signal_type == "SELL" else "warning"
        
        signal_cards.append(
            html.Div([
                html.H5(f"{signal_type} Signal", className=f"text-{color_class}"),
                html.P(f"Confidence: {confidence:.2f}", className="mb-1"),
                html.P(f"Reasoning: {reasoning}", className="mb-1"),
                html.Small(f"Entry: ${signal.get('entry_price', 0):.2f}", className="text-muted")
            ], className="card-body")
        )
    
    return html.Div([
        html.H3("🎯 Trading Signals", className="text-center mb-4"),
        html.Div(signal_cards, className="card-body")
    ], className="card mb-4")

def create_performance_chart(data: Dict[str, Any]) -> html.Div:
    """Create performance chart"""
    trades = data.get('trades', {})
    trade_list = trades.get('trades', [])
    
    if not trade_list:
        return html.Div([
            html.H3("📊 Performance Chart", className="text-center mb-4"),
            html.Div([
                html.P("No trades yet", className="text-center text-muted")
            ], className="card-body")
        ], className="card mb-4")
    
    # Create cumulative P&L chart
    df = pd.DataFrame(trade_list)
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['trade_number'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['trade_number'],
        y=df['cumulative_pnl'],
        mode='lines+markers',
        name='Cumulative P&L',
        line=dict(color='green' if df['cumulative_pnl'].iloc[-1] > 0 else 'red')
    ))
    
    fig.update_layout(
        title="Cumulative P&L",
        xaxis_title="Trade Number",
        yaxis_title="P&L ($)",
        showlegend=False
    )
    
    return html.Div([
        html.H3("📊 Performance Chart", className="text-center mb-4"),
        dcc.Graph(figure=fig)
    ], className="card mb-4")

def create_price_chart(data: Dict[str, Any]) -> html.Div:
    """Create price chart"""
    market = data.get('market', {})
    price_history = market.get('price_history', [])
    
    if not price_history:
        return html.Div([
            html.H3("📈 Price Chart", className="text-center mb-4"),
            html.Div([
                html.P("No price data available", className="text-center text-muted")
            ], className="card-body")
        ], className="card mb-4")
    
    df = pd.DataFrame(price_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['price'],
        mode='lines',
        name='BTCUSDT Price',
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        title="BTCUSDT Price (24h)",
        xaxis_title="Time",
        yaxis_title="Price ($)",
        showlegend=False
    )
    
    return html.Div([
        html.H3("📈 Price Chart", className="text-center mb-4"),
        dcc.Graph(figure=fig)
    ], className="card mb-4")

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("🚀 EvolvingTrader - Live Dashboard", className="text-center mb-4"),
        html.Div([
            html.P("Real-time trading statistics and performance monitoring", className="text-center text-muted")
        ])
    ], className="jumbotron"),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    ),
    
    # Main content
    html.Div(id='dashboard-content', className="container-fluid"),
    
    # Footer
    html.Div([
        html.P("Last updated: ", id="last-updated", className="text-center text-muted")
    ], className="mt-4")
])

@app.callback(
    [Output('dashboard-content', 'children'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    """Update dashboard with real data"""
    try:
        # Fetch all data
        data = fetch_api_data('stats')
        
        if not data:
            return html.Div([
                html.H3("❌ Unable to connect to trading system", className="text-center text-danger"),
                html.P("Make sure the trading bot is running and the API server is started", className="text-center")
            ]), "Never"
        
        # Create dashboard sections
        dashboard_content = html.Div([
            create_account_overview(data),
            create_trading_stats(data),
            create_market_data(data),
            create_signals_section(data),
            create_performance_chart(data),
            create_price_chart(data)
        ])
        
        last_updated = data.get('last_updated', 'Unknown')
        if last_updated != 'Unknown':
            try:
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                last_updated = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        return dashboard_content, f"Last updated: {last_updated}"
        
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")
        return html.Div([
            html.H3("❌ Error loading dashboard", className="text-center text-danger"),
            html.P(f"Error: {str(e)}", className="text-center")
        ]), "Error"

def run_dashboard(host: str = "127.0.0.1", port: int = 8050):
    """Run the dashboard"""
    logger.info(f"Starting EvolvingTrader dashboard on {host}:{port}")
    app.run_server(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_dashboard()