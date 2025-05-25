# Trading Core Infrastructure

This folder contains the core trading system infrastructure and framework components.

## Files Overview

### Main System
- **`trading_system.py`** - Main trading system orchestrator that coordinates all components
- **`strategy_framework.py`** - Base strategy classes and framework for creating custom strategies

### Core Components
- **`backtesting_engine.py`** - Backtesting engine for strategy performance analysis
- **`risk_manager.py`** - Risk management and position sizing calculations
- **`data_manager.py`** - Data acquisition, storage, and management
- **`market_data_api.py`** - Market data API interfaces and connections
- **`enhanced_market_data.py`** - Enhanced data processing and enrichment
- **`technical_indicators.py`** - Technical analysis indicators and calculations

## Architecture

```
TradingSystem (Main Orchestrator)
├── DataManager (Data handling)
├── RiskManager (Risk control)
├── BacktestEngine (Performance analysis)
└── Strategy (ICT or Custom)
    └── TechnicalIndicators (Analysis tools)
```

## Quick Usage

```python
from trading_core.trading_system import TradingSystem

# Initialize trading system
system = TradingSystem(
    initial_capital=100000,
    strategy_name="ict"  # or "custom", "momentum", "mean_reversion"
)

# Run backtest
results = system.run_backtest(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# Execute live trading (paper mode)
system.execute_live_trading()
```

## Key Features

### TradingSystem
- Strategy orchestration and execution
- Live trading and paper trading modes
- Portfolio management and tracking
- Signal processing and execution

### Strategy Framework
- Abstract base class for all strategies
- Built-in strategy templates (Custom, Momentum, Mean Reversion)
- Signal generation and validation
- Entry/exit calculation methods

### Risk Management
- Position sizing based on account equity
- Stop-loss and take-profit calculations
- Maximum drawdown protection
- Risk-per-trade controls

### Data Management
- Multi-source data acquisition (Yahoo Finance, Alpha Vantage)
- Real-time and historical data handling
- Data caching and storage
- Multiple asset class support (Forex, Stocks, Futures)

## Dependencies

- pandas, numpy - Data manipulation
- yfinance - Yahoo Finance data
- requests - API calls
- sqlite3 - Data storage
- logging - System logging
