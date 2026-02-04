# TradeForge - Advanced Indian Markets Trading Platform

A comprehensive trading platform for NSE/BSE markets with real-time data, strategy building, backtesting, paper trading, and forward testing capabilities.

## 🚀 Features

### 1. **Real-Time Market Data**
- Live NSE & BSE index prices (NIFTY 50, BANK NIFTY, SENSEX, etc.)
- Real-time derivatives data (Options, Futures)
- Live price updates every 3 seconds
- Volume, High, Low, Open prices

### 2. **Strategy Builder**
- Create custom trading strategies
- Support for multiple strategy types:
  - SMA (Simple Moving Average) Crossover
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
- Configurable parameters (periods, thresholds, position sizing)
- Save and manage multiple strategies

### 3. **Backtesting Engine**
- Test strategies on historical data (up to 5 years)
- Comprehensive performance metrics:
  - Total P&L
  - Win Rate
  - Average Win/Loss
  - Profit Factor
  - Drawdown analysis
- Detailed trade-by-trade breakdown
- Visual performance charts

### 4. **Paper Trading**
- Risk-free trading with virtual money
- Real-time portfolio tracking
- Position management (buy/sell)
- Live P&L calculation
- Starting capital: ₹10,00,000
- Supports all NSE/BSE indices

### 5. **Forward Testing**
- Test strategies on live market data without executing real trades
- Real-time signal generation
- Performance tracking
- Risk assessment

### 6. **Professional UI/UX**
- Dark theme optimized for trading
- Real-time updates
- Responsive design
- Professional charts and visualizations
- Clean, modern interface

## 📋 Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for real-time data

## 🛠️ Installation

### Backend Setup

1. **Clone or download the files**

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the backend server**
```bash
python backend.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. **Open the HTML file**
   - Simply open `trading-platform.html` in your web browser
   - Or serve it using a simple HTTP server:

```bash
# Python 3
python -m http.server 8000

# Then open http://localhost:8000/trading-platform.html
```

## 📊 Usage Guide

### Dashboard
- View real-time market overview
- Monitor NSE/BSE indices
- Track derivatives (options & futures)
- See your portfolio value and P&L

### Creating a Strategy

1. Navigate to **Strategy Builder**
2. Click **Create Strategy**
3. Fill in the details:
   - **Name**: Give your strategy a descriptive name
   - **Type**: Choose strategy type (SMA Crossover, RSI, MACD)
   - **Symbol**: Select index to trade (NIFTY 50, BANK NIFTY, etc.)
   - **Parameters**: Set technical indicator periods
   - **Position Size**: Percentage of capital per trade (1-100%)
   - **Initial Capital**: Starting amount for backtesting
4. Click **Create Strategy**

### Running a Backtest

1. Go to **Backtest** tab
2. Select a strategy from the dropdown
3. Click **Run Backtest**
4. View comprehensive results:
   - Total P&L
   - Win rate
   - Average win/loss
   - All trades with entry/exit dates
   - Performance metrics

### Paper Trading

1. Navigate to **Paper Trading**
2. Click **Start Paper Trading**
3. Place orders:
   - Select symbol
   - Choose Buy/Sell
   - Enter quantity
   - Execute order
4. Monitor positions in real-time
5. Track your portfolio value and P&L

### Forward Testing

1. Go to **Forward Test**
2. Select a strategy
3. Click **Start Forward Test**
4. Monitor live performance on real market data
5. View real-time statistics

## 🔧 Configuration

### Supported Indices

**NSE Indices:**
- NIFTY 50
- NIFTY BANK
- NIFTY IT
- NIFTY AUTO
- NIFTY PHARMA
- NIFTY FMCG
- NIFTY METAL

**BSE Indices:**
- SENSEX
- BSE 100
- BSE 200

### Strategy Types

#### 1. SMA Crossover
- Uses two moving averages (short and long period)
- Buy signal: Short MA crosses above Long MA
- Sell signal: Short MA crosses below Long MA
- Parameters: Short Period, Long Period

#### 2. RSI Strategy
- Uses Relative Strength Index
- Buy signal: RSI crosses above oversold level (default 30)
- Sell signal: RSI crosses below overbought level (default 70)
- Parameters: RSI Period, Oversold Level, Overbought Level

#### 3. MACD Strategy
- Uses MACD line and signal line
- Buy signal: MACD crosses above signal line
- Sell signal: MACD crosses below signal line
- Parameters: Fast Period, Slow Period, Signal Period

## 🔌 API Endpoints

### Market Data

**Get All Indices**
```
GET /api/market/indices
```

**Get Specific Index**
```
GET /api/market/index/<symbol>
```

**Get Historical Data**
```
GET /api/market/historical/<symbol>?period=1y&interval=1d
```

**Get Options Chain**
```
GET /api/market/options/<symbol>
```

### Backtesting

**Run Backtest**
```
POST /api/backtest
Body: {
  "strategy": {
    "name": "My Strategy",
    "type": "sma_crossover",
    "symbol": "NIFTY 50",
    "shortPeriod": 10,
    "longPeriod": 50,
    "positionSize": 10,
    "initialCapital": 1000000
  },
  "period": "1y"
}
```

### Paper Trading

**Execute Paper Trade**
```
POST /api/paper-trade/execute
Body: {
  "symbol": "NIFTY 50",
  "quantity": 1,
  "orderType": "buy"
}
```

### Health Check
```
GET /api/health
```

## 📈 Performance Metrics Explained

- **Total P&L**: Total profit/loss from all trades
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of trades executed
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of losing trades
- **Average Win**: Average profit per winning trade
- **Average Loss**: Average loss per losing trade
- **Profit Factor**: Ratio of total wins to total losses (>1 is profitable)
- **Final Capital**: Ending portfolio value after all trades

## 🎨 Customization

### Modify Trading Rules
Edit the strategy logic in `backend.py`:
- `_backtest_sma_crossover()`: SMA strategy logic
- `_backtest_rsi()`: RSI strategy logic
- `_backtest_macd()`: MACD strategy logic

### Add New Indicators
Use the `TechnicalIndicators` class to add new indicators:
```python
@staticmethod
def add_custom_indicator(df: pd.DataFrame) -> pd.DataFrame:
    # Your indicator logic
    return df
