"""
Vercel-compatible dashboard for EvolvingTrader
"""
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 EvolvingTrader - Live Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f8f9fa; }
        .card { margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .jumbotron { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
        .stat-card { text-align: center; padding: 1rem; }
        .stat-value { font-size: 2rem; font-weight: bold; }
        .stat-label { color: #6c757d; font-size: 0.9rem; }
        .text-success { color: #28a745 !important; }
        .text-danger { color: #dc3545 !important; }
        .text-warning { color: #ffc107 !important; }
        .text-info { color: #17a2b8 !important; }
        .text-primary { color: #007bff !important; }
        .loading { text-align: center; padding: 2rem; }
        .error { text-align: center; padding: 2rem; color: #dc3545; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="jumbotron">
            <h1 class="text-center">🚀 EvolvingTrader - Live Dashboard</h1>
            <p class="text-center">Real-time trading statistics and performance monitoring</p>
            <p class="text-center">
                <small>Last updated: <span id="last-updated">Loading...</span></small>
            </p>
        </div>

        <div id="loading" class="loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading trading data...</p>
        </div>

        <div id="error" class="error" style="display: none;">
            <h3>❌ Unable to load trading data</h3>
            <p>Make sure your trading bot is running and connected to the internet.</p>
        </div>

        <div id="dashboard-content" style="display: none;">
            <!-- Account Overview -->
            <div class="card">
                <div class="card-header">
                    <h3>💰 Account Overview</h3>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3 stat-card">
                            <div class="stat-value text-primary" id="total-balance">$0.00</div>
                            <div class="stat-label">Total Balance</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value" id="trading-mode">TESTNET</div>
                            <div class="stat-label">Trading Mode</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value" id="can-trade">❌</div>
                            <div class="stat-label">Can Trade</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value text-info" id="current-capital">$0.00</div>
                            <div class="stat-label">Current Capital</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Trading Statistics -->
            <div class="card">
                <div class="card-header">
                    <h3>📊 Trading Statistics</h3>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3 stat-card">
                            <div class="stat-value text-primary" id="total-trades">0</div>
                            <div class="stat-label">Total Trades</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value" id="win-rate">0%</div>
                            <div class="stat-label">Win Rate</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value" id="total-pnl">$0.00</div>
                            <div class="stat-label">Total P&L</div>
                        </div>
                        <div class="col-md-3 stat-card">
                            <div class="stat-value" id="profit-factor">0.00</div>
                            <div class="stat-label">Profit Factor</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Market Data -->
            <div class="card">
                <div class="card-header">
                    <h3>📈 Market Data</h3>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4 stat-card">
                            <div class="stat-value text-primary" id="btc-price">$0.00</div>
                            <div class="stat-label">BTCUSDT Price</div>
                        </div>
                        <div class="col-md-4 stat-card">
                            <div class="stat-value" id="rsi">0.0</div>
                            <div class="stat-label">RSI</div>
                        </div>
                        <div class="col-md-4 stat-card">
                            <div class="stat-value" id="macd">0.0000</div>
                            <div class="stat-label">MACD</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Trading Signals -->
            <div class="card">
                <div class="card-header">
                    <h3>🎯 Trading Signals</h3>
                </div>
                <div class="card-body">
                    <div id="signals-content">
                        <p class="text-center text-muted">No active signals</p>
                    </div>
                </div>
            </div>

            <!-- Performance Chart -->
            <div class="card">
                <div class="card-header">
                    <h3>📊 Performance Chart</h3>
                </div>
                <div class="card-body">
                    <canvas id="performanceChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        let performanceChart = null;

        async function fetchStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.error) {
                    showError();
                    return;
                }
                
                updateDashboard(data);
                hideLoading();
                
            } catch (error) {
                console.error('Error fetching stats:', error);
                showError();
            }
        }

        function updateDashboard(data) {
            // Update account overview
            document.getElementById('total-balance').textContent = `$${data.account.total_balance.toFixed(2)}`;
            document.getElementById('trading-mode').textContent = data.config.testnet ? 'TESTNET' : 'LIVE';
            document.getElementById('trading-mode').className = `stat-value ${data.config.testnet ? 'text-warning' : 'text-danger'}`;
            document.getElementById('can-trade').textContent = data.account.can_trade ? '✅' : '❌';
            document.getElementById('can-trade').className = `stat-value ${data.account.can_trade ? 'text-success' : 'text-danger'}`;
            document.getElementById('current-capital').textContent = `$${data.config.current_capital.toFixed(2)}`;

            // Update trading statistics
            const stats = data.trades.statistics;
            document.getElementById('total-trades').textContent = stats.total_trades;
            document.getElementById('win-rate').textContent = `${stats.win_rate.toFixed(1)}%`;
            document.getElementById('win-rate').className = `stat-value ${stats.win_rate > 50 ? 'text-success' : 'text-danger'}`;
            document.getElementById('total-pnl').textContent = `$${stats.total_pnl.toFixed(2)}`;
            document.getElementById('total-pnl').className = `stat-value ${stats.total_pnl > 0 ? 'text-success' : 'text-danger'}`;
            document.getElementById('profit-factor').textContent = stats.profit_factor.toFixed(2);
            document.getElementById('profit-factor').className = `stat-value ${stats.profit_factor > 1 ? 'text-success' : 'text-danger'}`;

            // Update market data
            document.getElementById('btc-price').textContent = `$${data.market.current_price.toLocaleString()}`;
            document.getElementById('rsi').textContent = data.market.indicators.rsi.toFixed(1);
            document.getElementById('rsi').className = `stat-value ${data.market.indicators.rsi > 70 ? 'text-danger' : data.market.indicators.rsi < 30 ? 'text-success' : 'text-warning'}`;
            document.getElementById('macd').textContent = data.market.indicators.macd.toFixed(4);
            document.getElementById('macd').className = `stat-value ${data.market.indicators.macd > 0 ? 'text-success' : 'text-danger'}`;

            // Update signals
            updateSignals(data.signals.signals);

            // Update performance chart
            updatePerformanceChart(data.trades.trades);

            // Update last updated time
            document.getElementById('last-updated').textContent = new Date(data.last_updated).toLocaleString();
        }

        function updateSignals(signals) {
            const signalsContent = document.getElementById('signals-content');
            
            if (signals.length === 0) {
                signalsContent.innerHTML = '<p class="text-center text-muted">No active signals</p>';
                return;
            }

            let html = '';
            signals.forEach(signal => {
                const colorClass = signal.signal_type === 'BUY' ? 'success' : signal.signal_type === 'SELL' ? 'danger' : 'warning';
                html += `
                    <div class="alert alert-${colorClass}">
                        <h5>${signal.signal_type} Signal</h5>
                        <p><strong>Confidence:</strong> ${signal.confidence.toFixed(2)}</p>
                        <p><strong>Reasoning:</strong> ${signal.reasoning}</p>
                        <p><strong>Entry Price:</strong> $${signal.entry_price.toFixed(2)}</p>
                    </div>
                `;
            });
            
            signalsContent.innerHTML = html;
        }

        function updatePerformanceChart(trades) {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            
            if (performanceChart) {
                performanceChart.destroy();
            }

            if (trades.length === 0) {
                ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
                ctx.fillText('No trades yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
                return;
            }

            // Calculate cumulative P&L
            let cumulativePnl = 0;
            const data = trades.map((trade, index) => {
                cumulativePnl += trade.pnl || 0;
                return {
                    x: index + 1,
                    y: cumulativePnl
                };
            });

            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Cumulative P&L',
                        data: data,
                        borderColor: data[data.length - 1].y > 0 ? 'green' : 'red',
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Trade Number'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'P&L ($)'
                            }
                        }
                    }
                }
            });
        }

        function showError() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error').style.display = 'block';
            document.getElementById('dashboard-content').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('dashboard-content').style.display = 'block';
        }

        // Initial load
        fetchStats();

        // Auto-refresh every 30 seconds
        setInterval(fetchStats, 30000);
    </script>
</body>
</html>
"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(DASHBOARD_HTML.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()