"""
ICT AMD Cycles Module
Implements Accumulation, Manipulation, Distribution cycles based on ICT concepts
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time, timedelta
import logging

class AMDCycles:
    """
    AMD (Accumulation, Manipulation, Distribution) cycles calculator
    Based on ICT's market maker model and session analysis
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Session timings (CET/European time)
        self.session_times = {
            'asian': {
                'start': time(20, 0),   # 20:00 CET (previous day)
                'end': time(5, 0),      # 05:00 CET
                'duration_hours': 9,
                'phase': 'accumulation'
            },
            'london': {
                'start': time(5, 0),    # 05:00 CET
                'end': time(11, 0),     # 11:00 CET
                'duration_hours': 6,
                'phase': 'manipulation'
            },
            'new_york': {
                'start': time(11, 0),   # 11:00 CET
                'end': time(20, 0),     # 20:00 CET
                'duration_hours': 9,
                'phase': 'distribution'
            }
        }

        # AMD cycle structure (3-6-9 pattern)
        self.amd_structure = {
            'accumulation': {'hours': 9, 'phase_number': 1},
            'manipulation': {'hours': 6, 'phase_number': 2},
            'distribution': {'hours': 9, 'phase_number': 3}
        }

        # Fractal AMD levels
        self.fractal_levels = [1, 3, 9]  # Main, sub, micro cycles

    def identify_daily_amd_cycle(self, data: pd.DataFrame,
                                target_date: datetime = None) -> Dict:
        """
        Identify AMD cycle for a specific trading day
        """
        if target_date is None:
            # Handle timezone-aware datetime
            last_timestamp = data.index[-1]
            if hasattr(last_timestamp, 'date'):
                target_date = last_timestamp.date()
            else:
                target_date = last_timestamp.to_pydatetime().date()

        # Filter data for the target date - handle timezone-aware index
        if data.index.tz is not None:
            # Convert to timezone-naive for comparison
            day_data = data[data.index.tz_convert(None).date == target_date]
        else:
            day_data = data[data.index.date == target_date]

        if day_data.empty:
            return {}

        amd_cycle = {
            'date': target_date,
            'accumulation': {'start': None, 'end': None, 'data': pd.DataFrame()},
            'manipulation': {'start': None, 'end': None, 'data': pd.DataFrame()},
            'distribution': {'start': None, 'end': None, 'data': pd.DataFrame()}
        }

        # Simplified session identification using time only (avoid timezone issues)
        for session_name, session_info in self.session_times.items():
            session_start = session_info['start']
            session_end = session_info['end']
            phase = session_info['phase']

            try:
                # Use time-based filtering to avoid timezone comparison issues
                if session_name == 'asian':
                    # Asian session spans midnight (20:00 to 05:00)
                    session_data = day_data[
                        (day_data.index.time >= session_start) |
                        (day_data.index.time <= session_end)
                    ]
                else:
                    # Regular sessions
                    session_data = day_data[
                        (day_data.index.time >= session_start) &
                        (day_data.index.time <= session_end)
                    ]

                if not session_data.empty:
                    amd_cycle[phase]['start'] = session_data.index[0]
                    amd_cycle[phase]['end'] = session_data.index[-1]
                    amd_cycle[phase]['data'] = session_data

            except Exception as e:
                # Fallback: create empty session data
                amd_cycle[phase]['start'] = None
                amd_cycle[phase]['end'] = None
                amd_cycle[phase]['data'] = pd.DataFrame()

        return amd_cycle

    def analyze_manipulation_phase(self, manipulation_data: pd.DataFrame) -> Dict:
        """
        Analyze manipulation phase for key characteristics
        """
        if manipulation_data.empty:
            return {}

        analysis = {
            'session_high': manipulation_data['high'].max(),
            'session_low': manipulation_data['low'].min(),
            'session_range': manipulation_data['high'].max() - manipulation_data['low'].min(),
            'opening_price': manipulation_data['open'].iloc[0],
            'closing_price': manipulation_data['close'].iloc[-1],
            'direction': None,
            'manipulation_type': None,
            'key_levels': []
        }

        # Determine manipulation direction
        if analysis['closing_price'] > analysis['opening_price']:
            analysis['direction'] = 'bullish'
        else:
            analysis['direction'] = 'bearish'

        # Identify manipulation type
        range_size = analysis['session_range']
        price_level = analysis['opening_price']
        range_percentage = (range_size / price_level) * 100

        if range_percentage > 0.5:  # Significant range
            analysis['manipulation_type'] = 'range_expansion'
        else:
            analysis['manipulation_type'] = 'consolidation'

        # Find key manipulation levels (thirds)
        session_low = analysis['session_low']
        session_high = analysis['session_high']

        analysis['key_levels'] = [
            session_low,
            session_low + (range_size * 0.33),  # Lower third
            session_low + (range_size * 0.50),  # Middle
            session_low + (range_size * 0.67),  # Upper third
            session_high
        ]

        return analysis

    def identify_fractal_amd(self, data: pd.DataFrame, main_phase: str,
                           fractal_level: int = 1) -> List[Dict]:
        """
        Identify fractal AMD cycles within main phases
        """
        if data.empty:
            return []

        fractal_cycles = []

        # Divide the main phase into 3 sub-phases
        data_length = len(data)
        third_size = data_length // 3

        phases = ['accumulation', 'manipulation', 'distribution']

        for i, phase_name in enumerate(phases):
            start_idx = i * third_size
            end_idx = (i + 1) * third_size if i < 2 else data_length

            phase_data = data.iloc[start_idx:end_idx]

            if not phase_data.empty:
                fractal_cycle = {
                    'main_phase': main_phase,
                    'fractal_phase': phase_name,
                    'fractal_level': fractal_level,
                    'start_time': phase_data.index[0],
                    'end_time': phase_data.index[-1],
                    'data': phase_data,
                    'phase_high': phase_data['high'].max(),
                    'phase_low': phase_data['low'].min(),
                    'phase_range': phase_data['high'].max() - phase_data['low'].min()
                }

                fractal_cycles.append(fractal_cycle)

        return fractal_cycles

    def calculate_amd_timing(self, start_time: datetime,
                           total_duration_hours: int = 24) -> Dict:
        """
        Calculate AMD timing using 3-6-9 pattern
        """
        # Standard AMD distribution: 9-6-9 hours
        accumulation_hours = 9
        manipulation_hours = 6
        distribution_hours = 9

        timing = {
            'accumulation': {
                'start': start_time,
                'end': start_time + timedelta(hours=accumulation_hours),
                'duration_hours': accumulation_hours
            },
            'manipulation': {
                'start': start_time + timedelta(hours=accumulation_hours),
                'end': start_time + timedelta(hours=accumulation_hours + manipulation_hours),
                'duration_hours': manipulation_hours
            },
            'distribution': {
                'start': start_time + timedelta(hours=accumulation_hours + manipulation_hours),
                'end': start_time + timedelta(hours=total_duration_hours),
                'duration_hours': distribution_hours
            }
        }

        return timing

    def identify_distortion_of_time(self, manipulation_data: pd.DataFrame,
                                  expected_timing: Dict) -> Dict:
        """
        Identify time distortion in manipulation phase
        """
        if manipulation_data.empty:
            return {'distortion_detected': False}

        # Calculate when key events occurred
        session_high_time = manipulation_data.loc[manipulation_data['high'].idxmax()].name
        session_low_time = manipulation_data.loc[manipulation_data['low'].idxmin()].name

        # Expected middle of manipulation phase
        start_time = expected_timing['manipulation']['start']
        end_time = expected_timing['manipulation']['end']
        expected_middle = start_time + (end_time - start_time) / 2

        # Calculate distortion
        middle_tolerance = timedelta(minutes=30)  # 30-minute tolerance

        distortion_analysis = {
            'distortion_detected': False,
            'high_time': session_high_time,
            'low_time': session_low_time,
            'expected_middle': expected_middle,
            'actual_key_time': None,
            'distortion_type': None
        }

        # Determine which extreme is more significant
        range_size = manipulation_data['high'].max() - manipulation_data['low'].min()
        high_move = manipulation_data['high'].max() - manipulation_data['open'].iloc[0]
        low_move = manipulation_data['open'].iloc[0] - manipulation_data['low'].min()

        if high_move > low_move:
            key_time = session_high_time
            distortion_analysis['actual_key_time'] = key_time
        else:
            key_time = session_low_time
            distortion_analysis['actual_key_time'] = key_time

        # Check for distortion
        time_diff = abs(key_time - expected_middle)

        if time_diff > middle_tolerance:
            distortion_analysis['distortion_detected'] = True

            if key_time < expected_middle:
                distortion_analysis['distortion_type'] = 'early'
            else:
                distortion_analysis['distortion_type'] = 'late'

        return distortion_analysis

    def calculate_candle_counting(self, data: pd.DataFrame,
                                amd_cycle: Dict) -> Dict:
        """
        Calculate 7-13-21 candle counting within AMD cycle
        """
        counting_results = {}

        for phase_name in ['accumulation', 'manipulation', 'distribution']:
            if phase_name in amd_cycle and not amd_cycle[phase_name]['data'].empty:
                phase_data = amd_cycle[phase_name]['data']
                candle_count = len(phase_data)

                counting_results[phase_name] = {
                    'candle_count': candle_count,
                    'expected_end_7': min(7, candle_count),
                    'expected_end_13': min(13, candle_count),
                    'expected_end_21': min(21, candle_count)
                }

        return counting_results