```

### Change UI Theme
Modify CSS variables in `trading-platform.html`:
```css
:root {
    --bg-primary: #0a0e1a;
    --accent-green: #00ff88;
    /* Add your colors */
}
```

## 🔐 Data Sources

- **Market Data**: Yahoo Finance (yfinance)
- **Historical Data**: Up to 5 years of daily data
- **Real-time Updates**: 3-second refresh interval
- **Derivatives**: Options chain from Yahoo Finance

## ⚠️ Important Notes

1. **Paper Trading Only**: This platform is for educational and testing purposes. No real money is involved.

2. **Data Delays**: Free data sources may have 15-20 minute delays. For real-time data, consider premium data providers.

3. **No Financial Advice**: This platform does not provide financial advice. All strategies should be thoroughly tested.

4. **Risk Disclosure**: Past performance does not guarantee future results. Trading involves risk.

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

### No market data showing
- Ensure backend is running
- Check internet connection
- Verify symbol names are correct

### Backtest not working
- Ensure sufficient historical data is available
- Check strategy parameters are valid
- Verify the selected time period has data

## 🚀 Advanced Features (Coming Soon)

- [ ] Multiple timeframe analysis
- [ ] Advanced charting (candlesticks, indicators)
- [ ] Strategy optimization
- [ ] Monte Carlo simulation
- [ ] Portfolio management
- [ ] Risk management tools
- [ ] Alert system
- [ ] Mobile app
- [ ] Social trading features
- [ ] Live broker integration

## 📝 License

This project is for educational purposes. Use at your own risk.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Test with the health check endpoint

## 🎓 Learning Resources

- [Technical Analysis Library](https://technical-analysis-library-in-python.readthedocs.io/)
- [Algorithmic Trading Basics](https://www.investopedia.com/articles/active-trading/101014/basics-algorithmic-trading-concepts-and-examples.asp)
- [NSE India](https://www.nseindia.com/)
- [BSE India](https://www.bseindia.com/)

---

**Happy Trading! 📈💰**

Remember: This is a paper trading platform. Always test strategies thoroughly before considering real money trading.
