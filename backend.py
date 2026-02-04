"""
TradeForge - Indian Markets Trading Platform Backend
Supports NSE/BSE real-time data, backtesting, paper trading, and forward testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta
import json
import requests
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# Configuration
NSE_INDICES = {
    'NIFTY 50': '^NSEI',
    'NIFTY BANK': '^NSEBANK',
    'NIFTY IT': '^CNXIT',
    'NIFTY AUTO': '^CNXAUTO',
    'NIFTY PHARMA': '^CNXPHARMA',
    'NIFTY FMCG': '^CNXFMCG',
    'NIFTY METAL': '^CNXMETAL',
}

BSE_INDICES = {
    'SENSEX': '^BSESN',
    'BSE 100': '^BSE100',
    'BSE 200': '^BSE200',
}

ALL_INDICES = {**NSE_INDICES, **BSE_INDICES}


class MarketDataProvider:
    """Fetches real-time and historical data from NSE/BSE"""
    
    @staticmethod
    def get_real_time_data(symbols: List[str]) -> List[Dict]:
        """Fetch real-time data for given symbols"""
        data = []
        
        for symbol in symbols:
            try:
                ticker_symbol = ALL_INDICES.get(symbol)
                if not ticker_symbol:
                    continue
                
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info
                hist = ticker.history(period='2d')
                
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100
                    
                    data.append({
                        'symbol': symbol,
                        'price': round(current_price, 2),
                        'change': round(change, 2),
                        'changePercent': round(change_percent, 2),
                        'volume': int(hist['Volume'].iloc[-1]),
                        'high': round(hist['High'].iloc[-1], 2),
                        'low': round(hist['Low'].iloc[-1], 2),
                        'open': round(hist['Open'].iloc[-1], 2),
                        'exchange': 'NSE' if symbol in NSE_INDICES else 'BSE',
                    })
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                continue
        
        return data
    
    @staticmethod
    def get_historical_data(symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """Fetch historical data for backtesting"""
        ticker_symbol = ALL_INDICES.get(symbol)
        if not ticker_symbol:
            return pd.DataFrame()
        
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period, interval=interval)
        
        return hist
    
    @staticmethod
    def get_options_chain(symbol: str) -> Dict:
        """Fetch options chain data (derivatives)"""
        # Note: Real options data requires NSE API or paid data providers
        # This is a simplified example
        ticker_symbol = ALL_INDICES.get(symbol)
        if not ticker_symbol:
            return {}
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            options_dates = ticker.options
            
            if len(options_dates) > 0:
                expiry = options_dates[0]
                options = ticker.option_chain(expiry)
                
                calls = options.calls.head(10).to_dict('records')
                puts = options.puts.head(10).to_dict('records')
                
                return {
                    'calls': calls,
                    'puts': puts,
                    'expiry': expiry,
                }
        except Exception as e:
            print(f"Error fetching options for {symbol}: {e}")
        
        return {}


class TechnicalIndicators:
    """Calculate technical indicators for strategies"""
    
    @staticmethod
    def add_sma(df: pd.DataFrame, period: int, column: str = 'Close') -> pd.DataFrame:
        """Add Simple Moving Average"""
        df[f'SMA_{period}'] = ta.trend.sma_indicator(df[column], window=period)
        return df
    
    @staticmethod
    def add_ema(df: pd.DataFrame, period: int, column: str = 'Close') -> pd.DataFrame:
        """Add Exponential Moving Average"""
        df[f'EMA_{period}'] = ta.trend.ema_indicator(df[column], window=period)
        return df
    
    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14, column: str = 'Close') -> pd.DataFrame:
        """Add Relative Strength Index"""
        df['RSI'] = ta.momentum.rsi(df[column], window=period)
        return df
    
    @staticmethod
    def add_macd(df: pd.DataFrame, column: str = 'Close') -> pd.DataFrame:
        """Add MACD indicator"""
        macd = ta.trend.MACD(df[column])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        return df
    
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, period: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Add Bollinger Bands"""
        bollinger = ta.volatility.BollingerBands(df[column], window=period)
        df['BB_upper'] = bollinger.bollinger_hband()
        df['BB_middle'] = bollinger.bollinger_mavg()
        df['BB_lower'] = bollinger.bollinger_lband()
        return df


