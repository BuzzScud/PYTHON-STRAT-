"""
ICT Strategy Demonstration
Shows how to use the ICT trading strategy with real-world examples
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from ict_strategy.standalone_ict_strategy import StandaloneICTStrategy

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_realistic_forex_data(days: int = 60, symbol: str = "EURUSD") -> pd.DataFrame:
    """Create realistic forex data with trends and volatility"""
    
    np.random.seed(42)
    
    # Base prices for different pairs
    base_prices = {
        "EURUSD": 1.0850,
        "GBPUSD": 1.2650,
        "AUDUSD": 0.6750,
        "USDJPY": 149.50
    }
    
    base_price = base_prices.get(symbol, 1.0850)
    
    # Generate dates (4-hour candles)
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         periods=days*6, freq='4h')
    
    # Create trending price movements
    trend_strength = np.random.uniform(-0.0001, 0.0001)  # Daily trend
    volatility = 0.0005  # Base volatility
    
    prices = [base_price]
    
    for i in range(1, len(dates)):
        # Add trend component
        trend_component = trend_strength
        
        # Add random walk
        random_component = np.random.normal(0, volatility)
        
        # Add session-based volatility (higher during London/NY overlap)
        hour = dates[i].hour
        if 13 <= hour <= 17:  # London/NY overlap (UTC)
            session_multiplier = 1.5
        elif 7 <= hour <= 11:  # London session
            session_multiplier = 1.2
        elif 0 <= hour <= 4:   # Asian session
            session_multiplier = 0.8
        else:
            session_multiplier = 1.0
        
        # Calculate new price
        price_change = (trend_component + random_component) * session_multiplier
        new_price = prices[-1] * (1 + price_change)
        prices.append(new_price)
    
    # Create OHLC data
    data = []
    for i in range(len(prices)):
        open_price = prices[i]
        
        # Create realistic intrabar movement
        high_move = np.random.uniform(0, 0.001)
        low_move = np.random.uniform(0, 0.001)
        close_move = np.random.uniform(-0.0005, 0.0005)
        
        high_price = open_price + high_move
        low_price = open_price - low_move
        close_price = open_price + close_move
        
        # Ensure OHLC logic
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
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

def demonstrate_ict_analysis():
    """Demonstrate comprehensive ICT analysis"""
    logger.info("ICT Strategy Demonstration")
    logger.info("=" * 60)
    
    # Create realistic data
    logger.info("Creating realistic EURUSD data...")
    data = create_realistic_forex_data(60, "EURUSD")
    
    # Initialize ICT strategy
    config = {
        'trading_style': 'day_trading',
        'asset_type': 'forex',
        'risk_per_trade': 0.02,
        'max_daily_trades': 3,
        'confluence_threshold': 0.6
    }
    
    strategy = StandaloneICTStrategy(config)
    
    # Perform comprehensive analysis
    logger.info("\nPerforming ICT Market Analysis...")
    logger.info("-" * 40)
    
    analysis = strategy.analyze_market(data)
    
    if analysis:
        current_price = analysis['current_price']
        logger.info(f"Current EURUSD Price: {current_price:.5f}")
        
        # PO3 Analysis
        po3_analysis = analysis.get('po3_analysis', {})
        if po3_analysis:
            dealing_range = po3_analysis['dealing_range']
            price_position = po3_analysis['price_position']
            
            logger.info(f"\n📊 Power of Three Analysis:")
            logger.info(f"  Optimal PO3 Size: {po3_analysis['optimal_size']}")
            logger.info(f"  Dealing Range: {dealing_range['range_low']:.5f} - {dealing_range['range_high']:.5f}")
            logger.info(f"  Equilibrium: {dealing_range['equilibrium']:.5f}")
            logger.info(f"  Price Zone: {price_position['zone'].upper()} (strength: {price_position['strength']:.2f})")
        
        # Goldbach Analysis
        goldbach_analysis = analysis.get('goldbach_analysis', {})
        if goldbach_analysis:
            nearest_level = goldbach_analysis.get('nearest_level')
            institutional_levels = goldbach_analysis.get('institutional_levels', {})
            
            logger.info(f"\n🎯 Goldbach/IPDA Analysis:")
            if nearest_level:
                logger.info(f"  Nearest Level: {nearest_level['level_type']} at {nearest_level['price']:.5f}")
                logger.info(f"  Distance: {nearest_level['distance']:.5f} ({nearest_level['distance']/current_price*10000:.1f} pips)")
            
            logger.info(f"  Key Institutional Levels:")
            for level_name, price in institutional_levels.items():
                logger.info(f"    {level_name}: {price:.5f}")
        
        # AMD Analysis
        amd_analysis = analysis.get('amd_analysis', {})
        if amd_analysis:
            current_phase = amd_analysis.get('current_phase')
            logger.info(f"\n⏰ AMD Cycle Analysis:")
            logger.info(f"  Current Phase: {current_phase.upper()}")
            
            if current_phase == 'manipulation':
                logger.info(f"  🔥 OPTIMAL ENTRY WINDOW - London Manipulation Phase")
            elif current_phase == 'accumulation':
                logger.info(f"  📈 ANALYSIS PHASE - Asian Accumulation")
            else:
                logger.info(f"  📉 MANAGEMENT PHASE - NY Distribution")
        
        # HIPPO Analysis
        hippo_analysis = analysis.get('hippo_analysis', {})
        if hippo_analysis:
            partition_info = hippo_analysis.get('partition_info', {})
            patterns = hippo_analysis.get('patterns', [])
            
            logger.info(f"\n🎪 HIPPO Pattern Analysis:")
            logger.info(f"  Current Lookback Partition: {partition_info.get('partition_number', 'N/A')}")
            logger.info(f"  Days into Partition: {partition_info.get('days_into_partition', 'N/A')}")
            logger.info(f"  HIPPO Patterns Found: {len(patterns)}")
    
    # Generate signals
    logger.info("\nGenerating Trading Signals...")
    logger.info("-" * 40)
    
    signals = strategy.generate_signals(data)
    
    if signals:
        logger.info(f"🚨 {len(signals)} HIGH-CONFIDENCE SIGNALS GENERATED:")
        
        for i, signal in enumerate(signals, 1):
            logger.info(f"\n  Signal #{i}:")
            logger.info(f"    Type: {signal['type']}")
            logger.info(f"    Direction: {signal['direction'].upper()}")
            logger.info(f"    Entry: {signal.get('entry_price', 'N/A'):.5f}")
            logger.info(f"    Confluence Score: {signal.get('confluence_score', 0):.2f}")
            logger.info(f"    Reasoning: {signal.get('reasoning', 'N/A')}")
            
            if 'stop_loss' in signal:
                logger.info(f"    Stop Loss: {signal['stop_loss']:.5f}")
            if 'take_profit' in signal:
                logger.info(f"    Take Profit: {signal['take_profit']:.5f}")
    else:
        logger.info("❌ No high-confidence signals found")
        logger.info("   Wait for better market structure alignment")
    
    # Generate trading plan
    logger.info("\nGenerating Trading Plan...")
    logger.info("-" * 40)
    
    trading_plan = strategy.get_trading_plan(data)
    
    recommendations = trading_plan.get('recommendations', [])
    risk_assessment = trading_plan.get('risk_assessment', {})
    
    logger.info("📋 TRADING RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        logger.info(f"  {i}. {rec}")
    
    logger.info(f"\n⚠️  RISK ASSESSMENT:")
    logger.info(f"  Overall Risk: {risk_assessment.get('overall_risk', 'unknown').upper()}")
    
    risk_factors = risk_assessment.get('factors', [])
    if risk_factors:
        logger.info(f"  Risk Factors:")
        for factor in risk_factors:
            logger.info(f"    - {factor}")
    else:
        logger.info(f"  No significant risk factors identified")
    
    return analysis, signals, trading_plan

def demonstrate_multiple_timeframes():
    """Demonstrate analysis across multiple timeframes"""
    logger.info("\n" + "=" * 60)
    logger.info("MULTIPLE TIMEFRAME ANALYSIS")
    logger.info("=" * 60)
    
    timeframes = {
        'Daily': create_realistic_forex_data(30, "EURUSD"),
        'Weekly': create_realistic_forex_data(7, "EURUSD"),
    }
    
    strategy = StandaloneICTStrategy({
        'trading_style': 'swing_trading',
        'asset_type': 'forex',
        'confluence_threshold': 0.7
    })
    
    for tf_name, tf_data in timeframes.items():
        logger.info(f"\n📊 {tf_name} Timeframe Analysis:")
        logger.info("-" * 30)
        
        analysis = strategy.analyze_market(tf_data)
        signals = strategy.generate_signals(tf_data)
        
        if analysis:
            po3_analysis = analysis.get('po3_analysis', {})
            price_position = po3_analysis.get('price_position', {})
            
            logger.info(f"  Price Zone: {price_position.get('zone', 'N/A').upper()}")
            logger.info(f"  Zone Strength: {price_position.get('strength', 0):.2f}")
            logger.info(f"  Signals: {len(signals)}")

def main():
    """Main demonstration"""
    try:
        # Main analysis
        analysis, signals, plan = demonstrate_ict_analysis()
        
        # Multiple timeframe analysis
        demonstrate_multiple_timeframes()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("DEMONSTRATION SUMMARY")
        logger.info("=" * 60)
        
        logger.info("✅ ICT Strategy Components Successfully Demonstrated:")
        logger.info("   • Power of Three (PO3) dealing ranges")
        logger.info("   • Goldbach/IPDA institutional levels")
        logger.info("   • AMD cycle timing analysis")
        logger.info("   • HIPPO pattern recognition")
        logger.info("   • Confluence-based signal generation")
        logger.info("   • Comprehensive trading plan creation")
        
        logger.info(f"\n📈 Ready for live trading with ICT methodology!")
        logger.info(f"   Configure your preferred settings in the strategy config")
        logger.info(f"   and integrate with your trading system.")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise

if __name__ == "__main__":
    main()
