"""
Test ICT Web Integration
Tests the ICT analysis functionality that would be used in the web interface
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_yfinance_integration():
    """Test yfinance data fetching"""
    logger.info("Testing yfinance integration...")
    
    try:
        import yfinance as yf
        
        # Test fetching EURUSD data
        symbol = "EURUSD=X"
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="30d", interval="4h")
        
        if data.empty:
            logger.error(f"No data received for {symbol}")
            return False
        
        # Convert column names to lowercase
        data.columns = [col.lower() for col in data.columns]
        
        logger.info(f"✅ Successfully fetched {len(data)} data points for {symbol}")
        logger.info(f"   Date range: {data.index[0]} to {data.index[-1]}")
        logger.info(f"   Current price: {data['close'].iloc[-1]:.5f}")
        
        return True, data
        
    except ImportError:
        logger.error("❌ yfinance not available")
        return False, None
    except Exception as e:
        logger.error(f"❌ Error fetching data: {e}")
        return False, None

def test_ict_analysis_with_real_data():
    """Test ICT analysis with real market data"""
    logger.info("Testing ICT analysis with real market data...")
    
    try:
        from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy
        
        # Get real data
        success, data = test_yfinance_integration()
        if not success or data is None:
            logger.error("Cannot proceed without market data")
            return False
        
        # Initialize ICT strategy
        config = {
            'trading_style': 'day_trading',
            'asset_type': 'forex',
            'risk_per_trade': 0.02,
            'max_daily_trades': 3,
            'confluence_threshold': 0.6
        }
        
        strategy = StandaloneICTStrategy(config)
        
        # Perform analysis
        logger.info("Running ICT analysis...")
        analysis = strategy.analyze_market(data)
        
        if not analysis:
            logger.error("❌ ICT analysis failed")
            return False
        
        # Display results
        logger.info("✅ ICT Analysis Results:")
        
        current_price = analysis['current_price']
        logger.info(f"   Current Price: {current_price:.5f}")
        
        # PO3 Analysis
        po3_analysis = analysis.get('po3_analysis', {})
        if po3_analysis:
            dealing_range = po3_analysis.get('dealing_range', {})
            price_position = po3_analysis.get('price_position', {})
            
            logger.info(f"   PO3 Optimal Size: {po3_analysis.get('optimal_size')}")
            logger.info(f"   Dealing Range: {dealing_range.get('range_low', 0):.5f} - {dealing_range.get('range_high', 0):.5f}")
            logger.info(f"   Price Zone: {price_position.get('zone', 'unknown').upper()}")
            logger.info(f"   Zone Strength: {price_position.get('strength', 0):.2f}")
        
        # Goldbach Analysis
        goldbach_analysis = analysis.get('goldbach_analysis', {})
        if goldbach_analysis:
            nearest_level = goldbach_analysis.get('nearest_level')
            if nearest_level:
                distance_pips = nearest_level.get('distance', 0) * 10000
                logger.info(f"   Nearest Goldbach Level: {nearest_level.get('level_type')} at {nearest_level.get('price', 0):.5f}")
                logger.info(f"   Distance: {distance_pips:.1f} pips")
        
        # AMD Analysis
        amd_analysis = analysis.get('amd_analysis', {})
        current_phase = amd_analysis.get('current_phase', 'unknown')
        logger.info(f"   Current AMD Phase: {current_phase.upper()}")
        
        # HIPPO Analysis
        hippo_analysis = analysis.get('hippo_analysis', {})
        partition_info = hippo_analysis.get('partition_info', {})
        patterns = hippo_analysis.get('patterns', [])
        
        logger.info(f"   Lookback Partition: {partition_info.get('partition_number', 'N/A')}")
        logger.info(f"   HIPPO Patterns: {len(patterns)}")
        
        # Generate signals
        logger.info("Generating trading signals...")
        signals = strategy.generate_signals(data)
        
        logger.info(f"✅ Generated {len(signals)} trading signals:")
        for i, signal in enumerate(signals, 1):
            logger.info(f"   Signal {i}: {signal.get('type')} - {signal.get('direction').upper()}")
            logger.info(f"     Entry: {signal.get('entry_price', current_price):.5f}")
            logger.info(f"     Confluence: {signal.get('confluence_score', 0):.2f}")
        
        # Generate trading plan
        trading_plan = strategy.get_trading_plan(data)
        recommendations = trading_plan.get('recommendations', [])
        
        logger.info(f"✅ Trading Plan Generated:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ICT analysis test failed: {e}")
        return False

def test_web_interface_components():
    """Test components that would be used in web interface"""
    logger.info("Testing web interface components...")
    
    try:
        # Test data structure for web display
        success, data = test_yfinance_integration()
        if not success:
            return False
        
        from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy
        
        strategy = StandaloneICTStrategy({
            'trading_style': 'day_trading',
            'asset_type': 'forex',
            'confluence_threshold': 0.6
        })
        
        analysis = strategy.analyze_market(data)
        signals = strategy.generate_signals(data)
        trading_plan = strategy.get_trading_plan(data)
        
        # Test web-friendly data structures
        web_data = {
            'symbol': 'EURUSD=X',
            'current_price': analysis['current_price'],
            'timestamp': analysis['timestamp'],
            'data_points': len(data),
            'analysis_sections': {
                'po3': bool(analysis.get('po3_analysis')),
                'goldbach': bool(analysis.get('goldbach_analysis')),
                'amd': bool(analysis.get('amd_analysis')),
                'hippo': bool(analysis.get('hippo_analysis'))
            },
            'signals_count': len(signals),
            'recommendations_count': len(trading_plan.get('recommendations', [])),
            'risk_level': trading_plan.get('risk_assessment', {}).get('overall_risk', 'medium')
        }
        
        logger.info("✅ Web interface data structure:")
        for key, value in web_data.items():
            logger.info(f"   {key}: {value}")
        
        # Test chart data preparation
        chart_data = {
            'dates': data.index.tolist(),
            'ohlc': {
                'open': data['open'].tolist(),
                'high': data['high'].tolist(),
                'low': data['low'].tolist(),
                'close': data['close'].tolist()
            },
            'levels': {}
        }
        
        # Add PO3 levels for chart
        po3_analysis = analysis.get('po3_analysis', {})
        if po3_analysis:
            dealing_range = po3_analysis.get('dealing_range', {})
            chart_data['levels']['po3'] = {
                'range_high': dealing_range.get('range_high'),
                'range_low': dealing_range.get('range_low'),
                'equilibrium': dealing_range.get('equilibrium')
            }
        
        # Add Goldbach levels for chart
        goldbach_analysis = analysis.get('goldbach_analysis', {})
        if goldbach_analysis:
            institutional_levels = goldbach_analysis.get('institutional_levels', {})
            chart_data['levels']['goldbach'] = institutional_levels
        
        logger.info(f"✅ Chart data prepared: {len(chart_data['dates'])} points, {len(chart_data['levels'])} level groups")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Web interface test failed: {e}")
        return False

def simulate_web_workflow():
    """Simulate the complete web interface workflow"""
    logger.info("Simulating complete web interface workflow...")
    
    try:
        # Step 1: User selects symbol and configuration
        user_config = {
            'symbol': 'EURUSD=X',
            'timeframe': '4h',
            'period': '30d',
            'trading_style': 'day_trading',
            'asset_type': 'forex',
            'confluence_threshold': 0.6,
            'max_trades': 3
        }
        
        logger.info(f"Step 1: User configuration: {user_config}")
        
        # Step 2: Fetch market data
        logger.info("Step 2: Fetching market data...")
        import yfinance as yf
        ticker = yf.Ticker(user_config['symbol'])
        data = ticker.history(period=user_config['period'], interval=user_config['timeframe'])
        data.columns = [col.lower() for col in data.columns]
        
        logger.info(f"   ✅ Data fetched: {len(data)} candles")
        
        # Step 3: Initialize ICT strategy
        logger.info("Step 3: Initializing ICT strategy...")
        from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy
        
        strategy = StandaloneICTStrategy({
            'trading_style': user_config['trading_style'],
            'asset_type': user_config['asset_type'],
            'confluence_threshold': user_config['confluence_threshold'],
            'max_daily_trades': user_config['max_trades']
        })
        
        logger.info("   ✅ ICT strategy initialized")
        
        # Step 4: Perform analysis
        logger.info("Step 4: Performing ICT analysis...")
        analysis = strategy.analyze_market(data)
        signals = strategy.generate_signals(data)
        trading_plan = strategy.get_trading_plan(data)
        
        logger.info("   ✅ Analysis completed")
        
        # Step 5: Prepare results for display
        logger.info("Step 5: Preparing results for web display...")
        
        # Summary metrics
        current_price = analysis['current_price']
        price_change = current_price - data['close'].iloc[-2] if len(data) > 1 else 0
        price_change_pct = (price_change / data['close'].iloc[-2]) * 100 if len(data) > 1 else 0
        
        summary = {
            'current_price': f"{current_price:.5f}",
            'price_change': f"{price_change_pct:+.2f}%",
            'signals_found': len(signals),
            'risk_level': trading_plan.get('risk_assessment', {}).get('overall_risk', 'medium').upper()
        }
        
        logger.info(f"   Summary metrics: {summary}")
        
        # Analysis sections
        po3_analysis = analysis.get('po3_analysis', {})
        if po3_analysis:
            price_position = po3_analysis.get('price_position', {})
            zone = price_position.get('zone', 'unknown').upper()
            strength = price_position.get('strength', 0)
            
            logger.info(f"   PO3: {zone} zone (strength: {strength:.2f})")
        
        # Trading signals
        if signals:
            logger.info(f"   Trading Signals:")
            for i, signal in enumerate(signals, 1):
                logger.info(f"     {i}. {signal.get('type')} - {signal.get('direction').upper()}")
                logger.info(f"        Confluence: {signal.get('confluence_score', 0):.2f}")
        
        # Recommendations
        recommendations = trading_plan.get('recommendations', [])
        if recommendations:
            logger.info(f"   Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"     {i}. {rec}")
        
        logger.info("✅ Complete web workflow simulation successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Web workflow simulation failed: {e}")
        return False

def main():
    """Run all web integration tests"""
    logger.info("🌐 ICT WEB INTEGRATION TESTS")
    logger.info("=" * 60)
    
    tests = [
        ("yFinance Integration", test_yfinance_integration),
        ("ICT Analysis with Real Data", test_ict_analysis_with_real_data),
        ("Web Interface Components", test_web_interface_components),
        ("Complete Web Workflow", simulate_web_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_name == "yFinance Integration":
                result, _ = test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.info(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🎯 WEB INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:30} : {status}")
    
    logger.info("-" * 60)
    logger.info(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 All web integration tests passed!")
        logger.info("The ICT Analysis view is ready for your web application!")
        logger.info("\nTo use in your web app:")
        logger.info("1. Install required packages: streamlit, yfinance, plotly")
        logger.info("2. Run: streamlit run bloomberg_ui.py")
        logger.info("3. Navigate to 'ICT Analysis' in the sidebar")
        logger.info("4. Enter a symbol (e.g., EURUSD=X) and click 'RUN ICT ANALYSIS'")
    else:
        logger.warning("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