class BacktestEngine:
    """Backtesting engine for strategy validation"""
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
    
    def run_backtest(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Execute backtest with given strategy"""
        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        
        strategy_type = strategy.get('type', 'sma_crossover')
        
        if strategy_type == 'sma_crossover':
            return self._backtest_sma_crossover(strategy, data)
        elif strategy_type == 'rsi':
            return self._backtest_rsi(strategy, data)
        elif strategy_type == 'macd':
            return self._backtest_macd(strategy, data)
        else:
            return {'error': 'Unknown strategy type'}
    
    def _backtest_sma_crossover(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Backtest SMA crossover strategy"""
        short_period = strategy.get('shortPeriod', 10)
        long_period = strategy.get('longPeriod', 50)
        position_size = strategy.get('positionSize', 10) / 100
        
        # Add indicators
        data = TechnicalIndicators.add_sma(data, short_period)
        data = TechnicalIndicators.add_sma(data, long_period)
        
        data = data.dropna()
        position = None
        
        for i in range(1, len(data)):
            current_row = data.iloc[i]
            prev_row = data.iloc[i-1]
            
            short_sma = current_row[f'SMA_{short_period}']
            long_sma = current_row[f'SMA_{long_period}']
            prev_short_sma = prev_row[f'SMA_{short_period}']
            prev_long_sma = prev_row[f'SMA_{long_period}']
            
            # Buy signal
            if not position and short_sma > long_sma and prev_short_sma <= prev_long_sma:
                quantity = int((self.capital * position_size) / current_row['Close'])
                if quantity > 0:
                    position = {
                        'entry_price': current_row['Close'],
                        'quantity': quantity,
                        'entry_date': current_row.name,
                    }
            
            # Sell signal
            elif position and short_sma < long_sma and prev_short_sma >= prev_long_sma:
                pnl = (current_row['Close'] - position['entry_price']) * position['quantity']
                self.capital += pnl
                
                self.trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(current_row.name),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(current_row['Close']),
                    'quantity': position['quantity'],
                    'pnl': float(pnl),
                    'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
                })
                
                position = None
        
        # Close any open position
        if position:
            last_row = data.iloc[-1]
            pnl = (last_row['Close'] - position['entry_price']) * position['quantity']
            self.capital += pnl
            
            self.trades.append({
                'entry_date': str(position['entry_date']),
                'exit_date': str(last_row.name),
                'entry_price': float(position['entry_price']),
                'exit_price': float(last_row['Close']),
                'quantity': position['quantity'],
                'pnl': float(pnl),
                'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
            })
        
        return self._calculate_metrics()
    
    def _backtest_rsi(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Backtest RSI strategy"""
        rsi_period = strategy.get('rsiPeriod', 14)
        oversold = strategy.get('oversold', 30)
        overbought = strategy.get('overbought', 70)
        position_size = strategy.get('positionSize', 10) / 100
        
        data = TechnicalIndicators.add_rsi(data, rsi_period)
        data = data.dropna()
        
        position = None
        
        for i in range(1, len(data)):
            current_row = data.iloc[i]
            prev_row = data.iloc[i-1]
            
            # Buy signal (RSI crosses above oversold)
            if not position and current_row['RSI'] > oversold and prev_row['RSI'] <= oversold:
                quantity = int((self.capital * position_size) / current_row['Close'])
                if quantity > 0:
                    position = {
                        'entry_price': current_row['Close'],
                        'quantity': quantity,
                        'entry_date': current_row.name,
                    }
            
            # Sell signal (RSI crosses below overbought)
            elif position and current_row['RSI'] < overbought and prev_row['RSI'] >= overbought:
                pnl = (current_row['Close'] - position['entry_price']) * position['quantity']
                self.capital += pnl
                
                self.trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(current_row.name),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(current_row['Close']),
                    'quantity': position['quantity'],
                    'pnl': float(pnl),
                    'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
                })
                
                position = None
        
        # Close any open position
        if position:
            last_row = data.iloc[-1]
            pnl = (last_row['Close'] - position['entry_price']) * position['quantity']
            self.capital += pnl
            
            self.trades.append({
                'entry_date': str(position['entry_date']),
                'exit_date': str(last_row.name),
                'entry_price': float(position['entry_price']),
                'exit_price': float(last_row['Close']),
                'quantity': position['quantity'],
                'pnl': float(pnl),
                'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
            })
        
        return self._calculate_metrics()
    
    def _backtest_macd(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Backtest MACD strategy"""
        position_size = strategy.get('positionSize', 10) / 100
        
        data = TechnicalIndicators.add_macd(data)
        data = data.dropna()
        
        position = None
        
        for i in range(1, len(data)):
            current_row = data.iloc[i]
            prev_row = data.iloc[i-1]
            
            # Buy signal (MACD crosses above signal)
            if not position and current_row['MACD'] > current_row['MACD_signal'] and prev_row['MACD'] <= prev_row['MACD_signal']:
                quantity = int((self.capital * position_size) / current_row['Close'])
                if quantity > 0:
                    position = {
                        'entry_price': current_row['Close'],
                        'quantity': quantity,
                        'entry_date': current_row.name,
                    }
            
            # Sell signal (MACD crosses below signal)
            elif position and current_row['MACD'] < current_row['MACD_signal'] and prev_row['MACD'] >= prev_row['MACD_signal']:
                pnl = (current_row['Close'] - position['entry_price']) * position['quantity']
                self.capital += pnl
                
                self.trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(current_row.name),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(current_row['Close']),
                    'quantity': position['quantity'],
                    'pnl': float(pnl),
                    'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
                })
                
                position = None
        
        # Close any open position
        if position:
            last_row = data.iloc[-1]
            pnl = (last_row['Close'] - position['entry_price']) * position['quantity']
            self.capital += pnl
            
            self.trades.append({
                'entry_date': str(position['entry_date']),
                'exit_date': str(last_row.name),
                'entry_price': float(position['entry_price']),
                'exit_price': float(last_row['Close']),
                'quantity': position['quantity'],
                'pnl': float(pnl),
                'pnl_percent': float((pnl / (position['entry_price'] * position['quantity'])) * 100),
            })
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'finalCapital': self.initial_capital,
                'totalPnL': 0,
                'totalTrades': 0,
                'winningTrades': 0,
                'losingTrades': 0,
                'winRate': 0,
                'avgWin': 0,
                'avgLoss': 0,
                'profitFactor': 0,
                'trades': [],
            }
        
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / len(self.trades)) * 100 if self.trades else 0
        
        avg_win = sum(t['pnl'] for t in winning_trades) / win_count if win_count > 0 else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / loss_count if loss_count > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            'finalCapital': float(self.capital),
            'totalPnL': float(total_pnl),
            'totalTrades': len(self.trades),
            'winningTrades': win_count,
            'losingTrades': loss_count,
            'winRate': float(win_rate),
            'avgWin': float(avg_win),
            'avgLoss': float(avg_loss),
            'profitFactor': float(profit_factor),
            'trades': self.trades,
        }


