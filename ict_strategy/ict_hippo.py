"""
ICT HIPPO Module
Implements Hidden Interbank Price Point Objective patterns and Look Back periods
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import calendar
import logging

class HIPPOPatterns:
    """
    HIPPO (Hidden Interbank Price Point Objective) pattern identifier
    Based on ICT's 20-40-60 look back periods and number 9 concepts
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Look back partition calendar (based on multiples of 9)
        self.lookback_calendar = {
            1: {'day': 8, 'number': 18},    # January 8th -> 18
            2: {'day': 7, 'number': 27},    # February 7th -> 27
            3: {'day': 6, 'number': 36},    # March 6th -> 36
            4: {'day': 5, 'number': 45},    # April 5th -> 45
            5: {'day': 4, 'number': 54},    # May 4th -> 54
            6: {'day': 3, 'number': 63},    # June 3rd -> 63
            7: {'day': 2, 'number': 72},    # July 2nd -> 72
            8: {'day': 1, 'number': 81},    # August 1st -> 81
            9: {'day': 9, 'number': 90},    # September 9th -> 90-99
            10: {'day': 8, 'number': 108},  # October 8th -> 108
            11: {'day': 7, 'number': 117},  # November 7th -> 117
            12: {'day': 6, 'number': 126}   # December 6th -> 126
        }

        # Standard look back periods
        self.lookback_periods = [20, 40, 60]

        # HIPPO pattern requirements
        self.hippo_requirements = {
            'min_gap_size': 5,      # Minimum gap size in pips
            'max_gap_ratio': 2.0,   # Maximum ratio between gaps
            'min_body_size': 3,     # Minimum candle body size
            'wick_connection': True  # Must connect wicks
        }

    def get_current_lookback_partition(self, current_date: datetime = None) -> Dict:
        """
        Get current look back partition based on date
        """
        if current_date is None:
            current_date = datetime.now()

        month = current_date.month

        if month in self.lookback_calendar:
            partition_info = self.lookback_calendar[month]

            # Calculate partition start date
            partition_day = partition_info['day']
            partition_start = datetime(current_date.year, month, partition_day)

            # If we haven't reached the partition day yet, use previous month
            if current_date.day < partition_day:
                if month == 1:
                    prev_month = 12
                    year = current_date.year - 1
                else:
                    prev_month = month - 1
                    year = current_date.year

                partition_info = self.lookback_calendar[prev_month]
                partition_start = datetime(year, prev_month, partition_info['day'])

            return {
                'month': month,
                'partition_number': partition_info['number'],
                'partition_start': partition_start,
                'current_date': current_date,
                'days_into_partition': (current_date - partition_start).days
            }

        return {}

    def identify_hippo_patterns(self, data: pd.DataFrame,
                               lookback_periods: int = 60) -> List[Dict]:
        """
        Identify HIPPO patterns in price data
        """
        hippo_patterns = []

        if len(data) < 3:  # Need at least 3 candles
            return hippo_patterns

        # Look for two-bar patterns with gaps
        for i in range(1, len(data) - 1):
            candle1 = data.iloc[i-1]
            candle2 = data.iloc[i]
            candle3 = data.iloc[i+1]

            # Check for HIPPO pattern
            hippo_pattern = self._analyze_hippo_pattern(candle1, candle2, candle3)

            if hippo_pattern['is_hippo']:
                hippo_pattern['timestamp'] = candle2.name
                hippo_pattern['candle_index'] = i
                hippo_patterns.append(hippo_pattern)

        return hippo_patterns

    def _analyze_hippo_pattern(self, candle1: pd.Series, candle2: pd.Series,
                              candle3: pd.Series) -> Dict:
        """
        Analyze three candles for HIPPO pattern
        """
        pattern = {
            'is_hippo': False,
            'pattern_type': None,
            'gap1_size': 0,
            'gap2_size': 0,
            'gap_ratio': 0,
            'hidden_level': None,
            'direction': None
        }

        # Calculate gaps
        gap1 = self._calculate_gap(candle1, candle2)
        gap2 = self._calculate_gap(candle2, candle3)

        if gap1['size'] > 0 and gap2['size'] > 0:
            pattern['gap1_size'] = gap1['size']
            pattern['gap2_size'] = gap2['size']
            pattern['gap_ratio'] = max(gap1['size'], gap2['size']) / min(gap1['size'], gap2['size'])

            # Check HIPPO requirements
            min_gap_size = self.hippo_requirements['min_gap_size']
            max_gap_ratio = self.hippo_requirements['max_gap_ratio']

            if (gap1['size'] >= min_gap_size and
                gap2['size'] >= min_gap_size and
                pattern['gap_ratio'] <= max_gap_ratio):

                pattern['is_hippo'] = True

                # Determine pattern type and hidden level
                if gap1['type'] == 'up' and gap2['type'] == 'up':
                    pattern['pattern_type'] = 'bullish_continuation'
                    pattern['direction'] = 'bullish'
                    pattern['hidden_level'] = self._calculate_hidden_level(candle1, candle2, candle3, 'bullish')

                elif gap1['type'] == 'down' and gap2['type'] == 'down':
                    pattern['pattern_type'] = 'bearish_continuation'
                    pattern['direction'] = 'bearish'
                    pattern['hidden_level'] = self._calculate_hidden_level(candle1, candle2, candle3, 'bearish')

                elif gap1['type'] != gap2['type']:
                    pattern['pattern_type'] = 'reversal'
                    pattern['direction'] = 'reversal'
                    pattern['hidden_level'] = self._calculate_hidden_level(candle1, candle2, candle3, 'reversal')

        return pattern

    def _calculate_gap(self, candle1: pd.Series, candle2: pd.Series) -> Dict:
        """
        Calculate gap between two candles
        """
        gap_info = {'size': 0, 'type': None}

        # Gap up: candle2 low > candle1 high
        if candle2['low'] > candle1['high']:
            gap_info['size'] = candle2['low'] - candle1['high']
            gap_info['type'] = 'up'

        # Gap down: candle2 high < candle1 low
        elif candle2['high'] < candle1['low']:
            gap_info['size'] = candle1['low'] - candle2['high']
            gap_info['type'] = 'down'

        # Convert to pips for forex
        gap_info['size'] *= 10000  # Assuming forex pair

        return gap_info

    def _calculate_hidden_level(self, candle1: pd.Series, candle2: pd.Series,
                               candle3: pd.Series, direction: str) -> float:
        """
        Calculate hidden level by connecting wicks
        """
        if direction == 'bullish':
            # Connect lower wicks
            wick1_low = min(candle1['open'], candle1['close'])
            wick3_low = min(candle3['open'], candle3['close'])
            hidden_level = (wick1_low + wick3_low) / 2

        elif direction == 'bearish':
            # Connect upper wicks
            wick1_high = max(candle1['open'], candle1['close'])
            wick3_high = max(candle3['open'], candle3['close'])
            hidden_level = (wick1_high + wick3_high) / 2

        else:  # reversal
            # Use middle candle extreme
            if candle2['high'] > max(candle1['high'], candle3['high']):
                hidden_level = candle2['high']
            else:
                hidden_level = candle2['low']

        return hidden_level

    def analyze_lookback_clues(self, data: pd.DataFrame,
                              partition_info: Dict) -> List[Dict]:
        """
        Analyze look back clues based on partition number
        """
        clues = []
        partition_number = partition_info.get('partition_number', 27)

        # Look for clues matching partition number
        for idx, (i, row) in enumerate(data.iterrows()):
            # Check for gaps of partition size
            if idx > 0:
                prev_row = data.iloc[idx - 1]
                gap_size = self._calculate_gap(prev_row, row)['size']

                if abs(gap_size - partition_number) < partition_number * 0.1:  # 10% tolerance
                    clues.append({
                        'timestamp': i,
                        'type': 'gap',
                        'size': gap_size,
                        'target_size': partition_number,
                        'match_quality': 1 - abs(gap_size - partition_number) / partition_number
                    })

            # Check for wick sizes
            upper_wick = row['high'] - max(row['open'], row['close'])
            lower_wick = min(row['open'], row['close']) - row['low']

            upper_wick_pips = upper_wick * 10000
            lower_wick_pips = lower_wick * 10000

            if abs(upper_wick_pips - partition_number) < partition_number * 0.1:
                clues.append({
                    'timestamp': i,
                    'type': 'upper_wick',
                    'size': upper_wick_pips,
                    'target_size': partition_number,
                    'match_quality': 1 - abs(upper_wick_pips - partition_number) / partition_number
                })

            if abs(lower_wick_pips - partition_number) < partition_number * 0.1:
                clues.append({
                    'timestamp': i,
                    'type': 'lower_wick',
                    'size': lower_wick_pips,
                    'target_size': partition_number,
                    'match_quality': 1 - abs(lower_wick_pips - partition_number) / partition_number
                })

        # Sort clues by match quality
        clues.sort(key=lambda x: x['match_quality'], reverse=True)

        return clues

    def generate_lookback_trade_plan(self, data: pd.DataFrame,
                                   hippo_patterns: List[Dict],
                                   partition_info: Dict) -> Dict:
        """
        Generate monthly look back trade plan
        """
        trade_plan = {
            'partition_info': partition_info,
            'hippo_patterns': hippo_patterns,
            'trade_setups': [],
            'risk_levels': [],
            'target_levels': []
        }

        partition_number = partition_info.get('partition_number', 27)

        # Generate trade setups based on HIPPO patterns
        for pattern in hippo_patterns:
            if pattern['is_hippo']:
                setup = {
                    'entry_level': pattern['hidden_level'],
                    'direction': pattern['direction'],
                    'stop_loss': None,
                    'take_profit': None,
                    'risk_reward': 2.0  # Default 1:2 RR
                }

                # Calculate stop loss and take profit
                if pattern['direction'] == 'bullish':
                    setup['stop_loss'] = pattern['hidden_level'] - (partition_number / 10000)
                    setup['take_profit'] = pattern['hidden_level'] + (2 * partition_number / 10000)

                elif pattern['direction'] == 'bearish':
                    setup['stop_loss'] = pattern['hidden_level'] + (partition_number / 10000)
                    setup['take_profit'] = pattern['hidden_level'] - (2 * partition_number / 10000)

                trade_plan['trade_setups'].append(setup)

        return trade_plan
