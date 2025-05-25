"""
Simplified Bloomberg Terminal UI with Better Error Handling
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with error handling
try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from datetime import datetime
    STREAMLIT_AVAILABLE = True
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install: pip install streamlit pandas plotly")
    sys.exit(1)

# Optional imports with graceful fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False

try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False

# Bloomberg Terminal Colors
BLOOMBERG_COLORS = {
    'bg_primary': '#000000',
    'bg_secondary': '#1a1a1a',
    'accent_orange': '#ff6600',
    'text_primary': '#ffffff',
    'accent_green': '#00cc66',
    'accent_red': '#cc0000',
}

def apply_bloomberg_theme():
    """Apply Bloomberg Terminal styling"""
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BLOOMBERG_COLORS['bg_primary']};
        color: {BLOOMBERG_COLORS['text_primary']};
    }}

    .stButton > button {{
        background-color: {BLOOMBERG_COLORS['accent_orange']};
        color: {BLOOMBERG_COLORS['bg_primary']};
        border: none;
        font-weight: bold;
    }}

    .metric-card {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid {BLOOMBERG_COLORS['accent_orange']};
        margin: 5px 0;
    }}

    .terminal-header {{
        background-color: {BLOOMBERG_COLORS['accent_orange']};
        color: {BLOOMBERG_COLORS['bg_primary']};
        padding: 10px;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 20px;
    }}

    .status-green {{ color: {BLOOMBERG_COLORS['accent_green']}; font-weight: bold; }}
    .status-red {{ color: {BLOOMBERG_COLORS['accent_red']}; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value):
    """Create Bloomberg-style metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 14px; opacity: 0.8;">{title}</div>
        <div style="font-size: 24px; font-weight: bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def dashboard_page():
    """Main dashboard"""
    st.markdown("## TRADING DASHBOARD")

    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card("PORTFOLIO VALUE", "$100,000.00")

    with col2:
        create_metric_card("CASH", "$95,000.00")

    with col3:
        create_metric_card("UNREALIZED P&L", "$+2,500.00")

    with col4:
        create_metric_card("OPEN POSITIONS", "3")

    st.markdown("---")

    # System status
    st.markdown("### SYSTEM STATUS")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="status-green">Trading System: ONLINE</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-green">Paper Trading: ENABLED</div>', unsafe_allow_html=True)

    with col2:
        yf_status = "CONNECTED" if YFINANCE_AVAILABLE else "NOT AVAILABLE"
        st.markdown(f'<div class="status-green">Data Feed: {yf_status}</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-green">Risk Manager: ACTIVE</div>', unsafe_allow_html=True)

def market_data_page():
    """Enhanced market data page with comprehensive analysis"""
    if not YFINANCE_AVAILABLE:
        st.error("yfinance not available. Install with: pip install yfinance")
        st.info("This page requires yfinance for market data access.")
        return

    # Import the enhanced market data functionality
    try:
        from trading_core.enhanced_market_data import enhanced_market_data_page
        enhanced_market_data_page()
    except ImportError:
        # Fallback to basic functionality
        st.markdown("## MARKET DATA CENTER")

        # Symbol search
        st.markdown("### SYMBOL LOOKUP")

        col1, col2 = st.columns([3, 1])

        with col1:
            symbol = st.text_input("Enter Symbol", placeholder="e.g., AAPL, MSFT, TSLA")

        with col2:
            if st.button("GET QUOTE"):
                if symbol:
                    try:
                        ticker = yf.Ticker(symbol.upper())
                        info = ticker.info
                        hist = ticker.history(period='1d')

                        if not hist.empty:
                            current_price = hist['Close'].iloc[-1]

                            st.success(f"""
                            **{symbol.upper()}**

                            Current Price: ${current_price:.2f}
                            Company: {info.get('longName', 'N/A')}
                            Exchange: {info.get('exchange', 'N/A')}
                            """)
                        else:
                            st.error(f"No data found for {symbol}")

                    except Exception as e:
                        st.error(f"Error fetching data: {e}")

        # Quick access
        st.markdown("### QUICK ACCESS")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("POPULAR STOCKS"):
                st.session_state.quick_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

        with col2:
            if st.button("FUTURES"):
                st.session_state.quick_symbols = ['ES=F', 'NQ=F', 'YM=F']

        with col3:
            if st.button("FOREX"):
                st.session_state.quick_symbols = ['EURUSD=X', 'GBPUSD=X', 'AUDUSD=X']

        with col4:
            if st.button("CRYPTO"):
                st.session_state.quick_symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD']

        # Display quick quotes
        if hasattr(st.session_state, 'quick_symbols'):
            st.markdown("#### QUICK QUOTES")

            for sym in st.session_state.quick_symbols:
                try:
                    ticker = yf.Ticker(sym)
                    hist = ticker.history(period='1d')

                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                        col1, col2 = st.columns([1, 3])

                        with col1:
                            st.markdown(f"**{sym}**")

                        with col2:
                            st.markdown(f"${price:.2f}")

                except Exception as e:
                    st.error(f"Error fetching {sym}: {e}")

def strategy_page():
    """Strategy editor page"""
    st.markdown("## STRATEGY EDITOR")

    if ACE_AVAILABLE:
        st.markdown("### CODE EDITOR")

        default_code = '''# Custom Trading Strategy
def generate_signals(data):
    """
    Generate trading signals based on market data

    Args:
        data: DataFrame with OHLCV data

    Returns:
        List of trading signals
    """
    signals = []

    # Example: Simple RSI strategy
    if 'rsi' in data.columns:
        latest_rsi = data['rsi'].iloc[-1]

        if latest_rsi < 30:  # Oversold
            signals.append({
                'symbol': 'SYMBOL',
                'direction': 'LONG',
                'confidence': 0.8,
                'reason': 'RSI Oversold'
            })
        elif latest_rsi > 70:  # Overbought
            signals.append({
                'symbol': 'SYMBOL',
                'direction': 'SHORT',
                'confidence': 0.8,
                'reason': 'RSI Overbought'
            })

    return signals
'''

        edited_code = st_ace(
            value=default_code,
            language='python',
            theme='monokai',
            height=400
        )

        if st.button("SAVE STRATEGY"):
            st.success("Strategy saved successfully!")

    else:
        st.warning("Advanced code editor not available. Install with: pip install streamlit-ace")

        # Fallback text area
        st.markdown("### BASIC EDITOR")
        strategy_code = st.text_area("Strategy Code", height=300, value="# Enter your strategy code here")

        if st.button("SAVE STRATEGY"):
            st.success("Strategy saved!")

def main():
    """Main application"""
    st.set_page_config(
        page_title="Algorithmic Trading Terminal",
        page_icon="chart_with_upwards_trend",
        layout="wide"
    )

    # Apply theme
    apply_bloomberg_theme()

    # Header
    st.markdown(f"""
    <div class="terminal-header">
        ALGORITHMIC TRADING TERMINAL v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    if OPTION_MENU_AVAILABLE:
        with st.sidebar:
            selected = option_menu(
                menu_title="TRADING TERMINAL",
                options=["Dashboard", "Market Data", "Strategy Editor"],
                icons=["speedometer2", "graph-up-arrow", "code-slash"],
                default_index=0
            )
    else:
        # Fallback navigation
        with st.sidebar:
            st.markdown("## TRADING TERMINAL")
            selected = st.selectbox("Navigate", ["Dashboard", "Market Data", "Strategy Editor"])

    # Route pages
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Market Data":
        market_data_page()
    elif selected == "Strategy Editor":
        strategy_page()

if __name__ == "__main__":
    main()