# API Routes

@app.route('/api/market/indices', methods=['GET'])
def get_indices():
    """Get real-time index data"""
    symbols = list(NSE_INDICES.keys()) + list(BSE_INDICES.keys())
    data = MarketDataProvider.get_real_time_data(symbols)
    return jsonify(data)


@app.route('/api/market/index/<symbol>', methods=['GET'])
def get_index_data(symbol):
    """Get specific index data"""
    data = MarketDataProvider.get_real_time_data([symbol])
    if data:
        return jsonify(data[0])
    return jsonify({'error': 'Symbol not found'}), 404


@app.route('/api/market/historical/<symbol>', methods=['GET'])
def get_historical(symbol):
    """Get historical data for backtesting"""
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    data = MarketDataProvider.get_historical_data(symbol, period, interval)
    
    if data.empty:
        return jsonify({'error': 'No data found'}), 404
    
    # Convert to JSON-serializable format
    data_dict = data.reset_index().to_dict('records')
    
    # Convert Timestamp to string
    for row in data_dict:
        row['Date'] = str(row['Date'])
    
    return jsonify(data_dict)


@app.route('/api/market/options/<symbol>', methods=['GET'])
def get_options(symbol):
    """Get options chain data"""
    data = MarketDataProvider.get_options_chain(symbol)
    return jsonify(data)


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest on strategy"""
    strategy = request.json.get('strategy')
    symbol = strategy.get('symbol', 'NIFTY 50')
    period = request.json.get('period', '1y')
    
    # Get historical data
    historical_data = MarketDataProvider.get_historical_data(symbol, period)
    
    if historical_data.empty:
        return jsonify({'error': 'No historical data available'}), 400
    
    # Run backtest
    engine = BacktestEngine(initial_capital=strategy.get('initialCapital', 1000000))
    results = engine.run_backtest(strategy, historical_data)
    
    return jsonify(results)


@app.route('/api/strategy/validate', methods=['POST'])
def validate_strategy():
    """Validate strategy configuration"""
    strategy = request.json
    
    required_fields = ['name', 'type', 'symbol', 'positionSize', 'initialCapital']
    
    for field in required_fields:
        if field not in strategy:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    return jsonify({'valid': True})


@app.route('/api/paper-trade/execute', methods=['POST'])
def execute_paper_trade():
    """Execute a paper trade"""
    order = request.json
    
    # Validate order
    if 'symbol' not in order or 'quantity' not in order or 'orderType' not in order:
        return jsonify({'error': 'Invalid order'}), 400
    
    # Get current price
    data = MarketDataProvider.get_real_time_data([order['symbol']])
    
    if not data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    current_price = data[0]['price']
    
    result = {
        'success': True,
        'orderType': order['orderType'],
        'symbol': order['symbol'],
        'quantity': order['quantity'],
        'price': current_price,
        'total': current_price * order['quantity'],
        'timestamp': datetime.now().isoformat(),
    }
    
    return jsonify(result)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
    })


if __name__ == '__main__':
    print("TradeForge Backend Starting...")
    print("Available Indices:", list(ALL_INDICES.keys()))
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
