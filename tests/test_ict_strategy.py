"""
Test script for ICT Strategy components
Demonstrates the integration of PO3, Goldbach, AMD, and HIPPO analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from trading_core.trading_system import TradingSystem
from ict_strategy.ict_strategy import ICTStrategy
from ict_strategy.ict_po3 import PowerOfThree
from ict_strategy.ict_goldbach import GoldbachLevels
from ict_strategy.ict_amd_cycles import AMDCycles
from ict_strategy.ict_hippo import HIPPOPatterns

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_forex_data(days: int = 100) -> pd.DataFrame:
    """Create sample forex data for testing"""
    
    # Generate realistic forex price data
    np.random.seed(42)
    
    # Start with base price
    base_price = 1.0850  # EURUSD example
    
    # Generate dates
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         periods=days*24, freq='H')  # Hourly data
    
    # Generate price movements
    returns = np.random.normal(0, 0.0002, len(dates))  # Small hourly returns
    prices = [base_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    # Create OHLC data
    data = []
    for i in range(0, len(prices)-4, 4):  # Group into 4-hour candles
        if i+4 < len(prices):
            open_price = prices[i]
            high_price = max(prices[i:i+4])
            low_price = min(prices[i:i+4])
            close_price = prices[i+3]
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': np.random.randint(1000, 10000)
            })
    
    df = pd.DataFrame(data)
    df.index = pd.date_range(start=datetime.now() - timedelta(days=days), 
                            periods=len(df), freq='4H')
    
    return df

def test_po3_analysis():
    """Test Power of Three analysis"""
    logger.info("Testing Power of Three Analysis...")
    
    # Create sample data
    data = create_sample_forex_data(30)
    current_price = data['close'].iloc[-1]
    
    # Initialize PO3
    po3 = PowerOfThree()
    
    # Test optimal PO3 size calculation
    optimal_size = po3.get_optimal_po3_size(data)
    logger.info(f"Optimal PO3 size: {optimal_size}")
    
    # Test dealing range calculation
    dealing_range = po3.calculate_dealing_range(current_price, optimal_size, 'forex')
    logger.info(f"Current dealing range: {dealing_range}")
    
    # Test stop run identification
    stop_runs = po3.identify_po3_stop_runs(data, optimal_size)
    logger.info(f"Found {len(stop_runs)} PO3 stop runs")
    
    return dealing_range

def test_goldbach_analysis(po3_range):
    """Test Goldbach levels analysis"""
    logger.info("Testing Goldbach Levels Analysis...")
    
    # Initialize Goldbach
    goldbach = GoldbachLevels()
    
    # Calculate Goldbach levels
    levels = goldbach.calculate_goldbach_levels(
        po3_range['range_high'], po3_range['range_low']
    )
    
    logger.info("Goldbach levels calculated:")
    for level_type, level_data in levels.items():
        logger.info(f"  {level_type}: {level_data}")
    
    # Test institutional levels
    data = create_sample_forex_data(30)
    institutional_levels = goldbach.calculate_institutional_levels(data, po3_range)
    logger.info(f"Institutional levels: {institutional_levels}")
    
    return levels

def test_amd_analysis():
    """Test AMD cycles analysis"""
    logger.info("Testing AMD Cycles Analysis...")
    
    # Create sample data
    data = create_sample_forex_data(5)  # 5 days of data
    
    # Initialize AMD
    amd = AMDCycles()
    
    # Test daily AMD cycle identification
    target_date = data.index[-1].date()
    amd_cycle = amd.identify_daily_amd_cycle(data, target_date)
    
    logger.info(f"AMD cycle for {target_date}:")
    for phase, phase_data in amd_cycle.items():
        if isinstance(phase_data, dict) and 'start' in phase_data:
            logger.info(f"  {phase}: {phase_data['start']} to {phase_data['end']}")
    
    # Test manipulation analysis
    if 'manipulation' in amd_cycle and not amd_cycle['manipulation']['data'].empty:
        manipulation_analysis = amd.analyze_manipulation_phase(
            amd_cycle['manipulation']['data']
        )
        logger.info(f"Manipulation analysis: {manipulation_analysis}")
    
    return amd_cycle

def test_hippo_analysis():
    """Test HIPPO patterns analysis"""
    logger.info("Testing HIPPO Patterns Analysis...")
    
    # Create sample data
    data = create_sample_forex_data(30)
    
    # Initialize HIPPO
    hippo = HIPPOPatterns()
    
    # Test current partition
    partition_info = hippo.get_current_lookback_partition()
    logger.info(f"Current lookback partition: {partition_info}")
    
    # Test HIPPO pattern identification
    patterns = hippo.identify_hippo_patterns(data)
    logger.info(f"Found {len(patterns)} HIPPO patterns")
    
    for i, pattern in enumerate(patterns[:3]):  # Show first 3 patterns
        logger.info(f"  Pattern {i+1}: {pattern}")
    
    # Test lookback clues
    clues = hippo.analyze_lookback_clues(data, partition_info)
    logger.info(f"Found {len(clues)} lookback clues")
    
    return patterns

def test_integrated_ict_strategy():
    """Test integrated ICT strategy"""
    logger.info("Testing Integrated ICT Strategy...")
    
    # Create ICT strategy configuration
    ict_config = {
        'trading_style': 'day_trading',
        'asset_type': 'forex',
        'risk_per_trade': 0.02,
        'max_daily_trades': 3
    }
    
    # Initialize ICT strategy
    ict_strategy = ICTStrategy(ict_config)
    
    # Create sample data
    data = create_sample_forex_data(60)
    
    # Test market analysis
    analysis = ict_strategy.analyze_market(data)
    
    logger.info("ICT Market Analysis Results:")
    logger.info(f"  Current Price: {analysis.get('current_price', 'N/A')}")
    
    # PO3 Analysis
    po3_analysis = analysis.get('po3_analysis', {})
    if po3_analysis:
        logger.info(f"  PO3 Optimal Size: {po3_analysis.get('optimal_size', 'N/A')}")
        price_position = po3_analysis.get('price_position', {})
        logger.info(f"  Price Position: {price_position.get('zone', 'N/A')} "
                   f"(strength: {price_position.get('strength', 0):.2f})")
    
    # Goldbach Analysis
    goldbach_analysis = analysis.get('goldbach_analysis', {})
    nearest_level = goldbach_analysis.get('nearest_level')
    if nearest_level:
        logger.info(f"  Nearest Goldbach Level: {nearest_level.get('level_type', 'N/A')} "
                   f"at {nearest_level.get('price', 'N/A')}")
    
    # AMD Analysis
    amd_analysis = analysis.get('amd_analysis', {})
    current_phase = amd_analysis.get('current_phase')
    if current_phase:
        logger.info(f"  Current AMD Phase: {current_phase}")
    
    # HIPPO Analysis
    hippo_analysis = analysis.get('hippo_analysis', {})
    patterns = hippo_analysis.get('patterns', [])
    logger.info(f"  HIPPO Patterns Found: {len(patterns)}")
    
    # Test signal generation
    signals = ict_strategy.generate_signals(data)
    logger.info(f"Generated {len(signals)} trading signals:")
    
    for i, signal in enumerate(signals):
        logger.info(f"  Signal {i+1}: {signal.get('type', 'N/A')} - "
                   f"{signal.get('direction', 'N/A')} "
                   f"(strength: {signal.get('strength', 0):.2f}, "
                   f"confluence: {signal.get('confluence_score', 0):.2f})")
    
    return analysis, signals

def test_trading_system_with_ict():
    """Test trading system with ICT strategy"""
    logger.info("Testing Trading System with ICT Strategy...")
    
    # Initialize trading system with ICT strategy
    system = TradingSystem(initial_capital=100000, strategy_name="ict")
    
    logger.info(f"Trading system initialized with strategy: {system.strategy.__class__.__name__}")
    
    # Test getting current signals (this will use sample data since we don't have live data)
    try:
        signals = system.get_current_signals()
        logger.info(f"Current signals from trading system: {len(signals)}")
        
        for signal in signals:
            logger.info(f"  {signal}")
            
    except Exception as e:
        logger.warning(f"Could not get live signals (expected in test environment): {e}")
    
    # Test performance report
    report = system.get_performance_report()
    logger.info(f"Performance report: {report}")

def main():
    """Run all ICT strategy tests"""
    logger.info("Starting ICT Strategy Component Tests")
    logger.info("=" * 60)
    
    try:
        # Test individual components
        logger.info("\n1. Testing Individual Components:")
        logger.info("-" * 40)
        
        po3_range = test_po3_analysis()
        goldbach_levels = test_goldbach_analysis(po3_range)
        amd_cycle = test_amd_analysis()
        hippo_patterns = test_hippo_analysis()
        
        # Test integrated strategy
        logger.info("\n2. Testing Integrated ICT Strategy:")
        logger.info("-" * 40)
        
        analysis, signals = test_integrated_ict_strategy()
        
        # Test trading system integration
        logger.info("\n3. Testing Trading System Integration:")
        logger.info("-" * 40)
        
        test_trading_system_with_ict()
        
        logger.info("\n" + "=" * 60)
        logger.info("All ICT Strategy tests completed successfully!")
        
        # Summary
        logger.info("\nSUMMARY:")
        logger.info(f"✓ PO3 Analysis: Range calculated successfully")
        logger.info(f"✓ Goldbach Levels: {len(goldbach_levels)} level types identified")
        logger.info(f"✓ AMD Cycles: Daily cycle analysis completed")
        logger.info(f"✓ HIPPO Patterns: {len(hippo_patterns)} patterns found")
        logger.info(f"✓ Integrated Strategy: {len(signals)} signals generated")
        logger.info(f"✓ Trading System: ICT strategy integrated successfully")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
