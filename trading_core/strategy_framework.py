"""
Strategy Framework - Base classes and customizable strategy shell
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
from trading_core.technical_indicators import TechnicalIndicators
from trading_core.risk_manager import RiskManager
from config.config import trading_config

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""

    def __init__(self, name: str, risk_manager: RiskManager):
        self.name = name
        self.risk_manager = risk_manager
        self.technical_indicators = TechnicalIndicators()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.signals = []
        self.performance_metrics = {}

    @abstractmethod
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate trading signals based on market data"""
        pass

    @abstractmethod
    def calculate_entry_exit(self, symbol: str, data: pd.DataFrame, signal: Dict) -> Tuple[float, float, Optional[float]]:
        """Calculate entry price, stop loss, and take profit"""
        pass

    def prepare_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Prepare data with technical indicators"""
        prepared_data = {}

        for symbol, df in data.items():
            if df.empty:
                continue

            # Add technical indicators
            df_with_indicators = self.technical_indicators.calculate_all_indicators(df)

            # Add market regime
            df_with_indicators['market_regime'] = self.technical_indicators.get_market_regime(df_with_indicators)

            prepared_data[symbol] = df_with_indicators

        return prepared_data

    def validate_signal(self, signal: Dict) -> bool:
        """Validate if signal meets basic criteria"""
        required_fields = ['symbol', 'direction', 'confidence', 'timestamp']

        for field in required_fields:
            if field not in signal:
                self.logger.warning(f"Signal missing required field: {field}")
                return False

        if signal['direction'] not in ['LONG', 'SHORT']:
            self.logger.warning(f"Invalid signal direction: {signal['direction']}")
            return False

        if not 0 <= signal['confidence'] <= 1:
            self.logger.warning(f"Invalid confidence level: {signal['confidence']}")
            return False

        return True

    def execute_strategy(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Main strategy execution method"""
        # Prepare data with indicators
        prepared_data = self.prepare_data(data)

        # Generate signals
        signals = self.generate_signals(prepared_data)

        # Validate and filter signals
        valid_signals = [signal for signal in signals if self.validate_signal(signal)]

        self.logger.info(f"Generated {len(valid_signals)} valid signals")

        return valid_signals

