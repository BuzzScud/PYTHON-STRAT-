"""
Example: How to create and customize your own trading strategy
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from trading_core.strategy_framework import BaseStrategy
from trading_core.risk_manager import RiskManager

class MyPersonalStrategy(BaseStrategy):
    """
    Example of a personalized trading strategy
    
    This strategy combines multiple timeframes and uses:
    - RSI divergence
    - MACD crossovers
    - Bollinger Band squeezes
    - Volume confirmation
    - Market regime filtering
    """
    
    def __init__(self, risk_manager: RiskManager):
        super().__init__("MyPersonalStrategy", risk_manager)
        
        # Customizable parameters
        self.rsi_period = 14
        self.rsi_oversold = 25
        self.rsi_overbought = 75
        
        self.bb_squeeze_threshold = 0.1  # Bollinger Band width threshold
        self.volume_multiplier = 1.5  # Volume above average
        
        self.min_confidence = 0.7  # Minimum signal confidence
        self.atr_stop_multiplier = 2.0
        self.risk_reward_ratio = 2.5
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate trading signals based on custom logic"""
        signals = []
        
        for symbol, df in data.items():
            if len(df) < 50:  # Need sufficient data
                continue
            
            # Get recent data points
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Calculate custom indicators
            signal_strength = self._calculate_signal_strength(df)
            market_condition = self._assess_market_condition(df)
            
            # LONG signal conditions
            long_conditions = self._get_long_conditions(df, latest, prev)
            long_confidence = self._calculate_confidence(long_conditions, signal_strength)
            
            # SHORT signal conditions  
            short_conditions = self._get_short_conditions(df, latest, prev)
            short_confidence = self._calculate_confidence(short_conditions, signal_strength)
            
            # Generate signals based on confidence and market conditions
            if (long_confidence >= self.min_confidence and 
                market_condition in ['BULLISH', 'NEUTRAL']):
                
                signals.append({
                    'symbol': symbol,
                    'direction': 'LONG',
                    'confidence': long_confidence,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'signal_strength': signal_strength,
                    'market_condition': market_condition,
                    'conditions_met': long_conditions
                })
                
            elif (short_confidence >= self.min_confidence and 
                  market_condition in ['BEARISH', 'NEUTRAL']):
                
                signals.append({
                    'symbol': symbol,
                    'direction': 'SHORT',
                    'confidence': short_confidence,
                    'timestamp': latest.name,
                    'price': latest['close'],
                    'signal_strength': signal_strength,
                    'market_condition': market_condition,
                    'conditions_met': short_conditions
                })
        
        return signals
    
    def _get_long_conditions(self, df: pd.DataFrame, latest: pd.Series, prev: pd.Series) -> List[bool]:
        """Define LONG signal conditions"""
        conditions = [
            # RSI conditions
            latest['rsi'] < self.rsi_oversold,  # Oversold
            latest['rsi'] > prev['rsi'],  # RSI rising
            
            # MACD conditions
            latest['macd'] > latest['macd_signal'],  # MACD above signal
            latest['macd_histogram'] > prev['macd_histogram'],  # Histogram increasing
            
            # Bollinger Band conditions
            latest['close'] <= latest['bb_lower'],  # Price at/below lower band
            latest['bb_width'] < self.bb_squeeze_threshold,  # Squeeze condition
            
            # Moving average conditions
            latest['ema_20'] > latest['ema_50'],  # Short-term trend up
            latest['close'] > latest['ema_10'],  # Price above short MA
            
            # Volume confirmation
            self._check_volume_confirmation(df, 'LONG'),
            
            # Momentum confirmation
            latest['close'] > prev['close'],  # Price rising
            
            # Support level
            self._check_support_level(df, latest['close'])
        ]
        
        return conditions
    
    def _get_short_conditions(self, df: pd.DataFrame, latest: pd.Series, prev: pd.Series) -> List[bool]:
        """Define SHORT signal conditions"""
        conditions = [
            # RSI conditions
            latest['rsi'] > self.rsi_overbought,  # Overbought
            latest['rsi'] < prev['rsi'],  # RSI falling
            
            # MACD conditions
            latest['macd'] < latest['macd_signal'],  # MACD below signal
            latest['macd_histogram'] < prev['macd_histogram'],  # Histogram decreasing
            
            # Bollinger Band conditions
            latest['close'] >= latest['bb_upper'],  # Price at/above upper band
            latest['bb_width'] < self.bb_squeeze_threshold,  # Squeeze condition
            
            # Moving average conditions
            latest['ema_20'] < latest['ema_50'],  # Short-term trend down
            latest['close'] < latest['ema_10'],  # Price below short MA
            
            # Volume confirmation
            self._check_volume_confirmation(df, 'SHORT'),
            
            # Momentum confirmation
            latest['close'] < prev['close'],  # Price falling
            
            # Resistance level
            self._check_resistance_level(df, latest['close'])
        ]
        
        return conditions
    
    def _calculate_signal_strength(self, df: pd.DataFrame) -> float:
        """Calculate overall signal strength (0-1)"""
        latest = df.iloc[-1]
        
        # Volatility factor (higher volatility = stronger signals)
        volatility_factor = min(latest['atr_percent'] / 2.0, 1.0)
        
        # Trend strength (ADX-like calculation)
        trend_strength = abs(latest['ema_20'] - latest['sma_50']) / latest['close']
        trend_factor = min(trend_strength * 10, 1.0)
        
        # Volume factor
        volume_factor = 0.5  # Default if no volume data
        if 'volume' in df.columns and not df['volume'].isna().all():
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            current_volume = latest['volume']
            volume_factor = min(current_volume / avg_volume / 2.0, 1.0)
        
        # Combine factors
        signal_strength = (volatility_factor + trend_factor + volume_factor) / 3
        
        return signal_strength
    
    def _assess_market_condition(self, df: pd.DataFrame) -> str:
        """Assess overall market condition"""
        latest = df.iloc[-1]
        
        # Trend assessment
        if latest['ema_20'] > latest['sma_50'] and latest['close'] > latest['sma_200']:
            trend = 'BULLISH'
        elif latest['ema_20'] < latest['sma_50'] and latest['close'] < latest['sma_200']:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        return trend
    
    def _calculate_confidence(self, conditions: List[bool], signal_strength: float) -> float:
        """Calculate signal confidence"""
        # Base confidence from conditions met
        base_confidence = sum(conditions) / len(conditions)
        
        # Adjust by signal strength
        adjusted_confidence = base_confidence * (0.7 + 0.3 * signal_strength)
        
        return min(adjusted_confidence, 1.0)
    
    def _check_volume_confirmation(self, df: pd.DataFrame, direction: str) -> bool:
        """Check volume confirmation"""
        if 'volume' not in df.columns or df['volume'].isna().all():
            return True  # Assume confirmed if no volume data
        
        latest = df.iloc[-1]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        
        return latest['volume'] > avg_volume * self.volume_multiplier
    
    def _check_support_level(self, df: pd.DataFrame, price: float) -> bool:
        """Check if price is near support level"""
        # Simple support check using recent lows
        recent_lows = df['low'].rolling(20).min()
        support_level = recent_lows.iloc[-1]
        
        # Price within 1% of support
        return abs(price - support_level) / price < 0.01
    
    def _check_resistance_level(self, df: pd.DataFrame, price: float) -> bool:
        """Check if price is near resistance level"""
        # Simple resistance check using recent highs
        recent_highs = df['high'].rolling(20).max()
        resistance_level = recent_highs.iloc[-1]
        
        # Price within 1% of resistance
        return abs(price - resistance_level) / price < 0.01
    
    def calculate_entry_exit(self, symbol: str, data: pd.DataFrame, signal: Dict) -> Tuple[float, float, Optional[float]]:
        """Calculate entry, stop loss, and take profit levels"""
        latest = data.iloc[-1]
        direction = signal['direction']
        entry_price = signal['price']
        
        # Use ATR for stop loss calculation
        atr = latest['atr']
        
        if direction == 'LONG':
            # Stop loss below recent support or ATR-based
            support_stop = latest['bb_lower']
            atr_stop = entry_price - (atr * self.atr_stop_multiplier)
            stop_loss = max(support_stop, atr_stop)  # Use the higher (closer) stop
            
            # Take profit based on risk-reward ratio
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * self.risk_reward_ratio)
            
        else:  # SHORT
            # Stop loss above recent resistance or ATR-based
            resistance_stop = latest['bb_upper']
            atr_stop = entry_price + (atr * self.atr_stop_multiplier)
            stop_loss = min(resistance_stop, atr_stop)  # Use the lower (closer) stop
            
            # Take profit based on risk-reward ratio
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * self.risk_reward_ratio)
        
        return entry_price, stop_loss, take_profit

# Example usage
if __name__ == "__main__":
    from trading_core.trading_system import TradingSystem
    from trading_core.risk_manager import RiskManager
    
    # Create custom strategy
    risk_manager = RiskManager(100000)
    custom_strategy = MyPersonalStrategy(risk_manager)
    
    # Initialize trading system with custom strategy
    system = TradingSystem(initial_capital=100000)
    system.strategy = custom_strategy
    
    print("Custom Strategy Example")
    print("="*30)
    
    # Run backtest
    results = system.run_backtest(
        start_date="2023-06-01",
        end_date="2024-01-01"
    )
    
    if results:
        print(f"\nBacktest Results:")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
        print(f"Win Rate: {results.get('win_rate', 0)*100:.1f}%")
    
    print("\nCustom strategy ready for live trading!")
