"""
Market Data API Integration for Symbol Lookup and Real-time Data
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import time

@dataclass
class SymbolInfo:
    """Symbol information structure"""
    symbol: str
    name: str
    exchange: str
    currency: str
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

class MarketDataAPI:
    """Comprehensive market data API integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AlgoTrading/1.0'
        })
        
        # Symbol mappings for different asset classes
        self.futures_mapping = {
            'ES': 'ES=F',    # E-mini S&P 500
            'NQ': 'NQ=F',    # E-mini Nasdaq
            'YM': 'YM=F',    # E-mini Dow
            'RTY': 'RTY=F',  # E-mini Russell 2000
            'CL': 'CL=F',    # Crude Oil
            'GC': 'GC=F',    # Gold
            'SI': 'SI=F',    # Silver
            'NG': 'NG=F',    # Natural Gas
            'ZB': 'ZB=F',    # 30-Year Treasury Bond
            'ZN': 'ZN=F',    # 10-Year Treasury Note
        }
        
        self.forex_mapping = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'AUDUSD': 'AUDUSD=X',
            'USDJPY': 'USDJPY=X',
            'USDCAD': 'USDCAD=X',
            'USDCHF': 'USDCHF=X',
            'NZDUSD': 'NZDUSD=X',
            'EURGBP': 'EURGBP=X',
            'EURJPY': 'EURJPY=X',
            'GBPJPY': 'GBPJPY=X',
        }
        
        # Popular symbols for quick access
        self.popular_symbols = {
            'Stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'SPY', 'QQQ'],
            'Futures': list(self.futures_mapping.keys()),
            'Forex': list(self.forex_mapping.keys()),
            'Crypto': ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD'],
            'Commodities': ['GLD', 'SLV', 'USO', 'UNG', 'DBA'],
            'Indices': ['^GSPC', '^IXIC', '^DJI', '^RUT', '^VIX']
        }
    
    def search_symbols(self, query: str, limit: int = 20) -> List[SymbolInfo]:
        """Search for symbols using multiple methods"""
        results = []
        
        # Method 1: Direct symbol lookup
        if len(query) <= 6:
            direct_result = self._get_symbol_info(query.upper())
            if direct_result:
                results.append(direct_result)
        
        # Method 2: Search in popular symbols
        query_lower = query.lower()
        for category, symbols in self.popular_symbols.items():
            for symbol in symbols:
                if query_lower in symbol.lower():
                    symbol_info = self._get_symbol_info(symbol)
                    if symbol_info and symbol_info not in results:
                        results.append(symbol_info)
        
        # Method 3: Yahoo Finance search (fallback)
        try:
            yf_results = self._yahoo_search(query, limit - len(results))
            results.extend(yf_results)
        except Exception as e:
            self.logger.warning(f"Yahoo search failed: {e}")
        
        return results[:limit]
    
    def _get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """Get detailed information for a specific symbol"""
        try:
            # Map futures and forex symbols
            yf_symbol = self._map_symbol(symbol)
            
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Get current price data
            hist = ticker.history(period='1d', interval='1m')
            current_price = None
            change = None
            change_percent = None
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                if len(hist) > 1:
                    prev_close = float(hist['Close'].iloc[0])
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100
            
            return SymbolInfo(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                exchange=info.get('exchange', 'Unknown'),
                currency=info.get('currency', 'USD'),
                market_cap=info.get('marketCap'),
                sector=info.get('sector'),
                industry=info.get('industry'),
                price=current_price,
                change=change,
                change_percent=change_percent
            )
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def _map_symbol(self, symbol: str) -> str:
        """Map symbol to Yahoo Finance format"""
        symbol_upper = symbol.upper()
        
        # Check futures mapping
        if symbol_upper in self.futures_mapping:
            return self.futures_mapping[symbol_upper]
        
        # Check forex mapping
        if symbol_upper in self.forex_mapping:
            return self.forex_mapping[symbol_upper]
        
        # Return as-is for stocks and other symbols
        return symbol
    
    def _yahoo_search(self, query: str, limit: int) -> List[SymbolInfo]:
        """Search using Yahoo Finance (simplified)"""
        results = []
        
        # This is a simplified search - in production you might use
        # a dedicated search API or scraping service
        common_suffixes = ['', '.TO', '.L', '.PA', '.DE', '.HK']
        
        for suffix in common_suffixes:
            if len(results) >= limit:
                break
                
            test_symbol = f"{query.upper()}{suffix}"
            symbol_info = self._get_symbol_info(test_symbol)
            
            if symbol_info and symbol_info.price is not None:
                results.append(symbol_info)
        
        return results
    
    def get_market_data(self, symbol: str, period: str = '1d', 
                       interval: str = '1m') -> Optional[pd.DataFrame]:
        """Get market data for a symbol"""
        try:
            yf_symbol = self._map_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Get historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            # Clean and standardize data
            data.columns = [col.lower() for col in data.columns]
            data = data.dropna()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        try:
            yf_symbol = self._map_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Get latest data
            hist = ticker.history(period='1d', interval='1m')
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            
            # Calculate change from previous close
            info = ticker.info
            prev_close = info.get('previousClose', latest['Close'])
            
            change = latest['Close'] - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return {
                'symbol': symbol,
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'change': float(change),
                'change_percent': float(change_percent),
                'timestamp': latest.name,
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time quote for {symbol}: {e}")
            return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get real-time quotes for multiple symbols"""
        quotes = {}
        
        for symbol in symbols:
            quote = self.get_real_time_quote(symbol)
            if quote:
                quotes[symbol] = quote
            else:
                # Add placeholder for failed symbols
                quotes[symbol] = {
                    'symbol': symbol,
                    'price': None,
                    'change': None,
                    'change_percent': None,
                    'error': 'Failed to fetch data'
                }
        
        return quotes
    
    def get_market_movers(self, category: str = 'stocks') -> List[Dict]:
        """Get market movers for a category"""
        try:
            if category == 'stocks':
                symbols = ['SPY', 'QQQ', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            elif category == 'futures':
                symbols = list(self.futures_mapping.keys())[:8]
            elif category == 'forex':
                symbols = list(self.forex_mapping.keys())[:8]
            elif category == 'crypto':
                symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD']
            else:
                symbols = ['SPY', 'QQQ', 'IWM', 'VIX']
            
            quotes = self.get_multiple_quotes(symbols)
            
            # Sort by absolute change percent
            movers = []
            for symbol, quote in quotes.items():
                if quote.get('change_percent') is not None:
                    movers.append(quote)
            
            movers.sort(key=lambda x: abs(x.get('change_percent', 0)), reverse=True)
            
            return movers[:10]
            
        except Exception as e:
            self.logger.error(f"Error getting market movers: {e}")
            return []
    
    def get_symbol_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Get fundamental data for a symbol"""
        try:
            yf_symbol = self._map_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            if not info:
                return None
            
            fundamentals = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'enterprise_value': info.get('enterpriseValue'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue': info.get('totalRevenue'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'insider_percent': info.get('heldPercentInsiders'),
                'institution_percent': info.get('heldPercentInstitutions')
            }
            
            # Remove None values
            fundamentals = {k: v for k, v in fundamentals.items() if v is not None}
            
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"Error getting fundamentals for {symbol}: {e}")
            return None
    
    def get_options_chain(self, symbol: str) -> Optional[Dict]:
        """Get options chain for a symbol"""
        try:
            yf_symbol = self._map_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            
            if not expirations:
                return None
            
            # Get options for the nearest expiration
            nearest_exp = expirations[0]
            options = ticker.option_chain(nearest_exp)
            
            return {
                'expiration': nearest_exp,
                'calls': options.calls.to_dict('records'),
                'puts': options.puts.to_dict('records'),
                'available_expirations': list(expirations)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting options chain for {symbol}: {e}")
            return None
