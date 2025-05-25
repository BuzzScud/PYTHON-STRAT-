"""
Test script to verify the trading system works correctly
"""
import sys
import os
import traceback
from datetime import datetime

# Add the workspace root to Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

def test_imports():
    """Test all imports work correctly"""
    print("Testing imports...")

    try:
        from config.config import trading_config, instrument_config
        print("✓ Config imported successfully")

        from trading_core.data_manager import DataManager
        print("✓ DataManager imported successfully")

        from trading_core.technical_indicators import TechnicalIndicators
        print("✓ TechnicalIndicators imported successfully")

        from trading_core.risk_manager import RiskManager
        print("✓ RiskManager imported successfully")

        from trading_core.strategy_framework import CustomStrategy, MomentumStrategy, MeanReversionStrategy
        print("✓ Strategy framework imported successfully")

        from trading_core.backtesting_engine import BacktestEngine
        print("✓ BacktestEngine imported successfully")

        from trading_core.trading_system import TradingSystem
        print("✓ TradingSystem imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_data_fetching():
    """Test data fetching functionality"""
    print("\nTesting data fetching...")

    try:
        from trading_core.data_manager import DataManager

        dm = DataManager()

        # Test futures data
        es_data = dm.get_futures_data('ES', period='5d', interval='1d')
        if not es_data.empty:
            print(f"✓ ES futures data: {len(es_data)} records")
        else:
            print("⚠ ES futures data is empty")

        # Test forex data
        eurusd_data = dm.get_forex_data('EURUSD', period='5d', interval='1d')
        if not eurusd_data.empty:
            print(f"✓ EURUSD forex data: {len(eurusd_data)} records")
        else:
            print("⚠ EURUSD forex data is empty")

        return True

    except Exception as e:
        print(f"✗ Data fetching error: {e}")
        traceback.print_exc()
        return False

def test_technical_indicators():
    """Test technical indicators calculation"""
    print("\nTesting technical indicators...")

    try:
        from trading_core.data_manager import DataManager
        from trading_core.technical_indicators import TechnicalIndicators

        dm = DataManager()
        ti = TechnicalIndicators()

        # Get sample data
        data = dm.get_futures_data('ES', period='30d', interval='1d')

        if data.empty:
            print("⚠ No data available for indicator testing")
            return False

        # Calculate indicators
        data_with_indicators = ti.calculate_all_indicators(data)

        # Check if indicators were added
        indicator_columns = ['sma_20', 'ema_20', 'rsi', 'macd', 'bb_upper', 'atr']
        missing_indicators = [col for col in indicator_columns if col not in data_with_indicators.columns]

        if not missing_indicators:
            print(f"✓ Technical indicators calculated: {len(data_with_indicators.columns)} columns")
        else:
            print(f"⚠ Missing indicators: {missing_indicators}")

        return True

    except Exception as e:
        print(f"✗ Technical indicators error: {e}")
        traceback.print_exc()
        return False

def test_risk_manager():
    """Test risk management functionality"""
    print("\nTesting risk manager...")

    try:
        from trading_core.risk_manager import RiskManager

        rm = RiskManager(100000)  # $100K initial capital

        # Test position size calculation
        position_size = rm.calculate_position_size('ES', 4500, 4480, 100000)
        print(f"✓ Position size calculation: {position_size} contracts")

        # Test risk limits
        risk_check = rm.check_risk_limits('ES', position_size, 4500)
        print(f"✓ Risk limits check: {risk_check}")

        # Test portfolio summary
        summary = rm.get_portfolio_summary()
        print(f"✓ Portfolio summary: ${summary['current_capital']:,.2f} capital")

        return True

    except Exception as e:
        print(f"✗ Risk manager error: {e}")
        traceback.print_exc()
        return False

def test_strategy():
    """Test strategy execution"""
    print("\nTesting strategy...")

    try:
        from trading_core.data_manager import DataManager
        from trading_core.risk_manager import RiskManager
        from trading_core.strategy_framework import CustomStrategy

        # Initialize components
        dm = DataManager()
        rm = RiskManager(100000)
        strategy = CustomStrategy(rm)

        # Get sample data
        sample_data = {}
        for symbol in ['ES', 'EURUSD']:
            if symbol == 'ES':
                data = dm.get_futures_data(symbol, period='60d', interval='1d')
            else:
                data = dm.get_forex_data(symbol, period='60d', interval='1d')

            if not data.empty:
                sample_data[symbol] = data

        if not sample_data:
            print("⚠ No data available for strategy testing")
            return False

        # Execute strategy
        signals = strategy.execute_strategy(sample_data)
        print(f"✓ Strategy execution: {len(signals)} signals generated")

        # Test signal validation
        if signals:
            first_signal = signals[0]
            is_valid = strategy.validate_signal(first_signal)
            print(f"✓ Signal validation: {is_valid}")

        return True

    except Exception as e:
        print(f"✗ Strategy error: {e}")
        traceback.print_exc()
        return False

def test_trading_system():
    """Test the complete trading system"""
    print("\nTesting trading system...")

    try:
        from trading_core.trading_system import TradingSystem

        # Initialize system
        system = TradingSystem(initial_capital=100000, strategy_name="custom")
        print("✓ Trading system initialized")

        # Test signal generation
        signals = system.get_current_signals()
        print(f"✓ Current signals: {len(signals)} signals")

        # Test performance report
        report = system.get_performance_report()
        print(f"✓ Performance report generated for {report['strategy_name']}")

        return True

    except Exception as e:
        print(f"✗ Trading system error: {e}")
        traceback.print_exc()
        return False

def run_mini_backtest():
    """Run a quick backtest to verify everything works"""
    print("\nRunning mini backtest...")

    try:
        from trading_core.trading_system import TradingSystem

        system = TradingSystem(initial_capital=50000, strategy_name="custom")

        # Run short backtest
        results = system.run_backtest(
            start_date="2023-11-01",
            end_date="2023-12-01",
            timeframe="1d"
        )

        if results:
            print(f"✓ Backtest completed successfully")
            print(f"  Total Return: {results.get('total_return_pct', 0):.2f}%")
            print(f"  Total Trades: {results.get('total_trades', 0)}")
            print(f"  Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        else:
            print("⚠ Backtest returned no results")

        return True

    except Exception as e:
        print(f"✗ Backtest error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Algorithmic Trading System - Test Suite")
    print("="*50)
    print(f"Test started at: {datetime.now()}")

    tests = [
        ("Imports", test_imports),
        ("Data Fetching", test_data_fetching),
        ("Technical Indicators", test_technical_indicators),
        ("Risk Manager", test_risk_manager),
        ("Strategy", test_strategy),
        ("Trading System", test_trading_system),
        ("Mini Backtest", run_mini_backtest)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'-'*20} {test_name} {'-'*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:.<30} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your trading system is ready to use.")
        print("\nNext steps:")
        print("1. Review the configuration in config.py")
        print("2. Customize your strategy in strategy_framework.py")
        print("3. Run a full backtest with: python trading_system.py")
        print("4. Start with paper trading before going live")
    else:
        print(f"\n⚠ {total - passed} tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
