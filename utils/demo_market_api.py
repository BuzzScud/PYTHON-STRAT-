#!/usr/bin/env python3
"""
Demo script for Market Data API functionality
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_core.market_data_api import MarketDataAPI

def demo_symbol_search():
    """Demo symbol search functionality"""
    print("🔍 SYMBOL SEARCH DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    # Test searches
    test_queries = ['AAPL', 'Tesla', 'ES', 'EURUSD', 'Bitcoin']
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = api.search_symbols(query, limit=3)
        
        if results:
            for symbol_info in results:
                price_str = f"${symbol_info.price:.2f}" if symbol_info.price else "N/A"
                change_str = f"{symbol_info.change_percent:+.2f}%" if symbol_info.change_percent else "N/A"
                
                print(f"  📊 {symbol_info.symbol} - {symbol_info.name[:30]}...")
                print(f"      Price: {price_str} | Change: {change_str} | Exchange: {symbol_info.exchange}")
        else:
            print(f"  ❌ No results found for '{query}'")

def demo_real_time_quotes():
    """Demo real-time quotes"""
    print("\n📈 REAL-TIME QUOTES DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'ES', 'NQ', 'EURUSD', 'GBPUSD', 'BTC-USD']
    
    print("Fetching real-time quotes...")
    quotes = api.get_multiple_quotes(symbols)
    
    print(f"\n{'Symbol':<10} {'Price':<12} {'Change':<10} {'Change %':<10} {'Volume':<15}")
    print("-" * 65)
    
    for symbol, quote in quotes.items():
        if quote.get('price') is not None:
            price = f"${quote['price']:.2f}"
            change = f"{quote.get('change', 0):+.2f}"
            change_pct = f"{quote.get('change_percent', 0):+.2f}%"
            volume = f"{quote.get('volume', 0):,}"
            
            print(f"{symbol:<10} {price:<12} {change:<10} {change_pct:<10} {volume:<15}")
        else:
            print(f"{symbol:<10} {'ERROR':<12} {'N/A':<10} {'N/A':<10} {'N/A':<15}")

def demo_market_data():
    """Demo market data fetching"""
    print("\n📊 MARKET DATA DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    # Test symbol
    symbol = 'AAPL'
    print(f"Fetching 5-day hourly data for {symbol}...")
    
    data = api.get_market_data(symbol, period='5d', interval='1h')
    
    if data is not None and not data.empty:
        print(f"✅ Successfully fetched {len(data)} data points")
        print(f"Date range: {data.index[0]} to {data.index[-1]}")
        print(f"Latest close: ${data['close'].iloc[-1]:.2f}")
        print(f"5-day high: ${data['high'].max():.2f}")
        print(f"5-day low: ${data['low'].min():.2f}")
        print(f"Average volume: {data['volume'].mean():,.0f}")
    else:
        print(f"❌ Failed to fetch data for {symbol}")

def demo_fundamentals():
    """Demo fundamentals data"""
    print("\n📋 FUNDAMENTALS DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'TSLA']
    
    for symbol in symbols:
        print(f"\nFundamentals for {symbol}:")
        fundamentals = api.get_symbol_fundamentals(symbol)
        
        if fundamentals:
            # Display key metrics
            if 'market_cap' in fundamentals:
                print(f"  Market Cap: ${fundamentals['market_cap']/1e9:.1f}B")
            if 'pe_ratio' in fundamentals:
                print(f"  P/E Ratio: {fundamentals['pe_ratio']:.2f}")
            if 'dividend_yield' in fundamentals:
                print(f"  Dividend Yield: {fundamentals['dividend_yield']*100:.2f}%")
            if 'beta' in fundamentals:
                print(f"  Beta: {fundamentals['beta']:.2f}")
            if 'profit_margins' in fundamentals:
                print(f"  Profit Margin: {fundamentals['profit_margins']*100:.2f}%")
        else:
            print(f"  ❌ No fundamentals data available")

def demo_market_movers():
    """Demo market movers"""
    print("\n🚀 MARKET MOVERS DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    categories = ['stocks', 'futures', 'forex', 'crypto']
    
    for category in categories:
        print(f"\nTop movers in {category.upper()}:")
        movers = api.get_market_movers(category)
        
        if movers:
            for i, mover in enumerate(movers[:5], 1):
                symbol = mover['symbol']
                price = mover.get('price', 0)
                change_pct = mover.get('change_percent', 0)
                
                print(f"  {i}. {symbol:<8} ${price:<8.2f} {change_pct:+6.2f}%")
        else:
            print(f"  ❌ No movers data available for {category}")

def demo_popular_symbols():
    """Demo popular symbols access"""
    print("\n⭐ POPULAR SYMBOLS DEMO")
    print("="*40)
    
    api = MarketDataAPI()
    
    print("Available symbol categories:")
    for category, symbols in api.popular_symbols.items():
        print(f"\n{category}:")
        print(f"  {', '.join(symbols[:8])}{'...' if len(symbols) > 8 else ''}")

def main():
    """Run all demos"""
    print("🔥 MARKET DATA API DEMONSTRATION")
    print("="*50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    try:
        # Run demos
        demo_symbol_search()
        demo_real_time_quotes()
        demo_market_data()
        demo_fundamentals()
        demo_market_movers()
        demo_popular_symbols()
        
        print("\n" + "="*50)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        print("\n🚀 NEXT STEPS:")
        print("1. Launch the Bloomberg Terminal UI:")
        print("   python launch_terminal.py")
        print("\n2. Navigate to 'Market Data' page")
        print("3. Search for any symbol (stocks, futures, forex, crypto)")
        print("4. Add symbols to your watchlist")
        print("5. View real-time quotes and charts")
        
        print("\n💡 TIP: The Market Data page in the UI provides:")
        print("• Interactive symbol search")
        print("• Real-time price quotes")
        print("• Candlestick charts")
        print("• Fundamental analysis")
        print("• Personal watchlist management")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Ensure you have internet connection")
        print("2. Install required packages: pip install -r requirements.txt")
        print("3. Check if yfinance is working: pip install --upgrade yfinance")

if __name__ == "__main__":
    main()
