"""
Configuration file for algorithmic trading strategy
"""
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TradingConfig:
    """Main trading configuration"""

    # Risk Management
    RISK_PER_TRADE = 0.0025  # 0.25% per trade
    MAX_DRAWDOWN_USD = 1500  # $1.5K max drawdown
    MAX_POSITIONS = 6  # Max simultaneous positions (3 futures + 3 forex)

    # Instruments
    FUTURES_SYMBOLS = ['ES', 'NQ', 'YM']  # E-mini S&P 500, Nasdaq, Dow
    FOREX_SYMBOLS = ['AUDUSD', 'EURUSD', 'GBPUSD']

    # Timeframes
    PRIMARY_TIMEFRAME = '1d'  # Daily
    SECONDARY_TIMEFRAME = '4h'  # 4-hour

    # Data Sources
    DATA_PROVIDER = 'yfinance'  # Free data source
    BACKUP_PROVIDER = 'alpha_vantage'

    # Strategy Parameters (customize these)
    LOOKBACK_PERIOD = 20  # Days for technical indicators
    VOLATILITY_WINDOW = 14  # ATR calculation window

    # Execution
    PAPER_TRADING = True  # Start with paper trading
    SLIPPAGE_BPS = 2  # 2 basis points slippage assumption
    COMMISSION_USD = 2.50  # Per futures contract
    COMMISSION_FOREX_BPS = 1  # 1 basis point for forex

    # Database
    DATABASE_PATH = 'trading_data.db'

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'trading_strategy.log'

    # ICT Strategy Configuration
    ICT_TRADING_STYLE = 'day_trading'  # Options: 'scalping', 'day_trading', 'swing_trading', 'position_trading'
    ICT_ASSET_TYPE = 'forex'  # Options: 'forex', 'stocks', 'crypto', 'indices'
    ICT_PO3_AUTO_SIZE = True  # Automatically determine optimal PO3 size
    ICT_DEFAULT_PO3_SIZE = 81  # Default PO3 size if auto-sizing fails
    ICT_CONFLUENCE_THRESHOLD = 0.6  # Minimum confluence score for signals
    ICT_ENABLE_HIPPO = True  # Enable HIPPO pattern analysis
    ICT_ENABLE_AMD = True  # Enable AMD cycle analysis
    ICT_ENABLE_GOLDBACH = True  # Enable Goldbach level analysis
    ICT_MAX_DAILY_TRADES = 3  # Maximum trades per day for ICT strategy
    ICT_RISK_PER_TRADE = 0.02  # 2% risk per trade for ICT

@dataclass
class InstrumentConfig:
    """Configuration for specific instruments"""

    # Futures contract specifications
    FUTURES_SPECS = {
        'ES': {
            'tick_size': 0.25,
            'tick_value': 12.50,
            'margin_requirement': 13200,  # Approximate
            'trading_hours': '17:00-16:00 CT'
        },
        'NQ': {
            'tick_size': 0.25,
            'tick_value': 5.00,
            'margin_requirement': 17600,
            'trading_hours': '17:00-16:00 CT'
        },
        'YM': {
            'tick_size': 1.0,
            'tick_value': 5.00,
            'margin_requirement': 8800,
            'trading_hours': '17:00-16:00 CT'
        }
    }

    # Forex specifications
    FOREX_SPECS = {
        'AUDUSD': {
            'pip_value': 0.0001,
            'spread_typical': 1.5,  # pips
            'trading_hours': '24/5'
        },
        'EURUSD': {
            'pip_value': 0.0001,
            'spread_typical': 1.0,
            'trading_hours': '24/5'
        },
        'GBPUSD': {
            'pip_value': 0.0001,
            'spread_typical': 1.5,
            'trading_hours': '24/5'
        }
    }

# Environment variables (create .env file)
API_KEYS = {
    'ALPHA_VANTAGE_KEY': os.getenv('ALPHA_VANTAGE_KEY', ''),
    'FRED_API_KEY': os.getenv('FRED_API_KEY', ''),
}

# Initialize configurations
trading_config = TradingConfig()
instrument_config = InstrumentConfig()
