"""
ICT Goldbach/IPDA Levels Module
Implements Huddleston levels based on Goldbach conjecture for institutional price levels
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

class GoldbachLevels:
    """
    Goldbach/IPDA levels calculator
    Based on ICT's institutional price delivery algorithm using Goldbach conjecture
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard Goldbach levels (percentages)
        self.goldbach_levels = {
            'high_low': [0, 100],           # Extreme boundaries
            'order_block': [11, 89],        # Order block levels
            'fair_value_gap': [17, 83],     # Fair value gap levels  
            'liquidity_void': [29, 71],     # Liquidity void levels
            'breaker': [41, 59],            # Breaker levels
            'equilibrium': [50]             # Consequent encroachment
        }
        
        # Level importance weights
        self.level_weights = {
            'high_low': 1.0,
            'order_block': 0.9,
            'fair_value_gap': 0.8,
            'liquidity_void': 0.7,
            'breaker': 0.6,
            'equilibrium': 0.5
        }
    
    def calculate_goldbach_levels(self, range_high: float, range_low: float) -> Dict[str, Dict]:
        """
        Calculate all Goldbach levels within a given range
        """
        range_size = range_high - range_low
        
        levels = {}
        
        for level_name, percentages in self.goldbach_levels.items():
            levels[level_name] = {}
            
            for pct in percentages:
                price_level = range_low + (range_size * pct / 100)
                levels[level_name][f'{pct}%'] = {
                    'price': price_level,
                    'percentage': pct,
                    'weight': self.level_weights[level_name],
                    'type': level_name
                }
        
        return levels
    
    def get_nearest_goldbach_level(self, current_price: float, goldbach_levels: Dict, 
                                  max_distance: float = None) -> Optional[Dict]:
        """
        Find nearest Goldbach level to current price
        """
        nearest_level = None
        min_distance = float('inf')
        
        for level_type, levels in goldbach_levels.items():
            for pct_key, level_data in levels.items():
                distance = abs(current_price - level_data['price'])
                
                if max_distance is None or distance <= max_distance:
                    if distance < min_distance:
                        min_distance = distance
                        nearest_level = {
                            **level_data,
                            'distance': distance,
                            'level_type': level_type,
                            'percentage_key': pct_key
                        }
        
        return nearest_level
    
    def identify_consequent_encroachment(self, data: pd.DataFrame, 
                                       goldbach_levels: Dict) -> List[Dict]:
        """
        Identify consequent encroachment (50% level) interactions
        """
        ce_interactions = []
        
        if 'equilibrium' not in goldbach_levels:
            return ce_interactions
        
        equilibrium_price = goldbach_levels['equilibrium']['50%']['price']
        
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Check if price crossed equilibrium
            crossed_up = previous['close'] < equilibrium_price < current['close']
            crossed_down = previous['close'] > equilibrium_price > current['close']
            
            if crossed_up or crossed_down:
                ce_interactions.append({
                    'timestamp': current.name,
                    'direction': 'up' if crossed_up else 'down',
                    'equilibrium_price': equilibrium_price,
                    'entry_price': current['close'],
                    'previous_price': previous['close']
                })
        
        return ce_interactions
    
    def calculate_mean_threshold(self, data: pd.DataFrame, window: int = 20) -> float:
        """
        Calculate mean threshold for equilibrium analysis
        """
        if len(data) < window:
            window = len(data)
        
        recent_data = data.tail(window)
        
        # Calculate various means
        price_mean = recent_data['close'].mean()
        high_low_mean = ((recent_data['high'] + recent_data['low']) / 2).mean()
        ohlc_mean = ((recent_data['open'] + recent_data['high'] + 
                     recent_data['low'] + recent_data['close']) / 4).mean()
        
        # Weighted average of different means
        mean_threshold = (price_mean * 0.5 + high_low_mean * 0.3 + ohlc_mean * 0.2)
        
        return mean_threshold
    
    def identify_external_range_demarkers(self, data: pd.DataFrame, 
                                        goldbach_levels: Dict, 
                                        lookback: int = 50) -> List[Dict]:
        """
        Identify external range demarkers (boundaries of institutional interest)
        """
        demarkers = []
        
        if len(data) < lookback:
            lookback = len(data)
        
        recent_data = data.tail(lookback)
        
        # Get high/low levels
        if 'high_low' in goldbach_levels:
            high_level = goldbach_levels['high_low']['100%']['price']
            low_level = goldbach_levels['high_low']['0%']['price']
            
            # Check for interactions with external levels
            for i, row in recent_data.iterrows():
                # Check high level interaction
                if abs(row['high'] - high_level) < (high_level * 0.001):  # 0.1% tolerance
                    demarkers.append({
                        'timestamp': i,
                        'type': 'high_demarker',
                        'price': row['high'],
                        'level_price': high_level,
                        'interaction_type': 'touch'
                    })
                
                # Check low level interaction  
                if abs(row['low'] - low_level) < (low_level * 0.001):  # 0.1% tolerance
                    demarkers.append({
                        'timestamp': i,
                        'type': 'low_demarker', 
                        'price': row['low'],
                        'level_price': low_level,
                        'interaction_type': 'touch'
                    })
        
        return demarkers
    
    def calculate_institutional_levels(self, data: pd.DataFrame, 
                                     po3_range: Dict) -> Dict[str, float]:
        """
        Calculate key institutional levels within PO3 range
        """
        range_high = po3_range['range_high']
        range_low = po3_range['range_low']
        
        # Get Goldbach levels
        goldbach_levels = self.calculate_goldbach_levels(range_high, range_low)
        
        # Extract key institutional levels
        institutional_levels = {}
        
        # Order block levels (11/89)
        if 'order_block' in goldbach_levels:
            institutional_levels['order_block_low'] = goldbach_levels['order_block']['11%']['price']
            institutional_levels['order_block_high'] = goldbach_levels['order_block']['89%']['price']
        
        # Fair value gap levels (17/83)
        if 'fair_value_gap' in goldbach_levels:
            institutional_levels['fvg_low'] = goldbach_levels['fair_value_gap']['17%']['price']
            institutional_levels['fvg_high'] = goldbach_levels['fair_value_gap']['83%']['price']
        
        # Liquidity void levels (29/71)
        if 'liquidity_void' in goldbach_levels:
            institutional_levels['liq_void_low'] = goldbach_levels['liquidity_void']['29%']['price']
            institutional_levels['liq_void_high'] = goldbach_levels['liquidity_void']['71%']['price']
        
        # Breaker levels (41/59)
        if 'breaker' in goldbach_levels:
            institutional_levels['breaker_low'] = goldbach_levels['breaker']['41%']['price']
            institutional_levels['breaker_high'] = goldbach_levels['breaker']['59%']['price']
        
        # Equilibrium (50)
        if 'equilibrium' in goldbach_levels:
            institutional_levels['equilibrium'] = goldbach_levels['equilibrium']['50%']['price']
        
        return institutional_levels
    
    def get_algorithm_sequence(self, algorithm_type: int = 1) -> List[str]:
        """
        Get algorithm sequence for institutional price delivery
        Algorithm 1: 0 -> 11 -> 41 -> 71 -> 89 -> 100
        """
        if algorithm_type == 1:
            return [
                'high_low_0',      # 0% - Start point
                'order_block_11',   # 11% - Order block level
                'breaker_41',       # 41% - Breaker level  
                'liquidity_void_71', # 71% - Liquidity void
                'order_block_89',   # 89% - Order block high
                'high_low_100'      # 100% - End point
            ]
        else:
            # Can add more algorithm types here
            return []
    
    def validate_goldbach_interaction(self, price: float, level: Dict, 
                                    tolerance: float = 0.001) -> bool:
        """
        Validate if price interaction with Goldbach level is significant
        """
        level_price = level['price']
        distance = abs(price - level_price)
        tolerance_amount = level_price * tolerance
        
        return distance <= tolerance_amount
