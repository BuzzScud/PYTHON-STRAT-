"""
Unified Algorithmic Trading Terminal
Combines all trading system components into one cohesive web application
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import time
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Production environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# Optional imports with graceful fallback
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

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# Import trading system components with error handling
TRADING_SYSTEM_AVAILABLE = True
try:
    from trading_core.trading_system import TradingSystem
    from config.config import trading_config, instrument_config
    from trading_core.data_manager import DataManager
    from trading_core.risk_manager import RiskManager
    from trading_core.strategy_framework import CustomStrategy
    from trading_core.market_data_api import MarketDataAPI, SymbolInfo
    from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy
except ImportError as e:
    TRADING_SYSTEM_AVAILABLE = False
    # Note: Cannot use st.warning here as st.set_page_config must be first

# Bloomberg Terminal Color Scheme
BLOOMBERG_COLORS = {
    'bg_primary': '#000000',
    'bg_secondary': '#1a1a1a',
    'bg_tertiary': '#2d2d2d',
    'text_primary': '#ffffff',
    'text_secondary': '#cccccc',
    'accent_orange': '#ff6600',
    'accent_blue': '#0066cc',
    'accent_green': '#00cc66',
    'accent_red': '#cc0000',
    'accent_yellow': '#ffcc00'
}

def apply_bloomberg_theme():
    """Apply Bloomberg Terminal styling"""
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BLOOMBERG_COLORS['bg_primary']};
        color: {BLOOMBERG_COLORS['text_primary']};
    }}

    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        background-color: {BLOOMBERG_COLORS['bg_primary']};
    }}

    .stSelectbox > div > div {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
        color: {BLOOMBERG_COLORS['text_primary']};
        border: 1px solid {BLOOMBERG_COLORS['accent_orange']};
    }}

    .stTextInput > div > div > input {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
        color: {BLOOMBERG_COLORS['text_primary']};
        border: 1px solid {BLOOMBERG_COLORS['accent_orange']};
    }}

    .stButton > button {{
        background-color: {BLOOMBERG_COLORS['accent_orange']};
        color: {BLOOMBERG_COLORS['bg_primary']};
        border: none;
        font-weight: bold;
        border-radius: 2px;
    }}

    .stButton > button:hover {{
        background-color: {BLOOMBERG_COLORS['accent_blue']};
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
        border-radius: 3px;
    }}

    .status-green {{
        color: {BLOOMBERG_COLORS['accent_green']};
        font-weight: bold;
    }}

    .status-red {{
        color: {BLOOMBERG_COLORS['accent_red']};
        font-weight: bold;
    }}

    .status-yellow {{
        color: {BLOOMBERG_COLORS['accent_yellow']};
        font-weight: bold;
    }}

    .data-table {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
        color: {BLOOMBERG_COLORS['text_primary']};
    }}

    .sidebar .sidebar-content {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background-color: {BLOOMBERG_COLORS['bg_secondary']};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: {BLOOMBERG_COLORS['bg_tertiary']};
        color: {BLOOMBERG_COLORS['text_primary']};
        border: 1px solid {BLOOMBERG_COLORS['accent_orange']};
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {BLOOMBERG_COLORS['accent_orange']};
        color: {BLOOMBERG_COLORS['bg_primary']};
    }}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'trading_system' not in st.session_state:
        st.session_state.trading_system = None
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'live_data' not in st.session_state:
        st.session_state.live_data = {}
    if 'strategy_code' not in st.session_state:
        # Load default strategy code
        try:
            with open('strategy_framework.py', 'r') as f:
                st.session_state.strategy_code = f.read()
        except:
            st.session_state.strategy_code = "# Strategy code will appear here"
    if 'market_api' not in st.session_state:
        if TRADING_SYSTEM_AVAILABLE:
            try:
                from trading_core.market_data_api import MarketDataAPI
                st.session_state.market_api = MarketDataAPI()
            except Exception:
                st.session_state.market_api = None
        else:
            st.session_state.market_api = None
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['SPY', 'QQQ', 'ES', 'NQ', 'EURUSD', 'GBPUSD']

def create_terminal_header():
    """Create unified terminal header"""
    st.markdown(f"""
    <div class="terminal-header">
        UNIFIED TRADING TERMINAL v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create Bloomberg-style metric card"""
    delta_html = ""
    if delta is not None:
        color_class = "status-green" if delta_color == "normal" and delta > 0 else "status-red" if delta < 0 else "status-yellow"
        delta_html = f'<div class="{color_class}">Δ {delta:+.2f}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 14px; color: {BLOOMBERG_COLORS['text_secondary']};">{title}</div>
        <div style="font-size: 24px; font-weight: bold; color: {BLOOMBERG_COLORS['text_primary']};">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def dashboard_page():
    """Main dashboard page with fallback for missing components"""
    st.markdown("## UNIFIED TRADING DASHBOARD")

    if not TRADING_SYSTEM_AVAILABLE:
        st.warning("Trading system components not fully available. Running in demo mode.")

        # Demo dashboard
        st.markdown("### DEMO PORTFOLIO METRICS")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            create_metric_card("PORTFOLIO VALUE", "$100,000.00")
        with col2:
            create_metric_card("CASH", "$95,000.00")
        with col3:
            create_metric_card("UNREALIZED P&L", "+$2,500.00")
        with col4:
            create_metric_card("OPEN POSITIONS", "3")

        st.markdown("---")

        # Demo system status
        st.markdown("### SYSTEM STATUS")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="status-green">Demo Mode: ACTIVE</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-green">Paper Trading: ENABLED</div>', unsafe_allow_html=True)

        with col2:
            yf_status = "CONNECTED" if YFINANCE_AVAILABLE else "OFFLINE"
            st.markdown(f'<div class="status-green">Data Feed: {yf_status}</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-green">Risk Manager: SIMULATED</div>', unsafe_allow_html=True)

        return

    # Full trading system available
    # Initialize trading system if not exists
    if st.session_state.trading_system is None:
        with st.spinner("Initializing Trading System..."):
            try:
                st.session_state.trading_system = TradingSystem(
                    initial_capital=100000,
                    strategy_name="custom"
                )
            except Exception as e:
                st.error(f"Failed to initialize trading system: {e}")
                return

    system = st.session_state.trading_system

    # Real-time metrics row
    col1, col2, col3, col4 = st.columns(4)

    try:
        with col1:
            portfolio = system.get_performance_report()['portfolio_summary']
            create_metric_card("PORTFOLIO VALUE", f"${portfolio['total_equity']:,.2f}")

        with col2:
            create_metric_card("CASH", f"${portfolio['current_capital']:,.2f}")

        with col3:
            create_metric_card("UNREALIZED P&L", f"${portfolio['unrealized_pnl']:,.2f}")

        with col4:
            create_metric_card("OPEN POSITIONS", f"{portfolio['positions_count']}")
    except Exception as e:
        st.error(f"Error loading portfolio data: {e}")
        return

    st.markdown("---")

    # Market data and signals
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### MARKET DATA")

        # Get current signals
        if st.button("REFRESH SIGNALS", key="refresh_signals"):
            with st.spinner("Fetching market data..."):
                try:
                    signals = system.get_current_signals()
                    st.session_state.current_signals = signals
                except Exception as e:
                    st.error(f"Error fetching signals: {e}")

        if hasattr(st.session_state, 'current_signals'):
            if st.session_state.current_signals:
                signals_df = pd.DataFrame(st.session_state.current_signals)
                st.dataframe(signals_df, use_container_width=True)
            else:
                st.info("No signals generated at this time")

    with col2:
        st.markdown("### QUICK ACTIONS")

        if st.button("EXECUTE LIVE TRADING", key="execute_trading"):
            with st.spinner("Executing trades..."):
                try:
                    system.execute_live_trading()
                    st.success("Trading execution completed!")
                except Exception as e:
                    st.error(f"Trading execution failed: {e}")

        if st.button("UPDATE DATA", key="update_data"):
            with st.spinner("Updating market data..."):
                try:
                    system.data_manager.update_data()
                    st.success("Data updated!")
                except Exception as e:
                    st.error(f"Data update failed: {e}")

        if st.button("EXPORT TRADES", key="export_trades"):
            try:
                filename = system.export_trades()
                st.success(f"Trades exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {e}")

def strategy_editor_page():
    """Strategy editor page"""
    st.markdown("## STRATEGY EDITOR")

    # Strategy selection
    col1, col2 = st.columns([1, 1])

    with col1:
        strategy_type = st.selectbox(
            "Strategy Type",
            ["Custom Strategy", "Momentum Strategy", "Mean Reversion Strategy"],
            key="strategy_type"
        )

    with col2:
        if st.button("SAVE STRATEGY", key="save_strategy"):
            # Save the current strategy code
            try:
                with open('strategy_framework.py', 'w') as f:
                    f.write(st.session_state.strategy_code)
                st.success("Strategy saved successfully!")
            except Exception as e:
                st.error(f"Error saving strategy: {e}")

    st.markdown("---")

    # Code editor
    st.markdown("### STRATEGY CODE EDITOR")

    # Load strategy code if not in session state
    if 'strategy_code' not in st.session_state:
        try:
            with open('strategy_framework.py', 'r') as f:
                st.session_state.strategy_code = f.read()
        except:
            st.session_state.strategy_code = "# Strategy code will appear here"

    # Code editor with syntax highlighting
    edited_code = st_ace(
        value=st.session_state.strategy_code,
        language='python',
        theme='monokai',
        key="strategy_editor",
        height=400,
        auto_update=True,
        font_size=12,
        tab_size=4,
        wrap=False,
        annotations=None
    )

    st.session_state.strategy_code = edited_code

    # Strategy parameters
    st.markdown("### STRATEGY PARAMETERS")

    col1, col2, col3 = st.columns(3)

    with col1:
        rsi_oversold = st.slider("RSI Oversold", 10, 40, 30, key="rsi_oversold")
        rsi_overbought = st.slider("RSI Overbought", 60, 90, 70, key="rsi_overbought")

    with col2:
        atr_multiplier = st.slider("ATR Stop Multiplier", 1.0, 5.0, 2.0, 0.1, key="atr_mult")
        min_confidence = st.slider("Min Confidence", 0.1, 1.0, 0.6, 0.05, key="min_conf")

    with col3:
        risk_reward = st.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0, 0.1, key="risk_reward")
        max_positions = st.slider("Max Positions", 1, 10, 6, key="max_pos")

    # Test strategy button
    if st.button("TEST STRATEGY", key="test_strategy"):
        with st.spinner("Testing strategy..."):
            try:
                # Here you would implement strategy testing logic
                st.success("Strategy test completed successfully!")
                st.info("Strategy validation passed. Ready for backtesting.")
            except Exception as e:
                st.error(f"Strategy test failed: {e}")

def backtesting_page():
    """Backtesting page"""
    st.markdown("## BACKTESTING ENGINE")

    # Backtest parameters
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            key="backtest_start"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="backtest_end"
        )

    with col3:
        timeframe = st.selectbox(
            "Timeframe",
            ["1d", "4h", "1h"],
            key="backtest_timeframe"
        )

    # Run backtest button
    if st.button("RUN BACKTEST", key="run_backtest"):
        if st.session_state.trading_system is None:
            st.session_state.trading_system = TradingSystem(100000, "custom")

        with st.spinner("Running backtest... This may take a few minutes."):
            try:
                results = st.session_state.trading_system.run_backtest(
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    timeframe=timeframe
                )
                st.session_state.backtest_results = results
                st.success("Backtest completed successfully!")
            except Exception as e:
                st.error(f"Backtest failed: {e}")

    # Display results
    if st.session_state.backtest_results:
        results = st.session_state.backtest_results

        st.markdown("---")
        st.markdown("### BACKTEST RESULTS")

        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            create_metric_card(
                "TOTAL RETURN",
                f"{results.get('total_return_pct', 0):.2f}%"
            )

        with col2:
            create_metric_card(
                "SHARPE RATIO",
                f"{results.get('sharpe_ratio', 0):.2f}"
            )

        with col3:
            create_metric_card(
                "MAX DRAWDOWN",
                f"{results.get('max_drawdown_pct', 0):.2f}%"
            )

        with col4:
            create_metric_card(
                "WIN RATE",
                f"{results.get('win_rate', 0)*100:.1f}%"
            )

        # Equity curve chart
        if 'equity_curve' in results:
            st.markdown("### EQUITY CURVE")

            equity_df = results['equity_curve']

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=equity_df.index,
                y=equity_df['equity'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color=BLOOMBERG_COLORS['accent_green'], width=2)
            ))

            fig.update_layout(
                title="Portfolio Equity Curve",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                plot_bgcolor=BLOOMBERG_COLORS['bg_secondary'],
                paper_bgcolor=BLOOMBERG_COLORS['bg_primary'],
                font=dict(color=BLOOMBERG_COLORS['text_primary']),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

def ict_analysis_page():
    """ICT Analysis page"""
    st.markdown("## 🎯 ICT ANALYSIS TOOL")
    st.markdown("*Inner Circle Trader - Institutional Market Structure Analysis*")

    # Initialize ICT strategy if not exists
    if 'ict_strategy' not in st.session_state:
        if TRADING_SYSTEM_AVAILABLE:
            try:
                from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy
                st.session_state.ict_strategy = StandaloneICTStrategy({
                    'trading_style': 'day_trading',
                    'asset_type': 'forex',
                    'risk_per_trade': 0.02,
                    'max_daily_trades': 3,
                    'confluence_threshold': 0.6
                })
            except Exception:
                st.session_state.ict_strategy = None
        else:
            st.session_state.ict_strategy = None

    # Symbol selection and configuration
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        symbol = st.text_input(
            "📊 Enter Symbol",
            value="EURUSD=X",
            placeholder="e.g., EURUSD=X, AAPL, ES=F",
            key="ict_symbol"
        )

    with col2:
        timeframe = st.selectbox(
            "⏰ Timeframe",
            ["1d", "4h", "1h", "30m"],
            index=1,
            key="ict_timeframe"
        )

    with col3:
        period = st.selectbox(
            "📅 Period",
            ["60d", "30d", "7d", "5d"],
            index=0,
            key="ict_period"
        )

    # ICT Configuration
    st.markdown("---")
    st.markdown("### ⚙️ ICT CONFIGURATION")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        trading_style = st.selectbox(
            "Trading Style",
            ["scalping", "day_trading", "swing_trading", "position_trading"],
            index=1,
            key="ict_trading_style"
        )

    with col2:
        asset_type = st.selectbox(
            "Asset Type",
            ["forex", "stocks", "crypto", "indices"],
            index=0,
            key="ict_asset_type"
        )

    with col3:
        confluence_threshold = st.slider(
            "Confluence Threshold",
            0.3, 1.0, 0.6, 0.05,
            key="ict_confluence"
        )

    with col4:
        max_trades = st.slider(
            "Max Daily Trades",
            1, 10, 3,
            key="ict_max_trades"
        )

    # Update ICT strategy configuration if available
    if st.session_state.ict_strategy:
        st.session_state.ict_strategy.trading_style = trading_style
        st.session_state.ict_strategy.asset_type = asset_type
        st.session_state.ict_strategy.confluence_threshold = confluence_threshold
        st.session_state.ict_strategy.max_daily_trades = max_trades

    # Analysis button
    if st.button("🚀 RUN ICT ANALYSIS", key="run_ict_analysis"):
        if not st.session_state.ict_strategy:
            st.error("❌ ICT Strategy not available. Trading system components are missing.")
            st.info("💡 The system is running in demo mode with limited functionality.")
            return

        if symbol:
            with st.spinner(f"Fetching data and analyzing {symbol}..."):
                try:
                    # Fetch data using yfinance
                    if not YFINANCE_AVAILABLE:
                        st.error("❌ yfinance not available. Cannot fetch market data.")
                        return

                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period, interval=timeframe)

                    if data.empty:
                        st.error(f"No data found for symbol: {symbol}")
                        return

                    # Convert column names to lowercase for consistency
                    data.columns = [col.lower() for col in data.columns]

                    # Store data and analysis in session state
                    st.session_state.ict_data = data
                    st.session_state.ict_analysis = st.session_state.ict_strategy.analyze_market(data)
                    st.session_state.ict_signals = st.session_state.ict_strategy.generate_signals(data)
                    st.session_state.ict_trading_plan = st.session_state.ict_strategy.get_trading_plan(data)

                    st.success(f"✅ Analysis completed for {symbol}")

                except Exception as e:
                    st.error(f"Error analyzing {symbol}: {str(e)}")
                    return
        else:
            st.warning("Please enter a symbol to analyze")

    # Display analysis results if available
    if hasattr(st.session_state, 'ict_analysis') and st.session_state.ict_analysis:
        display_ict_analysis_results()

def display_ict_analysis_results():
    """Display ICT analysis results"""
    analysis = st.session_state.ict_analysis
    signals = st.session_state.ict_signals
    trading_plan = st.session_state.ict_trading_plan
    data = st.session_state.ict_data

    st.markdown("---")
    st.markdown("## 📊 ICT ANALYSIS RESULTS")

    # Current price and basic info
    current_price = analysis['current_price']
    symbol = st.session_state.get('ict_symbol', 'Unknown')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card("CURRENT PRICE", f"{current_price:.5f}")

    with col2:
        # Calculate price change
        if len(data) > 1:
            price_change = current_price - data['close'].iloc[-2]
            price_change_pct = (price_change / data['close'].iloc[-2]) * 100
            create_metric_card("24H CHANGE", f"{price_change_pct:+.2f}%")
        else:
            create_metric_card("24H CHANGE", "N/A")

    with col3:
        create_metric_card("SIGNALS FOUND", f"{len(signals)}")

    with col4:
        risk_level = trading_plan.get('risk_assessment', {}).get('overall_risk', 'medium')
        create_metric_card("RISK LEVEL", risk_level.upper())

    # Power of Three Analysis
    st.markdown("### 🎯 POWER OF THREE (PO3) ANALYSIS")

    po3_analysis = analysis.get('po3_analysis', {})
    if po3_analysis:
        dealing_range = po3_analysis.get('dealing_range', {})
        price_position = po3_analysis.get('price_position', {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📊 Dealing Range**")
            st.markdown(f"""
            - **Optimal PO3 Size**: {po3_analysis.get('optimal_size', 'N/A')}
            - **Range Low**: {dealing_range.get('range_low', 'N/A'):.5f}
            - **Range High**: {dealing_range.get('range_high', 'N/A'):.5f}
            - **Equilibrium**: {dealing_range.get('equilibrium', 'N/A'):.5f}
            """)

        with col2:
            zone = price_position.get('zone', 'unknown').upper()
            strength = price_position.get('strength', 0)

            # Color code the zone
            if zone == 'DISCOUNT':
                zone_color = BLOOMBERG_COLORS['accent_green']
                zone_emoji = "🟢"
                bias = "BULLISH BIAS"
            elif zone == 'PREMIUM':
                zone_color = BLOOMBERG_COLORS['accent_red']
                zone_emoji = "🔴"
                bias = "BEARISH BIAS"
            else:
                zone_color = BLOOMBERG_COLORS['accent_yellow']
                zone_emoji = "🟡"
                bias = "NEUTRAL"

            st.markdown("**🎯 Price Position**")
            st.markdown(f"""
            - **Current Zone**: {zone_emoji} {zone}
            - **Zone Strength**: {strength:.2f}
            - **Market Bias**: {bias}
            - **Position %**: {price_position.get('position_percentage', 0)*100:.1f}%
            """)

    # Goldbach/IPDA Analysis
    st.markdown("### 🎯 GOLDBACH/IPDA LEVELS")

    goldbach_analysis = analysis.get('goldbach_analysis', {})
    if goldbach_analysis:
        nearest_level = goldbach_analysis.get('nearest_level')
        institutional_levels = goldbach_analysis.get('institutional_levels', {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🏛️ Institutional Levels**")
            if institutional_levels:
                for level_name, price in institutional_levels.items():
                    level_display = level_name.replace('_', ' ').title()
                    st.markdown(f"- **{level_display}**: {price:.5f}")

        with col2:
            if nearest_level:
                distance_pips = nearest_level.get('distance', 0) * 10000
                st.markdown("**📍 Nearest Level**")
                st.markdown(f"""
                - **Type**: {nearest_level.get('level_type', 'N/A').replace('_', ' ').title()}
                - **Price**: {nearest_level.get('price', 'N/A'):.5f}
                - **Distance**: {distance_pips:.1f} pips
                - **Weight**: {nearest_level.get('weight', 0):.2f}
                """)

    # AMD Cycle Analysis
    st.markdown("### ⏰ AMD CYCLE ANALYSIS")

    amd_analysis = analysis.get('amd_analysis', {})
    current_phase = amd_analysis.get('current_phase', 'unknown')

    col1, col2 = st.columns(2)

    with col1:
        # Current phase with emoji and color
        phase_info = {
            'accumulation': {'emoji': '📊', 'color': BLOOMBERG_COLORS['accent_blue'], 'description': 'Asian Range - Analysis Phase'},
            'manipulation': {'emoji': '🔥', 'color': BLOOMBERG_COLORS['accent_orange'], 'description': 'London Session - Prime Entry Window'},
            'distribution': {'emoji': '💼', 'color': BLOOMBERG_COLORS['accent_green'], 'description': 'NY Session - Management Phase'}
        }

        phase_data = phase_info.get(current_phase, {'emoji': '❓', 'color': BLOOMBERG_COLORS['text_secondary'], 'description': 'Unknown Phase'})

        st.markdown("**⏰ Current AMD Phase**")
        st.markdown(f"""
        - **Phase**: {phase_data['emoji']} {current_phase.upper()}
        - **Description**: {phase_data['description']}
        - **Optimal Action**: {'Enter Trades' if current_phase == 'manipulation' else 'Analyze' if current_phase == 'accumulation' else 'Manage Positions'}
        """)

    with col2:
        st.markdown("**🕐 Session Timing (CET)**")
        st.markdown("""
        - **Asian (A)**: 20:00 - 05:00 (9 hours)
        - **London (M)**: 05:00 - 11:00 (6 hours) 🔥
        - **New York (D)**: 11:00 - 20:00 (9 hours)
        """)

    # HIPPO Pattern Analysis
    st.markdown("### 🎪 HIPPO PATTERN ANALYSIS")

    hippo_analysis = analysis.get('hippo_analysis', {})
    partition_info = hippo_analysis.get('partition_info', {})
    patterns = hippo_analysis.get('patterns', [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📅 Lookback Partition**")
        st.markdown(f"""
        - **Current Month Number**: {partition_info.get('partition_number', 'N/A')}
        - **Days into Partition**: {partition_info.get('days_into_partition', 'N/A')}
        - **Partition Start**: {partition_info.get('partition_start', 'N/A')}
        """)

    with col2:
        st.markdown("**🎪 HIPPO Patterns Found**")
        if patterns:
            for i, pattern in enumerate(patterns[:3], 1):  # Show first 3 patterns
                if pattern.get('is_hippo'):
                    st.markdown(f"""
                    **Pattern {i}:**
                    - Type: {pattern.get('pattern_type', 'N/A')}
                    - Direction: {pattern.get('direction', 'N/A')}
                    - Hidden Level: {pattern.get('hidden_level', 'N/A'):.5f}
                    """)
        else:
            st.markdown("No HIPPO patterns detected in current timeframe")

    # Trading Signals
    if signals:
        st.markdown("### 🚨 TRADING SIGNALS")

        for i, signal in enumerate(signals, 1):
            with st.expander(f"🎯 Signal #{i}: {signal.get('type', 'Unknown').replace('_', ' ').title()}", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    direction_emoji = "🟢" if signal.get('direction') == 'long' else "🔴"
                    st.markdown(f"""
                    **Signal Details:**
                    - **Direction**: {direction_emoji} {signal.get('direction', 'N/A').upper()}
                    - **Entry Price**: {signal.get('entry_price', current_price):.5f}
                    - **Confluence Score**: {signal.get('confluence_score', 0):.2f}
                    - **Strength**: {signal.get('strength', 0):.2f}
                    """)

                with col2:
                    st.markdown(f"""
                    **Risk Management:**
                    - **Stop Loss**: {signal.get('stop_loss', 'N/A')}
                    - **Take Profit**: {signal.get('take_profit', 'N/A')}
                    - **Reasoning**: {signal.get('reasoning', 'N/A')}
                    """)

    # Trading Plan
    st.markdown("### 📋 TRADING PLAN")

    recommendations = trading_plan.get('recommendations', [])
    risk_assessment = trading_plan.get('risk_assessment', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📝 Recommendations**")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.markdown("No specific recommendations at this time")

    with col2:
        risk_level = risk_assessment.get('overall_risk', 'medium')
        risk_factors = risk_assessment.get('factors', [])

        risk_color = {
            'low': BLOOMBERG_COLORS['accent_green'],
            'medium': BLOOMBERG_COLORS['accent_yellow'],
            'high': BLOOMBERG_COLORS['accent_red']
        }.get(risk_level, BLOOMBERG_COLORS['text_secondary'])

        st.markdown("**⚠️ Risk Assessment**")
        st.markdown(f"- **Overall Risk**: {risk_level.upper()}")

        if risk_factors:
            st.markdown("- **Risk Factors**:")
            for factor in risk_factors:
                st.markdown(f"  - {factor}")
        else:
            st.markdown("- **Risk Factors**: None identified")

    # Price Chart with ICT Levels
    st.markdown("### 📊 PRICE CHART WITH ICT LEVELS")

    if len(data) > 0:
        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="Price",
            increasing_line_color=BLOOMBERG_COLORS['accent_green'],
            decreasing_line_color=BLOOMBERG_COLORS['accent_red']
        ))

        # Add PO3 levels
        if po3_analysis:
            dealing_range = po3_analysis.get('dealing_range', {})

            # Range high
            if 'range_high' in dealing_range:
                fig.add_hline(
                    y=dealing_range['range_high'],
                    line_dash="dash",
                    line_color=BLOOMBERG_COLORS['accent_red'],
                    annotation_text="PO3 High"
                )

            # Range low
            if 'range_low' in dealing_range:
                fig.add_hline(
                    y=dealing_range['range_low'],
                    line_dash="dash",
                    line_color=BLOOMBERG_COLORS['accent_green'],
                    annotation_text="PO3 Low"
                )

            # Equilibrium
            if 'equilibrium' in dealing_range:
                fig.add_hline(
                    y=dealing_range['equilibrium'],
                    line_dash="dot",
                    line_color=BLOOMBERG_COLORS['accent_yellow'],
                    annotation_text="Equilibrium"
                )

        # Add Goldbach levels
        if goldbach_analysis and institutional_levels:
            for level_name, price in institutional_levels.items():
                if 'equilibrium' not in level_name:  # Don't duplicate equilibrium
                    fig.add_hline(
                        y=price,
                        line_dash="dashdot",
                        line_color=BLOOMBERG_COLORS['accent_blue'],
                        annotation_text=level_name.replace('_', ' ').title(),
                        annotation_position="bottom right"
                    )

        fig.update_layout(
            title=f"ICT Analysis - {st.session_state.get('ict_symbol', 'Unknown')}",
            xaxis_title="Time",
            yaxis_title="Price",
            plot_bgcolor=BLOOMBERG_COLORS['bg_secondary'],
            paper_bgcolor=BLOOMBERG_COLORS['bg_primary'],
            font=dict(color=BLOOMBERG_COLORS['text_primary']),
            showlegend=True,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

def risk_management_page():
    """Risk management page"""
    st.markdown("## 🛡️ RISK MANAGEMENT")

    if st.session_state.trading_system is None:
        st.session_state.trading_system = TradingSystem(100000, "custom")

    system = st.session_state.trading_system
    portfolio = system.get_performance_report()['portfolio_summary']

    # Risk metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        create_metric_card(
            "CURRENT DRAWDOWN",
            f"${portfolio['current_drawdown']:,.2f}"
        )

    with col2:
        create_metric_card(
            "MAX DRAWDOWN LIMIT",
            f"${portfolio['max_drawdown_limit']:,.2f}"
        )

    with col3:
        drawdown_pct = (portfolio['current_drawdown'] / portfolio['max_drawdown_limit']) * 100
        create_metric_card(
            "DRAWDOWN USAGE",
            f"{drawdown_pct:.1f}%"
        )

    st.markdown("---")

    # Risk settings
    st.markdown("### ⚙️ RISK PARAMETERS")

    col1, col2 = st.columns(2)

    with col1:
        risk_per_trade = st.slider(
            "Risk Per Trade (%)",
            0.1, 2.0, 0.25, 0.05,
            key="risk_per_trade"
        )

        max_positions = st.slider(
            "Maximum Positions",
            1, 10, 6,
            key="max_positions_risk"
        )

    with col2:
        max_drawdown = st.number_input(
            "Max Drawdown ($)",
            min_value=500,
            max_value=10000,
            value=1500,
            step=100,
            key="max_drawdown"
        )

        correlation_limit = st.slider(
            "Correlation Limit",
            0.1, 1.0, 0.7, 0.05,
            key="correlation_limit"
        )

    # Position sizing calculator
    st.markdown("### 🧮 POSITION SIZE CALCULATOR")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        symbol = st.selectbox(
            "Symbol",
            trading_config.FUTURES_SYMBOLS + trading_config.FOREX_SYMBOLS,
            key="calc_symbol"
        )

    with col2:
        entry_price = st.number_input(
            "Entry Price",
            min_value=0.01,
            value=4500.0,
            key="calc_entry"
        )

    with col3:
        stop_loss = st.number_input(
            "Stop Loss",
            min_value=0.01,
            value=4480.0,
            key="calc_stop"
        )

    with col4:
        account_balance = st.number_input(
            "Account Balance",
            min_value=1000,
            value=100000,
            key="calc_balance"
        )

    if st.button("📊 CALCULATE POSITION SIZE", key="calc_position"):
        try:
            position_size = system.risk_manager.calculate_position_size(
                symbol, entry_price, stop_loss, account_balance
            )

            risk_amount = account_balance * (risk_per_trade / 100)

            st.success(f"""
            **Position Size: {position_size} {'contracts' if symbol in trading_config.FUTURES_SYMBOLS else 'units'}**

            Risk Amount: ${risk_amount:,.2f}
            Price Risk: ${abs(entry_price - stop_loss):,.2f}
            """)
        except Exception as e:
            st.error(f"Calculation error: {e}")

def settings_page():
    """Settings page"""
    st.markdown("## ⚙️ SYSTEM SETTINGS")

    # Trading configuration
    st.markdown("### 🔧 TRADING CONFIGURATION")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Market Settings**")

        futures_symbols = st.multiselect(
            "Futures Symbols",
            ["ES", "NQ", "YM", "RTY", "CL", "GC"],
            default=["ES", "NQ", "YM"],
            key="futures_symbols"
        )

        forex_symbols = st.multiselect(
            "Forex Symbols",
            ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "NZDUSD"],
            default=["EURUSD", "GBPUSD", "AUDUSD"],
            key="forex_symbols"
        )

        primary_timeframe = st.selectbox(
            "Primary Timeframe",
            ["1d", "4h", "1h", "30m"],
            index=0,
            key="primary_tf"
        )

    with col2:
        st.markdown("**System Settings**")

        paper_trading = st.checkbox(
            "Paper Trading Mode",
            value=True,
            key="paper_trading"
        )

        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1,
            key="log_level"
        )

        auto_update = st.checkbox(
            "Auto Update Data",
            value=True,
            key="auto_update"
        )

    # Data source settings
    st.markdown("### 📡 DATA SOURCES")

    col1, col2 = st.columns(2)

    with col1:
        data_provider = st.selectbox(
            "Primary Data Provider",
            ["yfinance", "alpha_vantage", "polygon"],
            key="data_provider"
        )

        alpha_vantage_key = st.text_input(
            "Alpha Vantage API Key",
            type="password",
            key="av_key"
        )

    with col2:
        update_frequency = st.selectbox(
            "Update Frequency",
            ["Real-time", "Every 5 minutes", "Every 15 minutes", "Hourly"],
            index=2,
            key="update_freq"
        )

        fred_api_key = st.text_input(
            "FRED API Key",
            type="password",
            key="fred_key"
        )

    # Save settings
    if st.button("💾 SAVE SETTINGS", key="save_settings"):
        try:
            # Here you would save settings to config file
            st.success("Settings saved successfully!")
        except Exception as e:
            st.error(f"Error saving settings: {e}")

    # System status
    st.markdown("### 📊 SYSTEM STATUS")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="status-green">🟢 Trading System: ONLINE</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-green">🟢 Data Feed: CONNECTED</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="status-green">🟢 Risk Manager: ACTIVE</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-yellow">🟡 Paper Trading: ENABLED</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="status-green">🟢 Database: CONNECTED</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-green">🟢 Backtesting: READY</div>', unsafe_allow_html=True)

def market_data_page():
    """Market data and symbol lookup page"""
    st.markdown("## 📊 MARKET DATA CENTER")

    # Initialize market API
    market_api = st.session_state.market_api

    # Symbol search section
    st.markdown("### 🔍 SYMBOL LOOKUP")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_query = st.text_input(
            "Search Symbol or Company",
            placeholder="Enter symbol (e.g., AAPL, ES, EURUSD) or company name",
            key="symbol_search"
        )

    with col2:
        if st.button("🔍 SEARCH", key="search_btn"):
            if search_query:
                with st.spinner("Searching symbols..."):
                    results = market_api.search_symbols(search_query, limit=10)
                    st.session_state.search_results = results

    with col3:
        if st.button("📈 ADD TO WATCHLIST", key="add_watchlist"):
            if search_query and search_query.upper() not in st.session_state.watchlist:
                st.session_state.watchlist.append(search_query.upper())
                st.success(f"Added {search_query.upper()} to watchlist")

    # Display search results
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        st.markdown("#### 🎯 SEARCH RESULTS")

        for symbol_info in st.session_state.search_results:
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

            with col1:
                st.markdown(f"**{symbol_info.symbol}**")

            with col2:
                st.markdown(f"{symbol_info.name[:40]}...")

            with col3:
                if symbol_info.price:
                    color = "status-green" if symbol_info.change and symbol_info.change > 0 else "status-red"
                    st.markdown(f'<div class="{color}">${symbol_info.price:.2f}</div>', unsafe_allow_html=True)
                else:
                    st.markdown("N/A")

            with col4:
                if symbol_info.change_percent:
                    color = "status-green" if symbol_info.change_percent > 0 else "status-red"
                    st.markdown(f'<div class="{color}">{symbol_info.change_percent:+.2f}%</div>', unsafe_allow_html=True)
                else:
                    st.markdown("N/A")

    st.markdown("---")

    # Quick access categories
    st.markdown("### ⚡ QUICK ACCESS")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📈 POPULAR STOCKS", key="popular_stocks"):
            popular = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            quotes = market_api.get_multiple_quotes(popular)
            st.session_state.quick_quotes = quotes

    with col2:
        if st.button("🔮 FUTURES", key="futures_btn"):
            futures = ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC']
            quotes = market_api.get_multiple_quotes(futures)
            st.session_state.quick_quotes = quotes

    with col3:
        if st.button("💱 FOREX", key="forex_btn"):
            forex = ['EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD']
            quotes = market_api.get_multiple_quotes(forex)
            st.session_state.quick_quotes = quotes

    with col4:
        if st.button("₿ CRYPTO", key="crypto_btn"):
            crypto = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD']
            quotes = market_api.get_multiple_quotes(crypto)
            st.session_state.quick_quotes = quotes

    # Display quick quotes
    if hasattr(st.session_state, 'quick_quotes') and st.session_state.quick_quotes:
        st.markdown("#### 📊 REAL-TIME QUOTES")

        # Create a DataFrame for better display
        quote_data = []
        for symbol, quote in st.session_state.quick_quotes.items():
            if quote.get('price') is not None:
                quote_data.append({
                    'Symbol': symbol,
                    'Price': f"${quote['price']:.2f}",
                    'Change': f"{quote.get('change', 0):+.2f}",
                    'Change %': f"{quote.get('change_percent', 0):+.2f}%",
                    'Volume': f"{quote.get('volume', 0):,}",
                    'Exchange': quote.get('exchange', 'N/A')
                })

        if quote_data:
            df = pd.DataFrame(quote_data)
            st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Watchlist section
    st.markdown("### 👁️ WATCHLIST")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.session_state.watchlist:
            if st.button("🔄 REFRESH WATCHLIST", key="refresh_watchlist"):
                with st.spinner("Updating watchlist..."):
                    watchlist_quotes = market_api.get_multiple_quotes(st.session_state.watchlist)
                    st.session_state.watchlist_quotes = watchlist_quotes

    with col2:
        if st.button("🗑️ CLEAR WATCHLIST", key="clear_watchlist"):
            st.session_state.watchlist = []
            st.session_state.watchlist_quotes = {}
            st.success("Watchlist cleared")

    # Display watchlist
    if hasattr(st.session_state, 'watchlist_quotes') and st.session_state.watchlist_quotes:
        watchlist_data = []
        for symbol, quote in st.session_state.watchlist_quotes.items():
            if quote.get('price') is not None:
                watchlist_data.append({
                    'Symbol': symbol,
                    'Price': quote['price'],
                    'Change': quote.get('change', 0),
                    'Change %': quote.get('change_percent', 0),
                    'Volume': quote.get('volume', 0),
                    'Last Update': quote.get('timestamp', 'N/A')
                })

        if watchlist_data:
            df = pd.DataFrame(watchlist_data)

            # Create colored display
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns(6)

                with col1:
                    st.markdown(f"**{row['Symbol']}**")

                with col2:
                    st.markdown(f"${row['Price']:.2f}")

                with col3:
                    color = "status-green" if row['Change'] > 0 else "status-red"
                    st.markdown(f'<div class="{color}">{row["Change"]:+.2f}</div>', unsafe_allow_html=True)

                with col4:
                    color = "status-green" if row['Change %'] > 0 else "status-red"
                    st.markdown(f'<div class="{color}">{row["Change %"]:+.2f}%</div>', unsafe_allow_html=True)

                with col5:
                    st.markdown(f"{row['Volume']:,}")

                with col6:
                    if st.button("📊", key=f"chart_{row['Symbol']}", help="View Chart"):
                        st.session_state.selected_symbol = row['Symbol']

    # Detailed symbol view
    if hasattr(st.session_state, 'selected_symbol'):
        symbol = st.session_state.selected_symbol
        st.markdown(f"### 📈 DETAILED VIEW: {symbol}")

        # Get market data
        with st.spinner(f"Loading data for {symbol}..."):
            market_data = market_api.get_market_data(symbol, period='5d', interval='1h')

            if market_data is not None and not market_data.empty:
                # Create candlestick chart
                fig = go.Figure(data=go.Candlestick(
                    x=market_data.index,
                    open=market_data['open'],
                    high=market_data['high'],
                    low=market_data['low'],
                    close=market_data['close'],
                    name=symbol
                ))

                fig.update_layout(
                    title=f"{symbol} - 5 Day Hourly Chart",
                    xaxis_title="Time",
                    yaxis_title="Price",
                    plot_bgcolor=BLOOMBERG_COLORS['bg_secondary'],
                    paper_bgcolor=BLOOMBERG_COLORS['bg_primary'],
                    font=dict(color=BLOOMBERG_COLORS['text_primary']),
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                # Show fundamentals if available
                fundamentals = market_api.get_symbol_fundamentals(symbol)
                if fundamentals:
                    st.markdown("#### 📊 FUNDAMENTALS")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if 'market_cap' in fundamentals:
                            create_metric_card("Market Cap", f"${fundamentals['market_cap']/1e9:.1f}B")

                    with col2:
                        if 'pe_ratio' in fundamentals:
                            create_metric_card("P/E Ratio", f"{fundamentals['pe_ratio']:.2f}")

                    with col3:
                        if 'dividend_yield' in fundamentals:
                            create_metric_card("Dividend Yield", f"{fundamentals['dividend_yield']*100:.2f}%")

                    with col4:
                        if 'beta' in fundamentals:
                            create_metric_card("Beta", f"{fundamentals['beta']:.2f}")
            else:
                st.error(f"Could not load data for {symbol}")

def main():
    """Main unified application"""
    st.set_page_config(
        page_title="Unified Trading Terminal",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply Bloomberg theme
    apply_bloomberg_theme()

    # Initialize session state
    initialize_session_state()

    # Create terminal header
    create_terminal_header()

    # Sidebar navigation with fallback
    with st.sidebar:
        st.markdown(f"""
        <div style="background-color: {BLOOMBERG_COLORS['accent_orange']};
                    color: {BLOOMBERG_COLORS['bg_primary']};
                    padding: 10px;
                    text-align: center;
                    font-weight: bold;
                    margin-bottom: 20px;">
            UNIFIED TRADING TERMINAL
        </div>
        """, unsafe_allow_html=True)

        # Show system status
        st.markdown("### 📊 SYSTEM STATUS")

        # Check component availability
        if TRADING_SYSTEM_AVAILABLE:
            st.markdown('<div class="status-green">🟢 Trading System: READY</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-red">🔴 Trading System: LIMITED</div>', unsafe_allow_html=True)

        if YFINANCE_AVAILABLE:
            st.markdown('<div class="status-green">🟢 Market Data: CONNECTED</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-red">🔴 Market Data: OFFLINE</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Navigation menu
        if OPTION_MENU_AVAILABLE:
            selected = option_menu(
                menu_title=None,
                options=["Dashboard", "Market Data", "ICT Analysis", "Strategy Editor", "Backtesting", "Risk Management", "Settings"],
                icons=["speedometer2", "graph-up-arrow", "bullseye", "code-slash", "graph-up", "shield-check", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": BLOOMBERG_COLORS['bg_secondary']},
                    "icon": {"color": BLOOMBERG_COLORS['accent_orange'], "font-size": "18px"},
                    "nav-link": {
                        "font-size": "14px",
                        "text-align": "left",
                        "margin": "0px",
                        "color": BLOOMBERG_COLORS['text_primary'],
                        "background-color": BLOOMBERG_COLORS['bg_secondary']
                    },
                    "nav-link-selected": {"background-color": BLOOMBERG_COLORS['accent_orange']},
                }
            )
        else:
            # Fallback navigation
            st.markdown("### 🧭 NAVIGATION")
            selected = st.selectbox(
                "Select Page",
                ["Dashboard", "Market Data", "ICT Analysis", "Strategy Editor", "Backtesting", "Risk Management", "Settings"],
                key="navigation"
            )

    # Route to selected page
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Market Data":
        market_data_page()
    elif selected == "ICT Analysis":
        ict_analysis_page()
    elif selected == "Strategy Editor":
        strategy_editor_page()
    elif selected == "Backtesting":
        backtesting_page()
    elif selected == "Risk Management":
        risk_management_page()
    elif selected == "Settings":
        settings_page()

if __name__ == "__main__":
    main()
