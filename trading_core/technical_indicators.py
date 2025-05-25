"""
Technical Indicators for Trading Strategy
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Tuple, Optional
import logging

class TechnicalIndicators:
    """Collection of technical indicators for strategy development"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a given dataset"""
        df = data.copy()

        # Trend Indicators
        df = self.add_moving_averages(df)
        df = self.add_bollinger_bands(df)
        df = self.add_macd(df)

        # Momentum Indicators
        df = self.add_rsi(df)
        df = self.add_stochastic(df)
        df = self.add_williams_r(df)

        # Volatility Indicators
        df = self.add_atr(df)
        df = self.add_volatility_bands(df)

        # Volume Indicators (if volume data available)
        if 'volume' in df.columns and not df['volume'].isna().all():
            df = self.add_volume_indicators(df)

        # Support/Resistance
        df = self.add_pivot_points(df)
        df = self.add_fibonacci_levels(df)

        return df

    def add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add various moving averages"""
        # Simple Moving Averages
        df['sma_10'] = ta.sma(df['close'], length=10)
        df['sma_20'] = ta.sma(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['sma_200'] = ta.sma(df['close'], length=200)

        # Exponential Moving Averages
        df['ema_10'] = ta.ema(df['close'], length=10)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_50'] = ta.ema(df['close'], length=50)

        # Moving Average Convergence (handle NaN values)
        ema_20_valid = df['ema_20'].fillna(0)
        sma_50_valid = df['sma_50'].fillna(0)
        df['ma_signal'] = np.where(ema_20_valid > sma_50_valid, 1,
                                  np.where(ema_20_valid < sma_50_valid, -1, 0))

        return df

    def add_bollinger_bands(self, df: pd.DataFrame, length: int = 20, std: float = 2) -> pd.DataFrame:
        """Add Bollinger Bands"""
        bb = ta.bbands(df['close'], length=length, std=std)

        # Handle different possible column naming formats
        if bb is not None and not bb.empty:
            # Try different column name formats
            possible_upper = [f'BBU_{length}_{std}', f'BBU_{length}_{std:.0f}', 'BBU_20_2.0']
            possible_middle = [f'BBM_{length}_{std}', f'BBM_{length}_{std:.0f}', 'BBM_20_2.0']
            possible_lower = [f'BBL_{length}_{std}', f'BBL_{length}_{std:.0f}', 'BBL_20_2.0']

            # Find the correct column names
            upper_col = next((col for col in possible_upper if col in bb.columns), bb.columns[0] if len(bb.columns) >= 3 else None)
            middle_col = next((col for col in possible_middle if col in bb.columns), bb.columns[1] if len(bb.columns) >= 3 else None)
            lower_col = next((col for col in possible_lower if col in bb.columns), bb.columns[2] if len(bb.columns) >= 3 else None)

            if upper_col and middle_col and lower_col:
                df['bb_upper'] = bb[upper_col]
                df['bb_middle'] = bb[middle_col]
                df['bb_lower'] = bb[lower_col]

                # Calculate derived metrics with NaN handling
                df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'].replace(0, np.nan)
                bb_range = df['bb_upper'] - df['bb_lower']
                df['bb_position'] = np.where(bb_range != 0, (df['close'] - df['bb_lower']) / bb_range, 0.5)
            else:
                # Fallback: create empty columns
                df['bb_upper'] = np.nan
                df['bb_middle'] = np.nan
                df['bb_lower'] = np.nan
                df['bb_width'] = np.nan
                df['bb_position'] = 0.5
        else:
            # Fallback: create empty columns
            df['bb_upper'] = np.nan
            df['bb_middle'] = np.nan
            df['bb_lower'] = np.nan
            df['bb_width'] = np.nan
            df['bb_position'] = 0.5

        return df

    def add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD indicator"""
        try:
            # Check if we have enough data for MACD (needs at least 34 periods)
            if len(df) < 34:
                self.logger.warning(f"Insufficient data for MACD calculation: {len(df)} rows (need 34+)")
                df['macd'] = np.nan
                df['macd_signal'] = np.nan
                df['macd_histogram'] = np.nan
                df['macd_bullish'] = False
                df['macd_bearish'] = False
                return df

            macd = ta.macd(df['close'])

            if macd is not None and not macd.empty:
                # Handle different possible column names
                macd_cols = [col for col in macd.columns if 'MACD' in col and 'h' not in col and 's' not in col]
                signal_cols = [col for col in macd.columns if 'MACDs' in col]
                hist_cols = [col for col in macd.columns if 'MACDh' in col]

                df['macd'] = macd[macd_cols[0]] if macd_cols else np.nan
                df['macd_signal'] = macd[signal_cols[0]] if signal_cols else np.nan
                df['macd_histogram'] = macd[hist_cols[0]] if hist_cols else np.nan

                # MACD signals (with NaN handling)
                macd_valid = df['macd'].fillna(0)
                signal_valid = df['macd_signal'].fillna(0)
                df['macd_bullish'] = (macd_valid > signal_valid) & (macd_valid.shift(1) <= signal_valid.shift(1))
                df['macd_bearish'] = (macd_valid < signal_valid) & (macd_valid.shift(1) >= signal_valid.shift(1))
            else:
                df['macd'] = np.nan
                df['macd_signal'] = np.nan
                df['macd_histogram'] = np.nan
                df['macd_bullish'] = False
                df['macd_bearish'] = False

        except Exception as e:
            self.logger.error(f"Error calculating MACD: {e}")
            df['macd'] = np.nan
            df['macd_signal'] = np.nan
            df['macd_histogram'] = np.nan
            df['macd_bullish'] = False
            df['macd_bearish'] = False

        return df

    def add_rsi(self, df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        """Add RSI indicator"""
        df['rsi'] = ta.rsi(df['close'], length=length)

        # RSI signals
        df['rsi_oversold'] = df['rsi'] < 30
        df['rsi_overbought'] = df['rsi'] > 70
        df['rsi_bullish_divergence'] = self._detect_bullish_divergence(df['close'], df['rsi'])
        df['rsi_bearish_divergence'] = self._detect_bearish_divergence(df['close'], df['rsi'])

        return df

    def add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Stochastic oscillator"""
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch['STOCHk_14_3_3']
        df['stoch_d'] = stoch['STOCHd_14_3_3']

        # Stochastic signals
        df['stoch_oversold'] = (df['stoch_k'] < 20) & (df['stoch_d'] < 20)
        df['stoch_overbought'] = (df['stoch_k'] > 80) & (df['stoch_d'] > 80)

        return df

    def add_williams_r(self, df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        """Add Williams %R"""
        df['williams_r'] = ta.willr(df['high'], df['low'], df['close'], length=length)

        return df

    def add_atr(self, df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        """Add Average True Range"""
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=length)
        df['atr_percent'] = (df['atr'] / df['close']) * 100

        return df

    def add_volatility_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based bands"""
        # Keltner Channels
        kc = ta.kc(df['high'], df['low'], df['close'])
        df['kc_upper'] = kc['KCUe_20_2']
        df['kc_middle'] = kc['KCBe_20_2']
        df['kc_lower'] = kc['KCLe_20_2']

        return df

    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        # Volume Moving Average
        df['volume_sma'] = ta.sma(df['volume'], length=20)

        # On-Balance Volume
        df['obv'] = ta.obv(df['close'], df['volume'])

        # Volume Rate of Change
        df['volume_roc'] = ta.roc(df['volume'], length=10)

        return df

    def add_pivot_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add pivot points for support/resistance"""
        # Standard Pivot Points
        df['pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        df['r1'] = 2 * df['pivot'] - df['low'].shift(1)
        df['s1'] = 2 * df['pivot'] - df['high'].shift(1)
        df['r2'] = df['pivot'] + (df['high'].shift(1) - df['low'].shift(1))
        df['s2'] = df['pivot'] - (df['high'].shift(1) - df['low'].shift(1))

        return df

    def add_fibonacci_levels(self, df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """Add Fibonacci retracement levels"""
        # Calculate rolling high and low
        rolling_high = df['high'].rolling(window=lookback).max()
        rolling_low = df['low'].rolling(window=lookback).min()

        # Fibonacci levels
        fib_range = rolling_high - rolling_low
        df['fib_23.6'] = rolling_high - (fib_range * 0.236)
        df['fib_38.2'] = rolling_high - (fib_range * 0.382)
        df['fib_50.0'] = rolling_high - (fib_range * 0.500)
        df['fib_61.8'] = rolling_high - (fib_range * 0.618)

        return df

    def _detect_bullish_divergence(self, price: pd.Series, indicator: pd.Series, window: int = 5) -> pd.Series:
        """Detect bullish divergence between price and indicator"""
        # Simplified divergence detection
        price_lows = price.rolling(window=window).min() == price
        indicator_lows = indicator.rolling(window=window).min() == indicator

        # Look for higher lows in indicator while price makes lower lows
        divergence = pd.Series(False, index=price.index)

        for i in range(window, len(price)):
            if price_lows.iloc[i] and indicator_lows.iloc[i]:
                # Check previous low
                prev_price_low_idx = price_lows.iloc[:i][::-1].idxmax() if price_lows.iloc[:i].any() else None
                if prev_price_low_idx is not None:
                    if (price.iloc[i] < price.loc[prev_price_low_idx] and
                        indicator.iloc[i] > indicator.loc[prev_price_low_idx]):
                        divergence.iloc[i] = True

        return divergence

    def _detect_bearish_divergence(self, price: pd.Series, indicator: pd.Series, window: int = 5) -> pd.Series:
        """Detect bearish divergence between price and indicator"""
        # Simplified divergence detection
        price_highs = price.rolling(window=window).max() == price
        indicator_highs = indicator.rolling(window=window).max() == indicator

        # Look for lower highs in indicator while price makes higher highs
        divergence = pd.Series(False, index=price.index)

        for i in range(window, len(price)):
            if price_highs.iloc[i] and indicator_highs.iloc[i]:
                # Check previous high
                prev_price_high_idx = price_highs.iloc[:i][::-1].idxmax() if price_highs.iloc[:i].any() else None
                if prev_price_high_idx is not None:
                    if (price.iloc[i] > price.loc[prev_price_high_idx] and
                        indicator.iloc[i] < indicator.loc[prev_price_high_idx]):
                        divergence.iloc[i] = True

        return divergence

    def get_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """Determine market regime (trending vs ranging)"""
        # ADX for trend strength
        adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']

        # Bollinger Band width for volatility
        bb_width = df.get('bb_width', pd.Series(0, index=df.index))

        # Market regime classification
        regime = pd.Series('RANGING', index=df.index)
        regime[adx > 25] = 'TRENDING'
        regime[(adx > 40) & (bb_width > bb_width.rolling(20).mean())] = 'STRONG_TREND'

        return regime
