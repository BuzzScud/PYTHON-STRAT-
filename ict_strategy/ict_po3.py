"""
ICT Power of Three (PO3) Module
Implements Power of Three dealing ranges and calculations based on ICT concepts
"""
import pandas as pd
import numpy as np
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

class PowerOfThree:
    """
    Power of Three (PO3) dealing ranges calculator
    Based on ICT concepts using powers of 3 for price partitions
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard PO3 numbers
        self.po3_numbers = {
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
        
        # Trading style mapping
        self.trading_styles = {
            'scalping': 27,
            'day_trading': 81,
            'swing_trading': 243,
            'position_trading': 729
        }
    
    def calculate_po3_number(self, exponent: int) -> int:
        """Calculate power of three for given exponent"""
        return 3 ** exponent
    
    def get_optimal_po3_size(self, data: pd.DataFrame, lookback_periods: int = 60) -> int:
        """
        Determine optimal PO3 size by analyzing recent price swings
        """
        if len(data) < lookback_periods:
            lookback_periods = len(data)
        
        recent_data = data.tail(lookback_periods)
        
        # Calculate price swings
        highs = recent_data['high'].rolling(window=5).max()
        lows = recent_data['low'].rolling(window=5).min()
        swings = (highs - lows).dropna()
        
        # Convert to pips/points based on asset type
        if 'USD' in str(data.index.name) or any(pair in str(data.index.name) for pair in ['EUR', 'GBP', 'JPY']):
            # Forex - convert to pips
            swings = swings * 10000
        
        avg_swing = swings.mean()
        
        # Find closest PO3 number
        best_po3 = 27  # default
        min_diff = float('inf')
        
        for po3_value in self.po3_numbers.values():
            diff = abs(avg_swing - po3_value)
            if diff < min_diff:
                min_diff = diff
                best_po3 = po3_value
        
        self.logger.info(f"Optimal PO3 size determined: {best_po3} (avg swing: {avg_swing:.1f})")
        return best_po3
    
    def calculate_dealing_range(self, current_price: float, po3_number: int, 
                              asset_type: str = 'forex') -> Dict[str, float]:
        """
        Calculate current PO3 dealing range
        """
        # Prepare price for calculation
        if asset_type == 'forex':
            # Remove decimal point and take first 5 digits
            price_str = f"{current_price:.5f}".replace('.', '')
            base_price = int(price_str[:5])
            decimal_places = 5
        else:
            # For stocks, crypto, indices - use integer part
            base_price = int(current_price)
            decimal_places = 0
        
        # Calculate dealing range low
        range_low_int = (base_price // po3_number) * po3_number
        
        # Calculate dealing range high
        range_high_int = range_low_int + po3_number
        
        # Convert back to proper decimal format
        if asset_type == 'forex':
            range_low = range_low_int / (10 ** (decimal_places - 1))
            range_high = range_high_int / (10 ** (decimal_places - 1))
        else:
            range_low = float(range_low_int)
            range_high = float(range_high_int)
        
        # Calculate additional levels
        equilibrium = (range_low + range_high) / 2
        premium_threshold = range_low + (po3_number * 0.67)
        discount_threshold = range_low + (po3_number * 0.33)
        
        if asset_type == 'forex':
            premium_threshold = premium_threshold / (10 ** (decimal_places - 1))
            discount_threshold = discount_threshold / (10 ** (decimal_places - 1))
        
        return {
            'range_low': range_low,
            'range_high': range_high,
            'equilibrium': equilibrium,
            'premium_threshold': premium_threshold,
            'discount_threshold': discount_threshold,
            'po3_size': po3_number,
            'current_price': current_price
        }
    
    def identify_po3_stop_runs(self, data: pd.DataFrame, po3_number: int, 
                              lookback: int = 20) -> List[Dict]:
        """
        Identify PO3 stop runs in price data
        """
        stop_runs = []
        
        if len(data) < lookback:
            return stop_runs
        
        recent_data = data.tail(lookback)
        
        for i in range(1, len(recent_data)):
            current = recent_data.iloc[i]
            previous = recent_data.iloc[i-1]
            
            # Check for stop run patterns
            high_break = current['high'] > previous['high']
            low_break = current['low'] < previous['low']
            
            # Calculate wick sizes
            upper_wick = current['high'] - max(current['open'], current['close'])
            lower_wick = min(current['open'], current['close']) - current['low']
            
            # Convert to pips for forex
            if 'USD' in str(data.index.name):
                upper_wick *= 10000
                lower_wick *= 10000
            
            # Check if wick size matches PO3 numbers
            po3_values = [9, 27, 81, 243]
            
            for po3_val in po3_values:
                if abs(upper_wick - po3_val) < po3_val * 0.1:  # 10% tolerance
                    stop_runs.append({
                        'timestamp': current.name,
                        'type': 'upper_wick',
                        'size': upper_wick,
                        'po3_size': po3_val,
                        'price_level': current['high']
                    })
                
                if abs(lower_wick - po3_val) < po3_val * 0.1:  # 10% tolerance
                    stop_runs.append({
                        'timestamp': current.name,
                        'type': 'lower_wick',
                        'size': lower_wick,
                        'po3_size': po3_val,
                        'price_level': current['low']
                    })
        
        return stop_runs
    
    def check_range_expansion(self, data: pd.DataFrame, current_range: Dict, 
                            expansion_threshold: float = 0.8) -> bool:
        """
        Check if range expansion is needed
        """
        if len(data) < 10:
            return False
        
        recent_data = data.tail(10)
        
        # Count how many times price moved outside current range
        outside_count = 0
        for _, row in recent_data.iterrows():
            if row['high'] > current_range['range_high'] or row['low'] < current_range['range_low']:
                outside_count += 1
        
        expansion_ratio = outside_count / len(recent_data)
        
        return expansion_ratio > expansion_threshold
    
    def get_next_po3_level(self, current_po3: int, direction: str = 'up') -> int:
        """
        Get next PO3 level for range expansion/contraction
        """
        po3_values = list(self.po3_numbers.values())
        
        try:
            current_index = po3_values.index(current_po3)
            
            if direction == 'up' and current_index < len(po3_values) - 1:
                return po3_values[current_index + 1]
            elif direction == 'down' and current_index > 0:
                return po3_values[current_index - 1]
            else:
                return current_po3
        except ValueError:
            # If current_po3 not in standard list, find closest
            return min(po3_values, key=lambda x: abs(x - current_po3))
