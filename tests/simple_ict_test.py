"""
Simple ICT Strategy Test
Tests individual ICT components without full trading system dependencies
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_forex_data(days: int = 30) -> pd.DataFrame:
    """Create sample forex data for testing"""

    # Generate realistic forex price data
    np.random.seed(42)

    # Start with base price
    base_price = 1.0850  # EURUSD example

    # Generate dates
    dates = pd.date_range(start=datetime.now() - timedelta(days=days),
                         periods=days*6, freq='4H')  # 4-hour data

    # Generate price movements
    returns = np.random.normal(0, 0.0005, len(dates))  # Small returns
    prices = [base_price]

    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)

    # Create OHLC data
    data = []
    for i in range(len(prices)):
        open_price = prices[i]
        # Add some intrabar movement
        high_price = open_price + np.random.uniform(0, 0.002)
        low_price = open_price - np.random.uniform(0, 0.002)
        close_price = open_price + np.random.uniform(-0.001, 0.001)

        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': np.random.randint(1000, 10000)
        })

    df = pd.DataFrame(data)
    df.index = dates[:len(df)]

    return df

def test_po3_component():
    """Test Power of Three component independently"""
    logger.info("Testing Power of Three Component...")

    try:
        from ict_strategy.ict_po3 import PowerOfThree

        # Create sample data
        data = create_sample_forex_data(30)
        current_price = data['close'].iloc[-1]

        # Initialize PO3
        po3 = PowerOfThree()

        # Test optimal PO3 size calculation
        optimal_size = po3.get_optimal_po3_size(data)
        logger.info(f"✓ Optimal PO3 size: {optimal_size}")

        # Test dealing range calculation
        dealing_range = po3.calculate_dealing_range(current_price, optimal_size, 'forex')
        logger.info(f"✓ Current dealing range: {dealing_range}")

        # Test stop run identification
        stop_runs = po3.identify_po3_stop_runs(data, optimal_size)
        logger.info(f"✓ Found {len(stop_runs)} PO3 stop runs")

        return True, dealing_range

    except Exception as e:
        logger.error(f"✗ PO3 test failed: {e}")
        return False, None

def test_goldbach_component(po3_range):
    """Test Goldbach levels component independently"""
    logger.info("Testing Goldbach Levels Component...")

    try:
        from ict_strategy.ict_goldbach import GoldbachLevels

        # Initialize Goldbach
        goldbach = GoldbachLevels()

        # Calculate Goldbach levels
        levels = goldbach.calculate_goldbach_levels(
            po3_range['range_high'], po3_range['range_low']
        )

        logger.info(f"✓ Goldbach levels calculated: {len(levels)} level types")

        # Test nearest level calculation
        current_price = (po3_range['range_high'] + po3_range['range_low']) / 2
        nearest_level = goldbach.get_nearest_goldbach_level(current_price, levels)

        if nearest_level:
            logger.info(f"✓ Nearest level: {nearest_level['level_type']} at {nearest_level['price']:.5f}")

        return True, levels

    except Exception as e:
        logger.error(f"✗ Goldbach test failed: {e}")
        return False, None

def test_amd_component():
    """Test AMD cycles component independently"""
    logger.info("Testing AMD Cycles Component...")

    try:
        from ict_strategy.ict_amd_cycles import AMDCycles

        # Create sample data
        data = create_sample_forex_data(5)  # 5 days of data

        # Initialize AMD
        amd = AMDCycles()

        # Test daily AMD cycle identification
        target_date = data.index[-1].date()
        amd_cycle = amd.identify_daily_amd_cycle(data, target_date)

        logger.info(f"✓ AMD cycle identified for {target_date}")

        # Test timing calculation
        start_time = datetime.now()
        timing = amd.calculate_amd_timing(start_time)
        logger.info(f"✓ AMD timing calculated: {len(timing)} phases")

        return True, amd_cycle

    except Exception as e:
        logger.error(f"✗ AMD test failed: {e}")
        return False, None

def test_hippo_component():
    """Test HIPPO patterns component independently"""
    logger.info("Testing HIPPO Patterns Component...")

    try:
        from ict_strategy.ict_hippo import HIPPOPatterns

        # Create sample data
        data = create_sample_forex_data(30)

        # Initialize HIPPO
        hippo = HIPPOPatterns()

        # Test current partition
        partition_info = hippo.get_current_lookback_partition()
        logger.info(f"✓ Current lookback partition: {partition_info.get('partition_number', 'N/A')}")

        # Test HIPPO pattern identification
        patterns = hippo.identify_hippo_patterns(data)
        logger.info(f"✓ Found {len(patterns)} HIPPO patterns")

        # Test lookback clues
        clues = hippo.analyze_lookback_clues(data, partition_info)
        logger.info(f"✓ Found {len(clues)} lookback clues")

        return True, patterns

    except Exception as e:
        logger.error(f"✗ HIPPO test failed: {e}")
        return False, None

def test_integrated_strategy():
    """Test integrated ICT strategy"""
    logger.info("Testing Integrated ICT Strategy...")

    try:
        from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy

        # Create ICT strategy configuration
        ict_config = {
            'trading_style': 'day_trading',
            'asset_type': 'forex',
            'risk_per_trade': 0.02,
            'max_daily_trades': 3
        }

        # Initialize ICT strategy
        ict_strategy = StandaloneICTStrategy(ict_config)

        # Create sample data
        data = create_sample_forex_data(60)

        # Test market analysis
        analysis = ict_strategy.analyze_market(data)

        logger.info(f"✓ Market analysis completed")
        logger.info(f"  Current Price: {analysis.get('current_price', 'N/A'):.5f}")

        # Test signal generation
        signals = ict_strategy.generate_signals(data)
        logger.info(f"✓ Generated {len(signals)} trading signals")

        for i, signal in enumerate(signals[:3]):  # Show first 3 signals
            logger.info(f"  Signal {i+1}: {signal.get('type', 'N/A')} - "
                       f"{signal.get('direction', 'N/A')} "
                       f"(confluence: {signal.get('confluence_score', 0):.2f})")

        # Test trading plan generation
        trading_plan = ict_strategy.get_trading_plan(data)
        logger.info(f"✓ Trading plan generated with {len(trading_plan.get('recommendations', []))} recommendations")

        return True, len(signals)

    except Exception as e:
        logger.error(f"✗ Integrated strategy test failed: {e}")
        return False, 0

def main():
    """Run all ICT component tests"""
    logger.info("Starting ICT Strategy Component Tests")
    logger.info("=" * 60)

    results = {
        'po3': False,
        'goldbach': False,
        'amd': False,
        'hippo': False,
        'integrated': False
    }

    # Test PO3 component
    logger.info("\n1. Power of Three (PO3) Component:")
    logger.info("-" * 40)
    results['po3'], po3_range = test_po3_component()

    # Test Goldbach component (needs PO3 range)
    if results['po3'] and po3_range:
        logger.info("\n2. Goldbach Levels Component:")
        logger.info("-" * 40)
        results['goldbach'], goldbach_levels = test_goldbach_component(po3_range)

    # Test AMD component
    logger.info("\n3. AMD Cycles Component:")
    logger.info("-" * 40)
    results['amd'], amd_cycle = test_amd_component()

    # Test HIPPO component
    logger.info("\n4. HIPPO Patterns Component:")
    logger.info("-" * 40)
    results['hippo'], hippo_patterns = test_hippo_component()

    # Test integrated strategy
    logger.info("\n5. Integrated ICT Strategy:")
    logger.info("-" * 40)
    results['integrated'], signal_count = test_integrated_strategy()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY:")
    logger.info("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for component, passed_test in results.items():
        status = "✓ PASSED" if passed_test else "✗ FAILED"
        logger.info(f"{component.upper():12} : {status}")

    logger.info("-" * 60)
    logger.info(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        logger.info("🎉 All ICT components are working correctly!")
        logger.info("\nYou can now use the ICT strategy in your trading system:")
        logger.info("  system = TradingSystem(strategy_name='ict')")
    else:
        logger.warning("⚠️  Some components failed. Check the error messages above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
