"""
ICT Trading Strategy
Integrates all ICT components: PO3, Goldbach, AMD, HIPPO
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

from trading_core.strategy_framework import BaseStrategy
from ict_strategy.ict_po3 import PowerOfThree
from ict_strategy.ict_goldbach import GoldbachLevels
from ict_strategy.ict_amd_cycles import AMDCycles
from ict_strategy.ict_hippo import HIPPOPatterns

class ICTStrategy(BaseStrategy):
    """
    Comprehensive ICT trading strategy combining:
    - Power of Three (PO3) dealing ranges
    - Goldbach/IPDA levels
    - AMD cycles
    - HIPPO patterns
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Initialize ICT components
        self.po3 = PowerOfThree()
        self.goldbach = GoldbachLevels()
        self.amd = AMDCycles()
        self.hippo = HIPPOPatterns()
        
        # Strategy configuration
        self.trading_style = config.get('trading_style', 'day_trading')
        self.asset_type = config.get('asset_type', 'forex')
        self.risk_per_trade = config.get('risk_per_trade', 0.02)
        self.max_daily_trades = config.get('max_daily_trades', 3)
        
        # Current market state
        self.current_po3_range = None
        self.current_goldbach_levels = None
        self.current_amd_cycle = None
        self.current_partition = None
        
        self.logger = logging.getLogger(__name__)
    
    def analyze_market(self, data: pd.DataFrame) -> Dict:
        """
        Comprehensive market analysis using all ICT components
        """
        if len(data) < 100:
            self.logger.warning("Insufficient data for ICT analysis")
            return {}
        
        current_price = data['close'].iloc[-1]
        
        # 1. Power of Three Analysis
        optimal_po3 = self.po3.get_optimal_po3_size(data)
        po3_range = self.po3.calculate_dealing_range(
            current_price, optimal_po3, self.asset_type
        )
        self.current_po3_range = po3_range
        
        # 2. Goldbach Levels Analysis
        goldbach_levels = self.goldbach.calculate_goldbach_levels(
            po3_range['range_high'], po3_range['range_low']
        )
        self.current_goldbach_levels = goldbach_levels
        
        # 3. AMD Cycle Analysis
        amd_cycle = self.amd.identify_daily_amd_cycle(data)
        self.current_amd_cycle = amd_cycle
        
        # 4. HIPPO Pattern Analysis
        partition_info = self.hippo.get_current_lookback_partition()
        self.current_partition = partition_info
        
        hippo_patterns = self.hippo.identify_hippo_patterns(data)
        
        # 5. Integration Analysis
        market_analysis = {
            'timestamp': data.index[-1],
            'current_price': current_price,
            'po3_analysis': {
                'optimal_size': optimal_po3,
                'dealing_range': po3_range,
                'price_position': self._analyze_price_position(current_price, po3_range)
            },
            'goldbach_analysis': {
                'levels': goldbach_levels,
                'nearest_level': self.goldbach.get_nearest_goldbach_level(
                    current_price, goldbach_levels
                ),
                'institutional_levels': self.goldbach.calculate_institutional_levels(
                    data, po3_range
                )
            },
            'amd_analysis': {
                'current_cycle': amd_cycle,
                'current_phase': self._identify_current_amd_phase(),
                'manipulation_analysis': self._analyze_current_manipulation(amd_cycle)
            },
            'hippo_analysis': {
                'partition_info': partition_info,
                'patterns': hippo_patterns,
                'lookback_clues': self.hippo.analyze_lookback_clues(data, partition_info)
            }
        }
        
        return market_analysis
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        Generate trading signals based on ICT analysis
        """
        signals = []
        
        # Perform market analysis
        analysis = self.analyze_market(data)
        
        if not analysis:
            return signals
        
        # Signal generation logic
        signals.extend(self._generate_po3_signals(analysis))
        signals.extend(self._generate_goldbach_signals(analysis))
        signals.extend(self._generate_amd_signals(analysis))
        signals.extend(self._generate_hippo_signals(analysis))
        
        # Filter and rank signals
        filtered_signals = self._filter_signals(signals, analysis)
        
        return filtered_signals
    
    def _generate_po3_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on PO3 analysis"""
        signals = []
        
        po3_analysis = analysis.get('po3_analysis', {})
        price_position = po3_analysis.get('price_position', {})
        
        if price_position.get('zone') == 'discount' and price_position.get('strength') > 0.7:
            signals.append({
                'type': 'po3_discount_buy',
                'direction': 'long',
                'strength': price_position['strength'],
                'entry_price': analysis['current_price'],
                'stop_loss': po3_analysis['dealing_range']['range_low'],
                'take_profit': po3_analysis['dealing_range']['premium_threshold'],
                'reasoning': 'Price in strong discount zone of PO3 range'
            })
        
        elif price_position.get('zone') == 'premium' and price_position.get('strength') > 0.7:
            signals.append({
                'type': 'po3_premium_sell',
                'direction': 'short',
                'strength': price_position['strength'],
                'entry_price': analysis['current_price'],
                'stop_loss': po3_analysis['dealing_range']['range_high'],
                'take_profit': po3_analysis['dealing_range']['discount_threshold'],
                'reasoning': 'Price in strong premium zone of PO3 range'
            })
        
        return signals
    
    def _generate_goldbach_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on Goldbach level analysis"""
        signals = []
        
        goldbach_analysis = analysis.get('goldbach_analysis', {})
        nearest_level = goldbach_analysis.get('nearest_level')
        
        if nearest_level and nearest_level['distance'] < nearest_level['price'] * 0.001:
            # Price near significant Goldbach level
            if nearest_level['level_type'] in ['order_block', 'fair_value_gap']:
                signals.append({
                    'type': 'goldbach_level_reaction',
                    'direction': 'long' if nearest_level['percentage'] < 50 else 'short',
                    'strength': nearest_level['weight'],
                    'entry_price': analysis['current_price'],
                    'level_price': nearest_level['price'],
                    'level_type': nearest_level['level_type'],
                    'reasoning': f'Price near {nearest_level["level_type"]} Goldbach level'
                })
        
        return signals
    
    def _generate_amd_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on AMD cycle analysis"""
        signals = []
        
        amd_analysis = analysis.get('amd_analysis', {})
        current_phase = amd_analysis.get('current_phase')
        
        if current_phase == 'manipulation':
            manipulation_analysis = amd_analysis.get('manipulation_analysis', {})
            
            if manipulation_analysis.get('manipulation_type') == 'range_expansion':
                direction = manipulation_analysis.get('direction', 'bullish')
                
                signals.append({
                    'type': 'amd_manipulation_breakout',
                    'direction': 'long' if direction == 'bullish' else 'short',
                    'strength': 0.8,
                    'entry_price': analysis['current_price'],
                    'reasoning': f'AMD manipulation phase showing {direction} range expansion'
                })
        
        return signals
    
    def _generate_hippo_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on HIPPO pattern analysis"""
        signals = []
        
        hippo_analysis = analysis.get('hippo_analysis', {})
        patterns = hippo_analysis.get('patterns', [])
        
        for pattern in patterns:
            if pattern['is_hippo'] and pattern['direction'] != 'reversal':
                signals.append({
                    'type': 'hippo_pattern',
                    'direction': 'long' if pattern['direction'] == 'bullish' else 'short',
                    'strength': 0.7,
                    'entry_price': pattern['hidden_level'],
                    'pattern_type': pattern['pattern_type'],
                    'reasoning': f'HIPPO {pattern["pattern_type"]} pattern identified'
                })
        
        return signals
    
    def _filter_signals(self, signals: List[Dict], analysis: Dict) -> List[Dict]:
        """Filter and rank signals based on confluence"""
        if not signals:
            return signals
        
        # Add confluence scores
        for signal in signals:
            signal['confluence_score'] = self._calculate_confluence(signal, analysis)
        
        # Sort by confluence score
        signals.sort(key=lambda x: x['confluence_score'], reverse=True)
        
        # Filter by minimum confluence
        min_confluence = 0.6
        filtered_signals = [s for s in signals if s['confluence_score'] >= min_confluence]
        
        # Limit number of signals
        return filtered_signals[:self.max_daily_trades]
    
    def _calculate_confluence(self, signal: Dict, analysis: Dict) -> float:
        """Calculate confluence score for signal"""
        score = signal.get('strength', 0.5)
        
        # Add confluence factors
        
        # 1. AMD phase alignment
        amd_phase = analysis.get('amd_analysis', {}).get('current_phase')
        if amd_phase == 'manipulation':
            score += 0.2
        
        # 2. Goldbach level proximity
        nearest_level = analysis.get('goldbach_analysis', {}).get('nearest_level')
        if nearest_level and nearest_level['distance'] < nearest_level['price'] * 0.002:
            score += 0.15
        
        # 3. PO3 zone alignment
        price_position = analysis.get('po3_analysis', {}).get('price_position', {})
        if price_position.get('zone') in ['discount', 'premium']:
            score += 0.1
        
        # 4. HIPPO pattern confluence
        hippo_patterns = analysis.get('hippo_analysis', {}).get('patterns', [])
        if any(p['is_hippo'] for p in hippo_patterns):
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_price_position(self, current_price: float, po3_range: Dict) -> Dict:
        """Analyze current price position within PO3 range"""
        range_low = po3_range['range_low']
        range_high = po3_range['range_high']
        range_size = range_high - range_low
        
        # Calculate position percentage
        position_pct = (current_price - range_low) / range_size
        
        # Determine zone
        if position_pct <= 0.33:
            zone = 'discount'
            strength = (0.33 - position_pct) / 0.33
        elif position_pct >= 0.67:
            zone = 'premium'
            strength = (position_pct - 0.67) / 0.33
        else:
            zone = 'equilibrium'
            strength = 1 - abs(position_pct - 0.5) / 0.17
        
        return {
            'zone': zone,
            'position_percentage': position_pct,
            'strength': strength
        }
    
    def _identify_current_amd_phase(self) -> str:
        """Identify current AMD phase based on time"""
        current_time = datetime.now().time()
        
        # Based on CET times
        if current_time >= self.amd.session_times['asian']['start'] or \
           current_time <= self.amd.session_times['asian']['end']:
            return 'accumulation'
        elif self.amd.session_times['london']['start'] <= current_time <= \
             self.amd.session_times['london']['end']:
            return 'manipulation'
        else:
            return 'distribution'
    
    def _analyze_current_manipulation(self, amd_cycle: Dict) -> Dict:
        """Analyze current manipulation phase"""
        if not amd_cycle or 'manipulation' not in amd_cycle:
            return {}
        
        manipulation_data = amd_cycle['manipulation'].get('data', pd.DataFrame())
        
        if manipulation_data.empty:
            return {}
        
        return self.amd.analyze_manipulation_phase(manipulation_data)
