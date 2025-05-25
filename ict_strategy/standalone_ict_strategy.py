"""
Standalone ICT Trading Strategy
A simplified version that doesn't depend on the full trading system
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
import logging

from ict_strategy.ict_po3 import PowerOfThree
from ict_strategy.ict_goldbach import GoldbachLevels
from ict_strategy.ict_amd_cycles import AMDCycles
from ict_strategy.ict_hippo import HIPPOPatterns

class StandaloneICTStrategy:
    """
    Standalone ICT trading strategy combining:
    - Power of Three (PO3) dealing ranges
    - Goldbach/IPDA levels
    - AMD cycles
    - HIPPO patterns
    """
    
    def __init__(self, config: Dict = None):
        if config is None:
            config = {}
            
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
        self.confluence_threshold = config.get('confluence_threshold', 0.6)
        
        self.logger = logging.getLogger(__name__)
    
    def analyze_market(self, data: pd.DataFrame) -> Dict:
        """
        Comprehensive market analysis using all ICT components
        """
        if len(data) < 50:
            self.logger.warning("Insufficient data for ICT analysis")
            return {}
        
        current_price = data['close'].iloc[-1]
        
        try:
            # 1. Power of Three Analysis
            optimal_po3 = self.po3.get_optimal_po3_size(data)
            po3_range = self.po3.calculate_dealing_range(
                current_price, optimal_po3, self.asset_type
            )
            
            # 2. Goldbach Levels Analysis
            goldbach_levels = self.goldbach.calculate_goldbach_levels(
                po3_range['range_high'], po3_range['range_low']
            )
            
            # 3. AMD Cycle Analysis
            amd_cycle = self.amd.identify_daily_amd_cycle(data)
            
            # 4. HIPPO Pattern Analysis
            partition_info = self.hippo.get_current_lookback_partition()
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
                },
                'hippo_analysis': {
                    'partition_info': partition_info,
                    'patterns': hippo_patterns,
                }
            }
            
            return market_analysis
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {e}")
            return {}
    
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
        signals.extend(self._generate_hippo_signals(analysis))
        
        # Filter and rank signals
        filtered_signals = self._filter_signals(signals, analysis)
        
        return filtered_signals
    
    def _generate_po3_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on PO3 analysis"""
        signals = []
        
        po3_analysis = analysis.get('po3_analysis', {})
        price_position = po3_analysis.get('price_position', {})
        
        if price_position.get('zone') == 'discount' and price_position.get('strength', 0) > 0.7:
            signals.append({
                'type': 'po3_discount_buy',
                'direction': 'long',
                'strength': price_position['strength'],
                'entry_price': analysis['current_price'],
                'stop_loss': po3_analysis['dealing_range']['range_low'],
                'take_profit': po3_analysis['dealing_range']['premium_threshold'],
                'reasoning': 'Price in strong discount zone of PO3 range'
            })
        
        elif price_position.get('zone') == 'premium' and price_position.get('strength', 0) > 0.7:
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
        
        if nearest_level and nearest_level.get('distance', float('inf')) < nearest_level.get('price', 1) * 0.001:
            # Price near significant Goldbach level
            if nearest_level.get('level_type') in ['order_block', 'fair_value_gap']:
                signals.append({
                    'type': 'goldbach_level_reaction',
                    'direction': 'long' if nearest_level.get('percentage', 50) < 50 else 'short',
                    'strength': nearest_level.get('weight', 0.5),
                    'entry_price': analysis['current_price'],
                    'level_price': nearest_level.get('price'),
                    'level_type': nearest_level.get('level_type'),
                    'reasoning': f'Price near {nearest_level.get("level_type")} Goldbach level'
                })
        
        return signals
    
    def _generate_hippo_signals(self, analysis: Dict) -> List[Dict]:
        """Generate signals based on HIPPO pattern analysis"""
        signals = []
        
        hippo_analysis = analysis.get('hippo_analysis', {})
        patterns = hippo_analysis.get('patterns', [])
        
        for pattern in patterns:
            if pattern.get('is_hippo') and pattern.get('direction') != 'reversal':
                signals.append({
                    'type': 'hippo_pattern',
                    'direction': 'long' if pattern.get('direction') == 'bullish' else 'short',
                    'strength': 0.7,
                    'entry_price': pattern.get('hidden_level'),
                    'pattern_type': pattern.get('pattern_type'),
                    'reasoning': f'HIPPO {pattern.get("pattern_type")} pattern identified'
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
        signals.sort(key=lambda x: x.get('confluence_score', 0), reverse=True)
        
        # Filter by minimum confluence
        filtered_signals = [s for s in signals if s.get('confluence_score', 0) >= self.confluence_threshold]
        
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
        if nearest_level and nearest_level.get('distance', float('inf')) < nearest_level.get('price', 1) * 0.002:
            score += 0.15
        
        # 3. PO3 zone alignment
        price_position = analysis.get('po3_analysis', {}).get('price_position', {})
        if price_position.get('zone') in ['discount', 'premium']:
            score += 0.1
        
        # 4. HIPPO pattern confluence
        hippo_patterns = analysis.get('hippo_analysis', {}).get('patterns', [])
        if any(p.get('is_hippo', False) for p in hippo_patterns):
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_price_position(self, current_price: float, po3_range: Dict) -> Dict:
        """Analyze current price position within PO3 range"""
        range_low = po3_range['range_low']
        range_high = po3_range['range_high']
        range_size = range_high - range_low
        
        if range_size == 0:
            return {'zone': 'equilibrium', 'position_percentage': 0.5, 'strength': 0}
        
        # Calculate position percentage
        position_pct = (current_price - range_low) / range_size
        
        # Determine zone
        if position_pct <= 0.33:
            zone = 'discount'
            strength = (0.33 - position_pct) / 0.33 if position_pct <= 0.33 else 0
        elif position_pct >= 0.67:
            zone = 'premium'
            strength = (position_pct - 0.67) / 0.33 if position_pct >= 0.67 else 0
        else:
            zone = 'equilibrium'
            strength = 1 - abs(position_pct - 0.5) / 0.17
        
        return {
            'zone': zone,
            'position_percentage': position_pct,
            'strength': max(0, min(1, strength))
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
    
    def get_trading_plan(self, data: pd.DataFrame) -> Dict:
        """
        Generate a comprehensive trading plan
        """
        analysis = self.analyze_market(data)
        signals = self.generate_signals(data)
        
        plan = {
            'timestamp': datetime.now(),
            'market_analysis': analysis,
            'signals': signals,
            'recommendations': self._generate_recommendations(analysis, signals),
            'risk_assessment': self._assess_risk(analysis, signals)
        }
        
        return plan
    
    def _generate_recommendations(self, analysis: Dict, signals: List[Dict]) -> List[str]:
        """Generate trading recommendations"""
        recommendations = []
        
        if not signals:
            recommendations.append("No high-confidence signals found. Wait for better setups.")
        
        for signal in signals:
            rec = f"Consider {signal['direction']} position at {signal.get('entry_price', 'N/A'):.5f}"
            rec += f" (confluence: {signal.get('confluence_score', 0):.2f})"
            recommendations.append(rec)
        
        # Market structure recommendations
        po3_analysis = analysis.get('po3_analysis', {})
        price_position = po3_analysis.get('price_position', {})
        
        if price_position.get('zone') == 'equilibrium':
            recommendations.append("Price in equilibrium zone - wait for clear directional bias")
        
        return recommendations
    
    def _assess_risk(self, analysis: Dict, signals: List[Dict]) -> Dict:
        """Assess current market risk"""
        risk_assessment = {
            'overall_risk': 'medium',
            'factors': []
        }
        
        # Check volatility based on PO3 range
        po3_analysis = analysis.get('po3_analysis', {})
        dealing_range = po3_analysis.get('dealing_range', {})
        
        if dealing_range:
            range_size = dealing_range.get('range_high', 0) - dealing_range.get('range_low', 0)
            current_price = analysis.get('current_price', 1)
            
            if range_size / current_price > 0.01:  # > 1% range
                risk_assessment['factors'].append("High volatility detected")
                risk_assessment['overall_risk'] = 'high'
        
        # Check signal confluence
        if signals:
            avg_confluence = sum(s.get('confluence_score', 0) for s in signals) / len(signals)
            if avg_confluence < 0.7:
                risk_assessment['factors'].append("Low signal confluence")
                risk_assessment['overall_risk'] = 'high'
        
        return risk_assessment