class CustomStrategy(BaseStrategy):
    """Customizable strategy template - modify this for your specific strategy"""

    def __init__(self, risk_manager: RiskManager, **kwargs):
        super().__init__("CustomStrategy", risk_manager)

        # Strategy parameters - customize these
        self.rsi_oversold = kwargs.get('rsi_oversold', 30)
        self.rsi_overbought = kwargs.get('rsi_overbought', 70)
        self.macd_threshold = kwargs.get('macd_threshold', 0)
        self.bb_threshold = kwargs.get('bb_threshold', 0.1)
        self.min_confidence = kwargs.get('min_confidence', 0.6)
        self.atr_multiplier = kwargs.get('atr_multiplier', 2.0)

    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate trading signals - CUSTOMIZE THIS METHOD"""
        signals = []

        for symbol, df in data.items():
            if len(df) < 50:  # Need enough data for indicators
                continue

            # Get latest data point
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            # LONG SIGNAL CONDITIONS - CUSTOMIZE THESE
            long_conditions = [
                latest['rsi'] < self.rsi_oversold,  # RSI oversold
                latest['macd'] > latest['macd_signal'],  # MACD bullish
                latest['close'] < latest['bb_lower'],  # Below lower Bollinger Band
                latest['ema_20'] > latest['sma_50'],  # Short-term trend up
                latest['market_regime'] in ['TRENDING', 'STRONG_TREND']  # Trending market
            ]

            # SHORT SIGNAL CONDITIONS - CUSTOMIZE THESE
            short_conditions = [
                latest['rsi'] > self.rsi_overbought,  # RSI overbought
                latest['macd'] < latest['macd_signal'],  # MACD bearish
                latest['close'] > latest['bb_upper'],  # Above upper Bollinger Band
                latest['ema_20'] < latest['sma_50'],  # Short-term trend down
                latest['market_regime'] in ['TRENDING', 'STRONG_TREND']  # Trending market
            ]

            # Calculate confidence based on how many conditions are met
            long_confidence = sum(long_conditions) / len(long_conditions)
            short_confidence = sum(short_conditions) / len(short_conditions)

            # Generate LONG signal
            if long_confidence >= self.min_confidence:
                signal = {
                    'symbol': symbol,
                    'direction': 'LONG',
                    'confidence': long_confidence,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'conditions_met': long_conditions,
                    'market_regime': latest['market_regime']
                }
                signals.append(signal)

            # Generate SHORT signal
            elif short_confidence >= self.min_confidence:
                signal = {
                    'symbol': symbol,
                    'direction': 'SHORT',
                    'confidence': short_confidence,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'conditions_met': short_conditions,
                    'market_regime': latest['market_regime']
                }
                signals.append(signal)

        return signals

    def calculate_entry_exit(self, symbol: str, data: pd.DataFrame, signal: Dict) -> Tuple[float, float, Optional[float]]:
        """Calculate entry, stop loss, and take profit levels - CUSTOMIZE THIS"""
        latest = data.iloc[-1]
        direction = signal['direction']

        # Entry price (could be market, limit, etc.)
        entry_price = signal['price']

        # Stop loss based on ATR
        atr = latest['atr']

        if direction == 'LONG':
            stop_loss = entry_price - (atr * self.atr_multiplier)
            take_profit = entry_price + (atr * self.atr_multiplier * 2)  # 2:1 risk/reward
        else:  # SHORT
            stop_loss = entry_price + (atr * self.atr_multiplier)
            take_profit = entry_price - (atr * self.atr_multiplier * 2)  # 2:1 risk/reward

        return entry_price, stop_loss, take_profit

class MomentumStrategy(BaseStrategy):
    """Example momentum-based strategy"""

    def __init__(self, risk_manager: RiskManager):
        super().__init__("MomentumStrategy", risk_manager)

    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate momentum-based signals"""
        signals = []

        for symbol, df in data.items():
            if len(df) < 20:
                continue

            latest = df.iloc[-1]

            # Momentum conditions
            momentum_up = (
                latest['ema_20'] > latest['ema_20'] and
                latest['rsi'] > 50 and
                latest['macd'] > 0 and
                latest['close'] > latest['sma_20']
            )

            momentum_down = (
                latest['ema_20'] < latest['ema_20'] and
                latest['rsi'] < 50 and
                latest['macd'] < 0 and
                latest['close'] < latest['sma_20']
            )

            if momentum_up:
                signals.append({
                    'symbol': symbol,
                    'direction': 'LONG',
                    'confidence': 0.7,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'strategy': 'momentum'
                })
            elif momentum_down:
                signals.append({
                    'symbol': symbol,
                    'direction': 'SHORT',
                    'confidence': 0.7,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'strategy': 'momentum'
                })

        return signals

    def calculate_entry_exit(self, symbol: str, data: pd.DataFrame, signal: Dict) -> Tuple[float, float, Optional[float]]:
        """Calculate entry/exit for momentum strategy"""
        latest = data.iloc[-1]
        atr = latest['atr']
        entry_price = signal['price']

        if signal['direction'] == 'LONG':
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 3.0)
        else:
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 3.0)

        return entry_price, stop_loss, take_profit

class MeanReversionStrategy(BaseStrategy):
    """Example mean reversion strategy"""

    def __init__(self, risk_manager: RiskManager):
        super().__init__("MeanReversionStrategy", risk_manager)

    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate mean reversion signals"""
        signals = []

        for symbol, df in data.items():
            if len(df) < 20:
                continue

            latest = df.iloc[-1]

            # Mean reversion conditions
            oversold = (
                latest['rsi'] < 30 and
                latest['bb_position'] < 0.1 and
                latest['close'] < latest['sma_20'] * 0.98
            )

            overbought = (
                latest['rsi'] > 70 and
                latest['bb_position'] > 0.9 and
                latest['close'] > latest['sma_20'] * 1.02
            )

            if oversold:
                signals.append({
                    'symbol': symbol,
                    'direction': 'LONG',
                    'confidence': 0.6,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'strategy': 'mean_reversion'
                })
            elif overbought:
                signals.append({
                    'symbol': symbol,
                    'direction': 'SHORT',
                    'confidence': 0.6,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'strategy': 'mean_reversion'
                })

        return signals

    def calculate_entry_exit(self, symbol: str, data: pd.DataFrame, signal: Dict) -> Tuple[float, float, Optional[float]]:
        """Calculate entry/exit for mean reversion strategy"""
        latest = data.iloc[-1]
        entry_price = signal['price']

        # Tighter stops for mean reversion
        atr = latest['atr']

        if signal['direction'] == 'LONG':
            stop_loss = entry_price - (atr * 1.0)
            take_profit = latest['sma_20']  # Target mean
        else:
            stop_loss = entry_price + (atr * 1.0)
            take_profit = latest['sma_20']  # Target mean

        return entry_price, stop_loss, take_profit
