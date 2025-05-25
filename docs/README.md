# Algorithmic Trading Strategy Framework

A comprehensive Python-based algorithmic trading system designed for futures and forex markets with advanced risk management, backtesting capabilities, and customizable strategy development.

## 🎯 Features

- **Multi-Asset Support**: ES, NQ, YM futures and AUDUSD, EURUSD, GBPUSD forex pairs
- **Advanced Risk Management**: 0.25% risk per trade, $1.5K max drawdown protection
- **Comprehensive Backtesting**: Historical performance analysis with detailed metrics
- **Technical Analysis**: 20+ built-in indicators with custom indicator support
- **Strategy Framework**: Easily customizable strategy templates
- **Real-time Data**: Free data sources with API integration options
- **Paper Trading**: Safe testing environment before live deployment
- **Performance Analytics**: Detailed reporting and visualization

## 🚀 Quick Start

### 1. One-Click Setup

```bash
# Quick setup (installs everything automatically)
python setup.py
```

### 2. Launch Bloomberg Terminal UI

```bash
# Launch the professional trading interface
python launch_terminal.py
```

**The Bloomberg Terminal-style UI will open at: http://localhost:8501**

### 3. Alternative: Command Line Interface

```python
from trading_system import TradingSystem

# Initialize system
system = TradingSystem(initial_capital=100000, strategy_name="custom")

# Run backtest
results = system.run_backtest(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# View results
print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown_pct']:.2f}%")
```

## 🖥️ Bloomberg Terminal UI

### Features

- **🔥 Professional Interface**: Dark theme with Bloomberg Terminal styling
- **📊 Real-time Dashboard**: Live portfolio metrics and market data
- **🧠 Strategy Editor**: Syntax-highlighted Python code editor
- **📈 Advanced Backtesting**: Interactive charts and performance metrics
- **🛡️ Risk Management**: Position sizing calculator and risk monitoring
- **⚙️ System Settings**: Complete configuration management

### UI Pages

1. **Dashboard**: Real-time portfolio status, signals, and quick actions
2. **Strategy Editor**: Edit and test your trading strategies with live code editor
3. **Backtesting**: Run comprehensive backtests with interactive visualizations
4. **Risk Management**: Monitor risk metrics and calculate position sizes
5. **Settings**: Configure system parameters and data sources

## 📊 Strategy Development

### Built-in Strategies

1. **CustomStrategy**: Template for your personal strategy
2. **MomentumStrategy**: Trend-following approach
3. **MeanReversionStrategy**: Counter-trend approach

### Creating Your Own Strategy

```python
from strategy_framework import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, risk_manager):
        super().__init__("MyStrategy", risk_manager)

    def generate_signals(self, data):
        # Your signal logic here
        signals = []

        for symbol, df in data.items():
            latest = df.iloc[-1]

            # Example: Simple RSI strategy
            if latest['rsi'] < 30:  # Oversold
                signals.append({
                    'symbol': symbol,
                    'direction': 'LONG',
                    'confidence': 0.8,
                    'timestamp': latest.name,
                    'price': latest['close']
                })

        return signals

    def calculate_entry_exit(self, symbol, data, signal):
        latest = data.iloc[-1]
        entry_price = signal['price']
        atr = latest['atr']

        if signal['direction'] == 'LONG':
            stop_loss = entry_price - (atr * 2)
            take_profit = entry_price + (atr * 4)
        else:
            stop_loss = entry_price + (atr * 2)
            take_profit = entry_price - (atr * 4)

        return entry_price, stop_loss, take_profit
```

## 🛡️ Risk Management

The system includes comprehensive risk management:

- **Position Sizing**: Automatic calculation based on 0.25% risk per trade
- **Stop Losses**: ATR-based or technical level stops
- **Drawdown Protection**: Automatic trading halt at $1.5K drawdown
- **Correlation Limits**: Maximum positions per asset class
- **Real-time Monitoring**: Continuous P&L and risk tracking

## 📈 Technical Indicators

Available indicators include:

- **Trend**: SMA, EMA, MACD, Bollinger Bands
- **Momentum**: RSI, Stochastic, Williams %R
- **Volatility**: ATR, Keltner Channels
- **Volume**: OBV, Volume Rate of Change
- **Support/Resistance**: Pivot Points, Fibonacci Levels

## 🔄 Live Trading

### Paper Trading (Recommended)

```python
# Start paper trading
system = TradingSystem(initial_capital=100000)

# Get current signals
signals = system.get_current_signals()

# Execute paper trades
system.execute_live_trading()
```

### Automated Trading

```python
# Schedule automated trading
system.schedule_trading()  # Runs daily at 9 AM
```

## 📊 Performance Analysis

### Backtest Metrics

- Total Return (%)
- Sharpe Ratio
- Maximum Drawdown
- Calmar Ratio
- Win Rate
- Profit Factor
- Average Win/Loss

### Visualization

The system automatically generates:
- Equity curves
- Drawdown charts
- Return distributions
- Rolling performance metrics

## 🔧 Configuration Options

### Risk Parameters

```python
# In config.py
RISK_PER_TRADE = 0.0025  # 0.25%
MAX_DRAWDOWN_USD = 1500  # $1.5K
MAX_POSITIONS = 6        # 3 futures + 3 forex
```

### Instruments

```python
FUTURES_SYMBOLS = ['ES', 'NQ', 'YM']
FOREX_SYMBOLS = ['AUDUSD', 'EURUSD', 'GBPUSD']
```

### Timeframes

```python
PRIMARY_TIMEFRAME = '1d'    # Daily
SECONDARY_TIMEFRAME = '4h'  # 4-hour
```

## 📁 Project Structure

```
trading-strategy/
├── config.py              # Configuration settings
├── data_manager.py        # Data fetching and storage
├── technical_indicators.py # Technical analysis tools
├── risk_manager.py        # Risk management system
├── strategy_framework.py  # Strategy base classes
├── backtesting_engine.py  # Backtesting system
├── trading_system.py      # Main orchestrator
├── example_custom_strategy.py # Strategy example
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🚨 Important Notes

### Risk Disclaimer

- This is for educational and personal use only
- Past performance does not guarantee future results
- Always start with paper trading
- Never risk more than you can afford to lose
- Consider consulting with financial professionals

### Data Sources

- Uses free data from Yahoo Finance (yfinance)
- Optional paid APIs for enhanced data quality
- Real-time data may have delays

### System Requirements

- Python 3.8+
- 4GB+ RAM recommended
- Stable internet connection for data feeds

## 🤝 Customization Examples

See `example_custom_strategy.py` for a detailed example of creating your own strategy with:

- Custom signal conditions
- Multi-timeframe analysis
- Volume confirmation
- Support/resistance levels
- Market regime filtering

## 📞 Support

For questions or issues:

1. Check the example files
2. Review the configuration options
3. Test with paper trading first
4. Start with simple strategies

## 🔄 Updates

The framework is designed to be:
- Modular and extensible
- Easy to customize
- Production-ready for paper trading
- Scalable for multiple strategies

---

**Remember**: Always test thoroughly with paper trading before considering any live implementation. This system is designed for educational purposes and personal use.
