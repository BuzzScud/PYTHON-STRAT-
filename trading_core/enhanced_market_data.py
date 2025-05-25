"""
Enhanced Market Data Page with Comprehensive Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import math
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(data):
    """Calculate technical indicators for analysis"""
    df = data.copy()

    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

    # ATR (Average True Range)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()

    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

    return df

def calculate_powers_of_three(current_price):
    """
    Calculate powers of three ranges for trading analysis
    Based on the document provided - powers of three are used for dealing ranges in finance
    """
    # Powers of three values as per the document
    powers_of_three = {
        1: 3,      # 3^1
        2: 9,      # 3^2
        3: 27,     # 3^3 - Scalping
        4: 81,     # 3^4 - Daily Range
        5: 243,    # 3^5 - Weekly Range
        6: 729,    # 3^6 - Monthly Range
        7: 2187,   # 3^7 - Yearly Range
        8: 6561,   # 3^8
        9: 19683,  # 3^9
        10: 59049, # 3^10
        11: 177147 # 3^11
    }

    # Range classifications as per the document
    range_classifications = {
        27: "Scalping",
        81: "Daily Range",
        243: "Weekly Range",
        729: "Monthly Range",
        2187: "Yearly Range"
    }

    # Find which power of three range the current price falls into
    current_range = None
    current_power = None
    next_range = None
    prev_range = None

    for power, value in powers_of_three.items():
        if current_price <= value:
            current_range = value
            current_power = power
            next_range = powers_of_three.get(power + 1)
            prev_range = powers_of_three.get(power - 1)
            break

    # If price is higher than our highest power, use the highest
    if current_range is None:
        current_power = 11
        current_range = powers_of_three[11]
        prev_range = powers_of_three[10]
        next_range = None

    # Calculate position within the range
    if prev_range:
        range_position = ((current_price - prev_range) / (current_range - prev_range)) * 100
    else:
        range_position = (current_price / current_range) * 100

    # Determine the trading classification
    classification = range_classifications.get(current_range, f"3^{current_power}")

    return {
        'current_price': current_price,
        'current_power': current_power,
        'current_range': current_range,
        'prev_range': prev_range,
        'next_range': next_range,
        'range_position_pct': range_position,
        'classification': classification,
        'all_powers': powers_of_three,
        'scalping_range': 27,
        'daily_range': 81,
        'weekly_range': 243,
        'monthly_range': 729,
        'yearly_range': 2187
    }

def calculate_goldbach_clusters(price):
    """Calculate Goldbach clusters for market analysis"""
    # The 7 clusters of 100 from Goldbach conjecture
    clusters = [
        {'cluster': 1, 'discount': 0, 'premium': 100},
        {'cluster': 2, 'discount': 3, 'premium': 97},
        {'cluster': 3, 'discount': 11, 'premium': 89},
        {'cluster': 4, 'discount': 17, 'premium': 83},
        {'cluster': 5, 'discount': 29, 'premium': 71},  # Liquidity void cluster
        {'cluster': 6, 'discount': 41, 'premium': 59},
        {'cluster': 7, 'discount': 47, 'premium': 53}
    ]

    # Calculate price-based clusters
    price_clusters = []
    for cluster in clusters:
        discount_level = price * (1 - cluster['discount'] / 100)
        premium_level = price * (1 + cluster['premium'] / 100)

        price_clusters.append({
            'cluster': cluster['cluster'],
            'discount_pct': cluster['discount'],
            'premium_pct': cluster['premium'],
            'discount_price': discount_level,
            'premium_price': premium_level,
            'is_liquidity_void': cluster['cluster'] == 5,  # 5th cluster has 12-step jump
            'symmetry_pair': (cluster['discount'], cluster['premium'])
        })

    return price_clusters

def analyze_goldbach_support_resistance(data, price_clusters):
    """Enhanced S&R analysis using Goldbach clusters"""
    current_price = data['Close'].iloc[-1]

    # Find nearest Goldbach levels
    nearest_support_cluster = None
    nearest_resistance_cluster = None
    min_support_distance = float('inf')
    min_resistance_distance = float('inf')

    for cluster in price_clusters:
        # Check discount levels (potential support)
        if cluster['discount_price'] < current_price:
            distance = current_price - cluster['discount_price']
            if distance < min_support_distance:
                min_support_distance = distance
                nearest_support_cluster = cluster

        # Check premium levels (potential resistance)
        if cluster['premium_price'] > current_price:
            distance = cluster['premium_price'] - current_price
            if distance < min_resistance_distance:
                min_resistance_distance = distance
                nearest_resistance_cluster = cluster

    # Traditional S&R
    recent_data = data.tail(20)
    traditional_support = recent_data['Low'].min()
    traditional_resistance = recent_data['High'].max()

    # Combine traditional and Goldbach levels
    goldbach_support = nearest_support_cluster['discount_price'] if nearest_support_cluster else traditional_support
    goldbach_resistance = nearest_resistance_cluster['premium_price'] if nearest_resistance_cluster else traditional_resistance

    # Use the stronger level (closer to current price)
    final_support = max(traditional_support, goldbach_support)
    final_resistance = min(traditional_resistance, goldbach_resistance)

    return {
        'support': final_support,
        'resistance': final_resistance,
        'goldbach_support': goldbach_support,
        'goldbach_resistance': goldbach_resistance,
        'support_cluster': nearest_support_cluster,
        'resistance_cluster': nearest_resistance_cluster,
        'distance_to_support': ((current_price - final_support) / current_price) * 100,
        'distance_to_resistance': ((final_resistance - current_price) / current_price) * 100,
        'in_liquidity_void': (nearest_support_cluster and nearest_support_cluster['is_liquidity_void']) or
                           (nearest_resistance_cluster and nearest_resistance_cluster['is_liquidity_void'])
    }

def generate_market_analysis(data, symbol):
    """Generate comprehensive market analysis with Goldbach clusters"""
    latest = data.iloc[-1]
    prev = data.iloc[-2] if len(data) > 1 else latest

    analysis = {
        'symbol': symbol,
        'current_price': latest['Close'],
        'price_change': latest['Close'] - prev['Close'],
        'price_change_pct': ((latest['Close'] - prev['Close']) / prev['Close']) * 100,
        'volume': latest['Volume'],
        'signals': [],
        'support_resistance': {},
        'trend_analysis': {},
        'momentum_analysis': {},
        'volatility_analysis': {},
        'powers_of_three': {},
        'goldbach_clusters': {}
    }

    # Powers of Three Analysis
    powers_analysis = calculate_powers_of_three(latest['Close'])
    analysis['powers_of_three'] = powers_analysis

    # Goldbach Clusters Analysis
    price_clusters = calculate_goldbach_clusters(latest['Close'])
    analysis['goldbach_clusters'] = price_clusters

    # Enhanced S&R with Goldbach analysis
    sr_analysis = analyze_goldbach_support_resistance(data, price_clusters)

    # Enhanced Trend Analysis with Goldbach context
    if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
        if sr_analysis['distance_to_resistance'] < 5:  # Near Goldbach resistance
            trend = "UPTREND - APPROACHING RESISTANCE"
            trend_strength = "Moderate"
        else:
            trend = "STRONG UPTREND"
            trend_strength = "Strong"
    elif latest['Close'] > latest['SMA_20']:
        trend = "UPTREND"
        trend_strength = "Moderate"
    elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
        if sr_analysis['distance_to_support'] < 5:  # Near Goldbach support
            trend = "DOWNTREND - APPROACHING SUPPORT"
            trend_strength = "Moderate"
        else:
            trend = "STRONG DOWNTREND"
            trend_strength = "Strong"
    elif latest['Close'] < latest['SMA_20']:
        trend = "DOWNTREND"
        trend_strength = "Moderate"
    else:
        trend = "SIDEWAYS"
        trend_strength = "Weak"

    analysis['trend_analysis'] = {
        'direction': trend,
        'strength': trend_strength,
        'sma_20': latest['SMA_20'],
        'sma_50': latest['SMA_50']
    }

    # Momentum Analysis
    rsi_signal = "NEUTRAL"
    if latest['RSI'] > 70:
        rsi_signal = "OVERBOUGHT"
    elif latest['RSI'] < 30:
        rsi_signal = "OVERSOLD"

    macd_signal = "NEUTRAL"
    if latest['MACD'] > latest['MACD_Signal']:
        macd_signal = "BULLISH"
    elif latest['MACD'] < latest['MACD_Signal']:
        macd_signal = "BEARISH"

    analysis['momentum_analysis'] = {
        'rsi': latest['RSI'],
        'rsi_signal': rsi_signal,
        'macd': latest['MACD'],
        'macd_signal': macd_signal
    }

    # Enhanced Support and Resistance with Goldbach clusters
    analysis['support_resistance'] = sr_analysis

    # Enhanced Volatility Analysis with Goldbach context
    volatility = (latest['ATR'] / latest['Close']) * 100

    # Adjust volatility expectations in liquidity void areas
    if sr_analysis['in_liquidity_void']:
        volatility_threshold_high = 2.5  # Lower threshold in void areas
        volatility_threshold_moderate = 1.2
    else:
        volatility_threshold_high = 3
        volatility_threshold_moderate = 1.5

    if volatility > volatility_threshold_high:
        vol_signal = "HIGH"
    elif volatility > volatility_threshold_moderate:
        vol_signal = "MODERATE"
    else:
        vol_signal = "LOW"

    analysis['volatility_analysis'] = {
        'atr': latest['ATR'],
        'volatility_pct': volatility,
        'volatility_signal': vol_signal,
        'in_liquidity_void': sr_analysis['in_liquidity_void']
    }

    # Enhanced Trading Signals with Goldbach integration
    signals = []

    # Volume analysis with Goldbach context
    volume_ratio = latest['Volume_Ratio']
    if sr_analysis['in_liquidity_void']:
        volume_multiplier = 1.5  # Expect higher volume in liquidity void areas
        volume_threshold = 1.2 * volume_multiplier
    else:
        volume_threshold = 1.2

    # Goldbach-based signals
    if sr_analysis['support_cluster'] and sr_analysis['distance_to_support'] < 3:
        if volume_ratio > volume_threshold:
            signals.append({
                'type': 'BUY',
                'reason': f'Price near Goldbach support cluster {sr_analysis["support_cluster"]["cluster"]} with high volume',
                'strength': 'Strong' if sr_analysis['support_cluster']['is_liquidity_void'] else 'Moderate',
                'confidence': 0.85 if sr_analysis['support_cluster']['is_liquidity_void'] else 0.75
            })

    if sr_analysis['resistance_cluster'] and sr_analysis['distance_to_resistance'] < 3:
        if volume_ratio > volume_threshold:
            signals.append({
                'type': 'SELL',
                'reason': f'Price near Goldbach resistance cluster {sr_analysis["resistance_cluster"]["cluster"]} with high volume',
                'strength': 'Strong' if sr_analysis['resistance_cluster']['is_liquidity_void'] else 'Moderate',
                'confidence': 0.85 if sr_analysis['resistance_cluster']['is_liquidity_void'] else 0.75
            })

    # RSI Signals with Goldbach context
    if latest['RSI'] < 30 and trend in ["UPTREND", "STRONG UPTREND"] and not sr_analysis['in_liquidity_void']:
        signals.append({
            'type': 'BUY',
            'reason': 'RSI Oversold in Uptrend, clear of liquidity voids',
            'strength': 'Strong',
            'confidence': 0.8
        })
    elif latest['RSI'] > 70 and trend in ["DOWNTREND", "STRONG DOWNTREND"] and not sr_analysis['in_liquidity_void']:
        signals.append({
            'type': 'SELL',
            'reason': 'RSI Overbought in Downtrend, clear of liquidity voids',
            'strength': 'Strong',
            'confidence': 0.8
        })

    # MACD Signals
    if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
        signals.append({
            'type': 'BUY',
            'reason': 'MACD Bullish Crossover',
            'strength': 'Moderate',
            'confidence': 0.6
        })
    elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
        signals.append({
            'type': 'SELL',
            'reason': 'MACD Bearish Crossover',
            'strength': 'Moderate',
            'confidence': 0.6
        })

    # Liquidity void signals
    if sr_analysis['in_liquidity_void'] and volume_ratio > 1.8:
        signals.append({
            'type': 'BUY' if analysis['price_change_pct'] > 0 else 'SELL',
            'reason': 'High volume activity in Goldbach liquidity void area - expect rapid price movement',
            'strength': 'Strong',
            'confidence': 0.9
        })

    # Trend-based signals with Goldbach context
    if "STRONG UPTREND" in trend and not sr_analysis['in_liquidity_void']:
        signals.append({
            'type': 'BUY',
            'reason': 'Strong uptrend with price above key SMAs, clear of liquidity voids',
            'strength': 'Strong',
            'confidence': 0.8
        })
    elif "STRONG DOWNTREND" in trend and not sr_analysis['in_liquidity_void']:
        signals.append({
            'type': 'SELL',
            'reason': 'Strong downtrend with price below key SMAs, clear of liquidity voids',
            'strength': 'Strong',
            'confidence': 0.8
        })

    # Volume Confirmation
    if volume_ratio > 1.5:
        for signal in signals:
            signal['confidence'] = min(1.0, signal['confidence'] + 0.1)  # Boost confidence with high volume

    analysis['signals'] = signals

    return analysis

def create_advanced_chart(data, symbol):
    """Create professional price chart with volume"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Price Chart', 'Volume'),
        row_heights=[0.8, 0.2]
    )

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444',
        increasing_fillcolor='#00ff88',
        decreasing_fillcolor='#ff4444'
    ), row=1, col=1)



    # Volume with better colors
    colors = ['#00ff88' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#ff4444'
              for i in range(len(data))]

    fig.add_trace(go.Bar(
        x=data.index, y=data['Volume'],
        marker_color=colors,
        name='Volume',
        opacity=0.7
    ), row=2, col=1)

    # Update layout for professional appearance
    fig.update_layout(
        title={
            'text': f'{symbol} Technical Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_rangeslider_visible=False,
        height=700,
        showlegend=True,
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#000000',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Update axes
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )

    return fig

def enhanced_market_data_page():
    """Enhanced market data page with comprehensive analysis"""
    st.markdown("## ADVANCED MARKET ANALYSIS")

    # Symbol input
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        symbol = st.text_input("Enter Symbol", value="AAPL", placeholder="e.g., AAPL, TSLA, SPY")

    with col2:
        period = st.selectbox("Period", ["6mo", "1mo"], index=0)

    with col3:
        interval = st.selectbox("Timeframe", ["1d", "4h"], index=0)

    with col4:
        if st.button("ANALYZE", type="primary"):
            if symbol:
                try:
                    # Fetch data
                    with st.spinner(f"Fetching data for {symbol}..."):
                        ticker = yf.Ticker(symbol.upper())
                        data = ticker.history(period=period, interval=interval)
                        info = ticker.info

                    if not data.empty:
                        # Calculate indicators
                        with st.spinner("Calculating technical indicators..."):
                            data_with_indicators = calculate_technical_indicators(data)

                        # Generate analysis
                        with st.spinner("Generating market analysis..."):
                            analysis = generate_market_analysis(data_with_indicators, symbol.upper())

                        # Store in session state
                        st.session_state.analysis_data = data_with_indicators
                        st.session_state.analysis_results = analysis
                        st.session_state.symbol_info = info

                        st.success(f"Analysis completed for {symbol.upper()}!")
                    else:
                        st.error(f"No data found for {symbol}")

                except Exception as e:
                    st.error(f"Error analyzing {symbol}: {e}")

    # Display analysis if available
    if hasattr(st.session_state, 'analysis_results'):
        analysis = st.session_state.analysis_results
        data = st.session_state.analysis_data
        info = st.session_state.symbol_info

        # Header with current price
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Price",
                f"${analysis['current_price']:.2f}",
                f"{analysis['price_change']:+.2f} ({analysis['price_change_pct']:+.2f}%)"
            )

        with col2:
            st.metric("Volume", f"{analysis['volume']:,}")

        with col3:
            st.metric("Company", info.get('longName', 'N/A')[:20])

        with col4:
            st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else "N/A")

        # Advanced Chart
        st.markdown("### TECHNICAL ANALYSIS CHART")
        chart = create_advanced_chart(data, analysis['symbol'])
        st.plotly_chart(chart, use_container_width=True)

        # Interactive Analysis sections
        col1, col2 = st.columns(2)

        with col1:
            # Interactive Trend Analysis
            st.markdown("### TREND ANALYSIS")
            trend = analysis['trend_analysis']

            # Trend direction indicator with color coding
            trend_color = "#00ff88" if "UP" in trend['direction'] else "#ff4444" if "DOWN" in trend['direction'] else "#ffcc00"
            strength_color = "#00ff88" if trend['strength'] == "Strong" else "#ffcc00" if trend['strength'] == "Moderate" else "#ff4444"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid {trend_color}; border-radius: 12px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 18px; font-weight: bold; color: {trend_color};">
                        {trend['direction']}
                    </div>
                    <div style="background: {strength_color}; color: black; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                        {trend['strength']}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="background: rgba(255,102,0,0.1); border: 1px solid #ff6600; border-radius: 8px; padding: 12px; text-align: center;">
                        <div style="font-size: 12px; opacity: 0.8;">SMA 20</div>
                        <div style="font-size: 16px; font-weight: bold; color: #ff6600;">${trend['sma_20']:.2f}</div>
                    </div>
                    <div style="background: rgba(0,153,255,0.1); border: 1px solid #0099ff; border-radius: 8px; padding: 12px; text-align: center;">
                        <div style="font-size: 12px; opacity: 0.8;">SMA 50</div>
                        <div style="font-size: 16px; font-weight: bold; color: #0099ff;">${trend['sma_50']:.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Interactive Support & Resistance
            st.markdown("### SUPPORT & RESISTANCE")
            sr = analysis['support_resistance']

            # Calculate visual indicators for distance
            support_distance = sr['distance_to_support']
            resistance_distance = sr['distance_to_resistance']

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid rgba(128,128,128,0.5); border-radius: 12px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: rgba(255,68,68,0.1); border: 2px solid #ff4444; border-radius: 10px; padding: 15px; text-align: center; position: relative;">
                        <div style="font-size: 14px; font-weight: bold; color: #ff4444; margin-bottom: 8px;">SUPPORT</div>
                        <div style="font-size: 18px; font-weight: bold; color: white;">${sr['support']:.2f}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">{support_distance:.1f}% away</div>
                        <div style="position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); width: 80%; height: 4px; background: rgba(255,68,68,0.3); border-radius: 2px;">
                            <div style="width: {min(100, support_distance * 5)}%; height: 100%; background: #ff4444; border-radius: 2px;"></div>
                        </div>
                    </div>
                    <div style="background: rgba(0,255,136,0.1); border: 2px solid #00ff88; border-radius: 10px; padding: 15px; text-align: center; position: relative;">
                        <div style="font-size: 14px; font-weight: bold; color: #00ff88; margin-bottom: 8px;">RESISTANCE</div>
                        <div style="font-size: 18px; font-weight: bold; color: white;">${sr['resistance']:.2f}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">{resistance_distance:.1f}% away</div>
                        <div style="position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); width: 80%; height: 4px; background: rgba(0,255,136,0.3); border-radius: 2px;">
                            <div style="width: {min(100, resistance_distance * 5)}%; height: 100%; background: #00ff88; border-radius: 2px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Interactive Volatility Analysis
            st.markdown("### VOLATILITY ANALYSIS")
            vol = analysis['volatility_analysis']

            # Volatility level indicator
            vol_color = "#ff4444" if vol['volatility_signal'] == "HIGH" else "#ffcc00" if vol['volatility_signal'] == "MODERATE" else "#00ff88"
            vol_percentage = min(100, (vol['volatility_pct'] / 5) * 100)  # Scale for visual

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid {vol_color}; border-radius: 12px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold;">ATR: ${vol['atr']:.2f}</div>
                    <div style="background: {vol_color}; color: black; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{vol['volatility_signal']}</div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 14px; margin-bottom: 8px;">Volatility: {vol['volatility_pct']:.2f}%</div>
                    <div style="width: 100%; height: 12px; background: rgba(128,128,128,0.3); border-radius: 6px; overflow: hidden;">
                        <div style="width: {vol_percentage}%; height: 100%; background: linear-gradient(90deg, {vol_color}, rgba(255,255,255,0.3)); border-radius: 6px; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Interactive Volume Analysis
            st.markdown("### VOLUME ANALYSIS")
            volume_ratio = data.iloc[-1]['Volume_Ratio']

            # Volume status color coding
            if volume_ratio > 1.5:
                vol_status = "High volume activity"
                vol_status_color = "#ff4444"
            elif volume_ratio > 1.2:
                vol_status = "Above average volume"
                vol_status_color = "#ffcc00"
            else:
                vol_status = "Normal volume"
                vol_status_color = "#00ff88"

            volume_percentage = min(100, (volume_ratio / 2) * 100)  # Scale for visual

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid {vol_status_color}; border-radius: 12px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold;">Volume Analysis</div>
                    <div style="background: {vol_status_color}; color: black; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{vol_status.split()[0].upper()}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 14px; opacity: 0.8;">Current Volume</div>
                    <div style="font-size: 18px; font-weight: bold; color: white;">{analysis['volume']:,}</div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 14px; margin-bottom: 8px;">Volume Ratio: {volume_ratio:.2f}x average</div>
                    <div style="width: 100%; height: 12px; background: rgba(128,128,128,0.3); border-radius: 6px; overflow: hidden;">
                        <div style="width: {volume_percentage}%; height: 100%; background: linear-gradient(90deg, {vol_status_color}, rgba(255,255,255,0.3)); border-radius: 6px; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8; text-align: center;">{vol_status}</div>
            </div>
            """, unsafe_allow_html=True)

        # Interactive Trading Signals
        st.markdown("### TRADING SIGNALS")

        if analysis['signals']:
            for i, signal in enumerate(analysis['signals']):
                # Signal type color coding
                signal_color = "#00ff88" if signal['type'] == "BUY" else "#ff4444"
                signal_bg_color = "rgba(0,255,136,0.1)" if signal['type'] == "BUY" else "rgba(255,68,68,0.1)"

                # Strength color coding
                strength_color = "#00ff88" if signal['strength'] == "Strong" else "#ffcc00" if signal['strength'] == "Moderate" else "#ff9999"

                # Confidence percentage for visual bar
                confidence_percentage = signal['confidence'] * 100

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid {signal_color}; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: {signal_bg_color}; opacity: 0.1;"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; position: relative; z-index: 1;">
                        <div style="font-size: 20px; font-weight: bold; color: {signal_color}; text-shadow: 0 0 10px {signal_color};">{signal['type']} SIGNAL</div>
                        <div style="background: {strength_color}; color: black; padding: 6px 15px; border-radius: 25px; font-size: 12px; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">{signal['strength'].upper()}</div>
                    </div>
                    <div style="margin-bottom: 15px; position: relative; z-index: 1;">
                        <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Reason:</div>
                        <div style="font-size: 16px; font-weight: bold; color: white;">{signal['reason']}</div>
                    </div>
                    <div style="position: relative; z-index: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 14px; opacity: 0.8;">Confidence</span>
                            <span style="font-size: 16px; font-weight: bold; color: {signal_color};">{signal['confidence']:.1%}</span>
                        </div>
                        <div style="width: 100%; height: 15px; background: rgba(128,128,128,0.3); border-radius: 8px; overflow: hidden; position: relative;">
                            <div style="width: {confidence_percentage}%; height: 100%; background: linear-gradient(90deg, {signal_color}, rgba(255,255,255,0.3)); border-radius: 8px; transition: width 0.5s ease; box-shadow: 0 0 10px {signal_color};"></div>
                            <div style="position: absolute; top: 0; left: 50%; width: 1px; height: 100%; background: rgba(255,255,255,0.3);"></div>
                            <div style="position: absolute; top: 0; left: 75%; width: 1px; height: 100%; background: rgba(255,255,255,0.3);"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 10px; opacity: 0.6; margin-top: 3px;">
                            <span>0%</span>
                            <span>50%</span>
                            <span>75%</span>
                            <span>100%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # No signals - neutral market display
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid #ffcc00; border-radius: 12px; padding: 30px; margin: 15px 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="font-size: 24px; margin-bottom: 10px; opacity: 0.7;">⚖️</div>
                <div style="font-size: 18px; font-weight: bold; color: #ffcc00; margin-bottom: 10px;">NEUTRAL MARKET</div>
                <div style="font-size: 14px; opacity: 0.8; color: white;">No clear trading signals at this time.<br>Market appears to be in a consolidation phase.</div>
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,204,0,0.1); border-radius: 8px; font-size: 12px; opacity: 0.7;">Consider waiting for clearer directional signals before entering positions.</div>
            </div>
            """, unsafe_allow_html=True)

        # Goldbach Clusters Analysis
        st.markdown("### GOLDBACH CLUSTERS ANALYSIS")

        goldbach_clusters = analysis['goldbach_clusters']
        sr = analysis['support_resistance']

        # Display Goldbach clusters information
        st.markdown("#### THE 7 CLUSTERS OF 100")

        # Create interactive cluster display
        cluster_cols = st.columns(7)
        for i, cluster in enumerate(goldbach_clusters):
            with cluster_cols[i]:
                is_support = sr['support_cluster'] and sr['support_cluster']['cluster'] == cluster['cluster']
                is_resistance = sr['resistance_cluster'] and sr['resistance_cluster']['cluster'] == cluster['cluster']
                is_liquidity_void = cluster['is_liquidity_void']

                # Color coding based on cluster significance
                if is_liquidity_void:
                    border_color = "#ff4444"  # Red for liquidity void
                    bg_color = "rgba(255,68,68,0.1)"
                elif is_support or is_resistance:
                    border_color = "#00ff88"  # Green for active S&R
                    bg_color = "rgba(0,255,136,0.1)"
                else:
                    border_color = "rgba(128,128,128,0.5)"
                    bg_color = "rgba(128,128,128,0.05)"

                st.markdown(f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 10px; text-align: center; margin: 5px 0; min-height: 120px;">
                    <div style="font-size: 14px; font-weight: bold; color: {border_color}; margin-bottom: 5px;">Cluster {cluster['cluster']}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-bottom: 8px;">
                        {cluster['discount_pct']}% | {cluster['premium_pct']}%
                    </div>
                    <div style="font-size: 11px; margin-bottom: 3px;">
                        <div style="color: #ff6666;">Discount: ${cluster['discount_price']:.2f}</div>
                        <div style="color: #66ff66;">Premium: ${cluster['premium_price']:.2f}</div>
                    </div>
                    {'<div style="font-size: 10px; color: #ff4444; font-weight: bold;">LIQUIDITY VOID</div>' if is_liquidity_void else ''}
                    {'<div style="font-size: 10px; color: #00ff88; font-weight: bold;">ACTIVE SUPPORT</div>' if is_support else ''}
                    {'<div style="font-size: 10px; color: #00ff88; font-weight: bold;">ACTIVE RESISTANCE</div>' if is_resistance else ''}
                </div>
                """, unsafe_allow_html=True)

        # Market symmetry explanation
        st.markdown("#### MARKET SYMMETRY & LIQUIDITY VOIDS")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid #ffcc00; border-radius: 12px; padding: 20px; margin: 10px 0;">
                <div style="font-size: 16px; font-weight: bold; color: #ffcc00; margin-bottom: 15px;">SYMMETRY PAIRS</div>
                <div style="font-size: 14px; margin-bottom: 10px;">Each cluster shows market symmetry:</div>
                <div style="font-size: 12px; opacity: 0.8;">
                    • Cluster 3: 11% ↔ 89% (symmetrical)<br>
                    • Cluster 4: 17% ↔ 83% (symmetrical)<br>
                    • Cluster 6: 41% ↔ 59% (symmetrical)<br>
                    • Cluster 7: 47% ↔ 53% (symmetrical)
                </div>
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,204,0,0.1); border-radius: 8px; font-size: 12px;">
                    Low numbers pair with high numbers as symmetrical opposites
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid #ff4444; border-radius: 12px; padding: 20px; margin: 10px 0;">
                <div style="font-size: 16px; font-weight: bold; color: #ff4444; margin-bottom: 15px;">LIQUIDITY VOID</div>
                <div style="font-size: 14px; margin-bottom: 10px;">Cluster 5 (29% ↔ 71%):</div>
                <div style="font-size: 12px; opacity: 0.8;">
                    • 12-step jump (largest gap)<br>
                    • Where liquidity voids reside<br>
                    • Expect rapid price movement<br>
                    • Higher volume activity
                </div>
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,68,68,0.1); border-radius: 8px; font-size: 12px;">
                    {'🔴 CURRENTLY IN LIQUIDITY VOID' if sr['in_liquidity_void'] else '✅ Clear of liquidity voids'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Current position relative to Goldbach levels
        st.markdown("#### CURRENT POSITION vs GOLDBACH LEVELS")

        current_price = analysis['current_price']

        # Find the closest clusters above and below current price
        support_clusters = [c for c in goldbach_clusters if c['discount_price'] < current_price]
        resistance_clusters = [c for c in goldbach_clusters if c['premium_price'] > current_price]

        if support_clusters and resistance_clusters:
            nearest_support = max(support_clusters, key=lambda x: x['discount_price'])
            nearest_resistance = min(resistance_clusters, key=lambda x: x['premium_price'])

            # Calculate position between nearest levels
            total_range = nearest_resistance['premium_price'] - nearest_support['discount_price']
            position_in_range = (current_price - nearest_support['discount_price']) / total_range * 100

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid #00ff88; border-radius: 12px; padding: 20px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div style="text-align: center; padding: 10px; background: rgba(255,68,68,0.1); border: 1px solid #ff4444; border-radius: 8px;">
                        <div style="font-size: 12px; opacity: 0.8;">Nearest Support</div>
                        <div style="font-size: 16px; font-weight: bold; color: #ff4444;">Cluster {nearest_support['cluster']}</div>
                        <div style="font-size: 14px;">${nearest_support['discount_price']:.2f}</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.1); border: 1px solid #ffffff; border-radius: 8px;">
                        <div style="font-size: 12px; opacity: 0.8;">Current Price</div>
                        <div style="font-size: 16px; font-weight: bold; color: #ffffff;">${current_price:.2f}</div>
                        <div style="font-size: 12px; color: #00ff88;">{position_in_range:.1f}% in range</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: rgba(0,255,136,0.1); border: 1px solid #00ff88; border-radius: 8px;">
                        <div style="font-size: 12px; opacity: 0.8;">Nearest Resistance</div>
                        <div style="font-size: 16px; font-weight: bold; color: #00ff88;">Cluster {nearest_resistance['cluster']}</div>
                        <div style="font-size: 14px;">${nearest_resistance['premium_price']:.2f}</div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 14px; margin-bottom: 8px;">Position between Goldbach levels:</div>
                    <div style="width: 100%; height: 20px; background: rgba(128,128,128,0.3); border-radius: 10px; overflow: hidden; position: relative;">
                        <div style="width: {position_in_range}%; height: 100%; background: linear-gradient(90deg, #ff4444, #00ff88); border-radius: 10px; transition: width 0.5s ease;"></div>
                        <div style="position: absolute; top: 50%; left: {position_in_range}%; transform: translate(-50%, -50%); color: white; font-size: 12px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{position_in_range:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Powers of Three Analysis
        st.markdown("### POWERS OF THREE ANALYSIS")

        powers = analysis['powers_of_three']

        # Interactive Current Range Position
        st.markdown("#### CURRENT RANGE POSITION")

        # Calculate position percentage for visual indicator
        position_percentage = powers['range_position_pct']
        position_color = "#00ff88" if position_percentage < 30 else "#ffcc00" if position_percentage < 70 else "#ff4444"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(40,40,40,0.8)); border: 2px solid {position_color}; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Current Price</div>
                    <div style="font-size: 24px; font-weight: bold; color: white;">${powers['current_price']:.2f}</div>
                </div>
                <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Power Range</div>
                    <div style="font-size: 20px; font-weight: bold; color: #00ff88;">3^{powers['current_power']} = {powers['current_range']:,}</div>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">Classification: <span style="color: #ffcc00;">{powers['classification']}</span></div>
                <div style="font-size: 14px; margin-bottom: 8px;">Position in Range: <span style="color: {position_color}; font-weight: bold;">{powers['range_position_pct']:.1f}%</span></div>
                <div style="width: 100%; height: 20px; background: rgba(128,128,128,0.3); border-radius: 10px; overflow: hidden; position: relative;">
                    <div style="width: {position_percentage}%; height: 100%; background: linear-gradient(90deg, {position_color}, rgba(255,255,255,0.3)); border-radius: 10px; transition: width 0.5s ease;"></div>
                    <div style="position: absolute; top: 0; left: 30%; width: 1px; height: 100%; background: rgba(255,255,255,0.5);"></div>
                    <div style="position: absolute; top: 0; left: 70%; width: 1px; height: 100%; background: rgba(255,255,255,0.5);"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; opacity: 0.6; margin-top: 3px;">
                    <span style="color: #00ff88;">Support Zone</span>
                    <span style="color: #ffcc00;">Mid Range</span>
                    <span style="color: #ff4444;">Resistance Zone</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                {f'<div style="background: rgba(255,68,68,0.1); border: 1px solid #ff4444; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 12px; opacity: 0.8;">Previous Range</div><div style="font-size: 16px; font-weight: bold; color: #ff4444;">{powers["prev_range"]:,}</div></div>' if powers['prev_range'] else ''}
                {f'<div style="background: rgba(0,255,136,0.1); border: 1px solid #00ff88; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 12px; opacity: 0.8;">Next Range</div><div style="font-size: 16px; font-weight: bold; color: #00ff88;">{powers["next_range"]:,}</div></div>' if powers['next_range'] else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Interactive Trading Ranges
        st.markdown("#### TRADING RANGES")

        # Create interactive range cards
        trading_ranges = [
            ("Scalping Range", "3³", powers['scalping_range'], "#ff6600"),
            ("Daily Range", "3⁴", powers['daily_range'], "#0099ff"),
            ("Weekly Range", "3⁵", powers['weekly_range'], "#00cc66"),
            ("Monthly Range", "3⁶", powers['monthly_range'], "#ffcc00"),
            ("Yearly Range", "3⁷", powers['yearly_range'], "#cc0000")
        ]

        # Display ranges in a grid
        cols = st.columns(len(trading_ranges))
        for i, (name, power, value, color) in enumerate(trading_ranges):
            with cols[i]:
                is_current = value == powers['current_range']

                st.markdown(f"""
                <div style="background: {'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(40,40,40,0.8))' if is_current else 'rgba(128,128,128,0.05)'}; border: {'3px solid ' + color if is_current else '1px solid rgba(128,128,128,0.3)'}; border-radius: 10px; padding: 15px; text-align: center; margin: 5px 0; box-shadow: {'0 0 15px rgba(255,255,255,0.3)' if is_current else 'none'}; transition: all 0.3s ease;">
                    <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">{name}</div>
                    <div style="font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 5px;">{power}</div>
                    <div style="font-size: 14px; font-weight: bold; color: white;">{value:,}</div>
                    <div style="font-size: 10px; opacity: 0.6;">points</div>
                    {'<div style="font-size: 10px; color: #00ff88; font-weight: bold; margin-top: 5px;">← CURRENT</div>' if is_current else ''}
                </div>
                """, unsafe_allow_html=True)

        # Interactive Powers of Three Display
        st.markdown("#### INTERACTIVE POWERS OF THREE")

        # Create visual range selector
        st.markdown("**Select a range to view details:**")

        # Create columns for the interactive display
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Create interactive buttons for each major range
            major_ranges = [
                (3, 27, "Scalping", "#ff6600"),
                (4, 81, "Daily Range", "#0099ff"),
                (5, 243, "Weekly Range", "#00cc66"),
                (6, 729, "Monthly Range", "#ffcc00"),
                (7, 2187, "Yearly Range", "#cc0000")
            ]

            # Display range buttons in a grid
            for i, (power, value, classification, color) in enumerate(major_ranges):
                is_current = value == powers['current_range']

                # Create button styling
                button_style = f"""
                <div style="background: {'linear-gradient(45deg, ' + color + ', rgba(255,255,255,0.1))' if is_current else 'rgba(128,128,128,0.1)'}; border: {'3px solid ' + color if is_current else '1px solid rgba(128,128,128,0.3)'}; border-radius: 10px; padding: 15px; margin: 5px 0; text-align: center; color: white; font-weight: {'bold' if is_current else 'normal'}; box-shadow: {'0 0 15px rgba(255,255,255,0.3)' if is_current else 'none'};">
                    <div style="font-size: 18px;">3^{power} = {value:,}</div>
                    <div style="font-size: 14px; opacity: 0.8;">{classification}</div>
                    {'<div style="font-size: 12px; color: #00ff88;">← CURRENT PRICE RANGE</div>' if is_current else ''}
                </div>
                """

                st.markdown(button_style, unsafe_allow_html=True)

        # Price position visualization
        st.markdown("---")
        st.markdown("#### PRICE POSITION VISUALIZATION")

        # Create a visual progress bar showing position in current range
        if powers['prev_range']:
            progress_value = powers['range_position_pct'] / 100

            st.markdown(f"""
            <div style="margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>3^{powers['current_power']-1} = {powers['prev_range']:,}</span>
                    <span style="color: #00ff88; font-weight: bold;">${powers['current_price']:.2f}</span>
                    <span>3^{powers['current_power']} = {powers['current_range']:,}</span>
                </div>
                <div style="width: 100%; height: 20px; background: linear-gradient(90deg, #333 0%, #666 100%); border-radius: 10px; position: relative; overflow: hidden;">
                    <div style="width: {progress_value * 100}%; height: 100%; background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%); border-radius: 10px; transition: width 0.3s ease;"></div>
                    <div style="position: absolute; top: 50%; left: {progress_value * 100}%; transform: translate(-50%, -50%); color: white; font-size: 12px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{powers['range_position_pct']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # All powers overview with interactive elements
        st.markdown("#### ALL POWERS OF THREE")

        # Create expandable sections for different power groups
        with st.expander("🔍 Lower Powers (3¹ - 3³)", expanded=False):
            cols = st.columns(3)
            for i, (power, value) in enumerate([(1, 3), (2, 9), (3, 27)]):
                with cols[i]:
                    is_current = value == powers['current_range']
                    classification = "Scalping" if value == 27 else ""

                    st.markdown(f"""
                    <div style="background: {'rgba(255, 102, 0, 0.2)' if is_current else 'rgba(128,128,128,0.1)'}; border: {'2px solid #ff6600' if is_current else '1px solid rgba(128,128,128,0.3)'}; border-radius: 8px; padding: 10px; text-align: center; margin: 5px 0;">
                        <div style="font-size: 16px; font-weight: bold;">3^{power}</div>
                        <div style="font-size: 14px;">{value:,}</div>
                        <div style="font-size: 12px; opacity: 0.8;">{classification}</div>
                        {'<div style="font-size: 10px; color: #00ff88;">CURRENT</div>' if is_current else ''}
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("📈 Trading Powers (3⁴ - 3⁷)", expanded=True):
            cols = st.columns(4)
            trading_powers = [(4, 81, "Daily"), (5, 243, "Weekly"), (6, 729, "Monthly"), (7, 2187, "Yearly")]

            for i, (power, value, timeframe) in enumerate(trading_powers):
                with cols[i]:
                    is_current = value == powers['current_range']
                    colors = ["#0099ff", "#00cc66", "#ffcc00", "#cc0000"]

                    st.markdown(f"""
                    <div style="background: {'rgba(255, 255, 255, 0.1)' if is_current else 'rgba(128,128,128,0.05)'}; border: {'3px solid ' + colors[i] if is_current else '1px solid rgba(128,128,128,0.3)'}; border-radius: 8px; padding: 15px; text-align: center; margin: 5px 0; box-shadow: {'0 0 10px rgba(255,255,255,0.2)' if is_current else 'none'};">
                        <div style="font-size: 18px; font-weight: bold; color: {colors[i]};">3^{power}</div>
                        <div style="font-size: 16px; font-weight: bold;">{value:,}</div>
                        <div style="font-size: 12px; opacity: 0.8;">{timeframe} Range</div>
                        {'<div style="font-size: 10px; color: #00ff88; font-weight: bold;">← CURRENT</div>' if is_current else ''}
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("🚀 Higher Powers (3⁸ - 3¹¹)", expanded=False):
            cols = st.columns(4)
            higher_powers = [(8, 6561), (9, 19683), (10, 59049), (11, 177147)]

            for i, (power, value) in enumerate(higher_powers):
                with cols[i]:
                    is_current = value == powers['current_range']

                    st.markdown(f"""
                    <div style="background: {'rgba(255, 255, 255, 0.1)' if is_current else 'rgba(128,128,128,0.05)'}; border: {'2px solid #ffffff' if is_current else '1px solid rgba(128,128,128,0.3)'}; border-radius: 8px; padding: 10px; text-align: center; margin: 5px 0;">
                        <div style="font-size: 16px; font-weight: bold;">3^{power}</div>
                        <div style="font-size: 14px;">{value:,}</div>
                        {'<div style="font-size: 10px; color: #00ff88;">CURRENT</div>' if is_current else ''}
                    </div>
                    """, unsafe_allow_html=True)

        # Enhanced Key Metrics Table with Goldbach integration
        st.markdown("### KEY METRICS")

        # Goldbach cluster information
        goldbach_support_info = f"Cluster {sr['support_cluster']['cluster']}" if sr['support_cluster'] else "Traditional"
        goldbach_resistance_info = f"Cluster {sr['resistance_cluster']['cluster']}" if sr['resistance_cluster'] else "Traditional"

        metrics_data = {
            'Metric': [
                'Current Price',
                'ATR',
                'Volume Ratio',
                'Goldbach Support',
                'Goldbach Resistance',
                'Powers of 3 Range',
                'Liquidity Status',
                'Market Symmetry'
            ],
            'Value': [
                f"${analysis['current_price']:.2f}",
                f"${vol['atr']:.2f}",
                f"{data.iloc[-1]['Volume_Ratio']:.2f}x",
                f"${sr['support']:.2f}",
                f"${sr['resistance']:.2f}",
                f"3^{powers['current_power']} = {powers['current_range']:,}",
                "IN VOID" if sr['in_liquidity_void'] else "CLEAR",
                f"{len([c for c in goldbach_clusters if c['symmetry_pair'][0] + c['symmetry_pair'][1] == 100])} pairs"
            ],
            'Status': [
                "UP" if analysis['price_change'] > 0 else "DOWN",
                vol['volatility_signal'],
                "HIGH" if data.iloc[-1]['Volume_Ratio'] > 1.2 else "NORMAL",
                goldbach_support_info,
                goldbach_resistance_info,
                powers['classification'],
                "🔴 CAUTION" if sr['in_liquidity_void'] else "✅ SAFE",
                "MATHEMATICAL"
            ]
        }

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    enhanced_market_data_page()
