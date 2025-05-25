"""
Data Manager for fetching and managing market data
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import logging
from typing import Dict, List, Optional
from config.config import trading_config, instrument_config

class DataManager:
    """Handles data fetching, storage, and retrieval"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = trading_config.DATABASE_PATH
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for storing market data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables for price data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT,
                timestamp DATETIME,
                timeframe TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (symbol, timestamp, timeframe)
            )
        ''')

        # Create table for strategy signals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp DATETIME,
                signal_type TEXT,
                price REAL,
                confidence REAL,
                strategy_name TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_futures_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch futures data using yfinance"""
        try:
            # Map our symbols to yfinance tickers
            ticker_map = {
                'ES': 'ES=F',  # E-mini S&P 500
                'NQ': 'NQ=F',  # E-mini Nasdaq
                'YM': 'YM=F'   # E-mini Dow
            }

            ticker = ticker_map.get(symbol, symbol)
            data = yf.download(ticker, period=period, interval=interval, progress=False)

            if data.empty:
                self.logger.warning(f"No data retrieved for {symbol}")
                return pd.DataFrame()

            # Clean and standardize data
            data = data.dropna()

            # Handle multi-level columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            # Convert column names to lowercase
            data.columns = [col.lower() if isinstance(col, str) else str(col).lower() for col in data.columns]

            # Store in database
            self._store_price_data(symbol, data, interval)

            return data

        except Exception as e:
            self.logger.error(f"Error fetching futures data for {symbol}: {e}")
            return pd.DataFrame()

    def get_forex_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch forex data using yfinance"""
        try:
            # Format forex symbols for yfinance
            ticker = f"{symbol}=X"
            data = yf.download(ticker, period=period, interval=interval, progress=False)

            if data.empty:
                self.logger.warning(f"No data retrieved for {symbol}")
                return pd.DataFrame()

            # Clean and standardize data
            data = data.dropna()

            # Handle multi-level columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            # Convert column names to lowercase
            data.columns = [col.lower() if isinstance(col, str) else str(col).lower() for col in data.columns]

            # Store in database
            self._store_price_data(symbol, data, interval)

            return data

        except Exception as e:
            self.logger.error(f"Error fetching forex data for {symbol}: {e}")
            return pd.DataFrame()

    def get_all_instruments_data(self, period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch data for all configured instruments"""
        all_data = {}

        # Fetch futures data
        for symbol in trading_config.FUTURES_SYMBOLS:
            self.logger.info(f"Fetching futures data for {symbol}")
            all_data[symbol] = self.get_futures_data(symbol, period, interval)

        # Fetch forex data
        for symbol in trading_config.FOREX_SYMBOLS:
            self.logger.info(f"Fetching forex data for {symbol}")
            all_data[symbol] = self.get_forex_data(symbol, period, interval)

        return all_data

    def _store_price_data(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Store price data in database"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Prepare data for insertion
            data_to_store = data.copy()
            data_to_store['symbol'] = symbol
            data_to_store['timeframe'] = timeframe
            data_to_store['timestamp'] = data_to_store.index

            # Select relevant columns
            columns = ['symbol', 'timestamp', 'timeframe', 'open', 'high', 'low', 'close', 'volume']
            data_to_store = data_to_store[columns]

            # Insert or replace data
            data_to_store.to_sql('price_data', conn, if_exists='replace', index=False)

            conn.close()
            self.logger.info(f"Stored {len(data_to_store)} records for {symbol}")

        except Exception as e:
            self.logger.error(f"Error storing data for {symbol}: {e}")

    def get_stored_data(self, symbol: str, timeframe: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """Retrieve stored data from database"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = "SELECT * FROM price_data WHERE symbol = ? AND timeframe = ?"
            params = [symbol, timeframe]

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            query += " ORDER BY timestamp"

            data = pd.read_sql_query(query, conn, params=params)
            conn.close()

            if not data.empty:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data.set_index('timestamp', inplace=True)

            return data

        except Exception as e:
            self.logger.error(f"Error retrieving stored data: {e}")
            return pd.DataFrame()

    def update_data(self):
        """Update all instrument data"""
        self.logger.info("Starting data update...")

        # Update daily data
        daily_data = self.get_all_instruments_data(period="1y", interval="1d")

        # Update 4-hour data
        hourly_data = self.get_all_instruments_data(period="60d", interval="4h")

        self.logger.info("Data update completed")

        return daily_data, hourly_data
