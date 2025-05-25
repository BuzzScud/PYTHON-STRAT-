# ICT Trading Strategy Implementation

This document describes the implementation of ICT (Inner Circle Trader) concepts based on the "DEMYSTIFYING ICT" document, integrating the significance of numbers 3, 6, and 9 in trading.

## Overview

The ICT strategy combines four main components:
1. **Power of Three (PO3)** - Price analysis using powers of 3
2. **Goldbach/IPDA Levels** - Institutional price levels using number 6
3. **AMD Cycles** - Time-based Accumulation, Manipulation, Distribution cycles
4. **HIPPO Patterns** - Hidden Interbank Price Point Objectives using number 9

## Components

### 1. Power of Three (PO3) - `ict_po3.py`

**Purpose**: Calculate dealing ranges using powers of 3 for price partitions.

**Key Features**:
- Automatic optimal PO3 size determination
- Dealing range calculation (3, 9, 27, 81, 243, 729, etc.)
- Stop run identification
- Range expansion/contraction analysis
- Premium/discount zone identification

**Usage**:
```python
from ict_po3 import PowerOfThree

po3 = PowerOfThree()
optimal_size = po3.get_optimal_po3_size(data)
dealing_range = po3.calculate_dealing_range(current_price, optimal_size, 'forex')
```

**Key Methods**:
- `get_optimal_po3_size()`: Determines best PO3 size for current market
- `calculate_dealing_range()`: Creates price boundaries
- `identify_po3_stop_runs()`: Finds PO3-sized stop runs
- `check_range_expansion()`: Determines if range needs expansion

### 2. Goldbach/IPDA Levels - `ict_goldbach.py`

**Purpose**: Calculate institutional price levels based on Goldbach conjecture (number 6).

**Key Features**:
- Standard Goldbach levels: 0/100, 11/89, 17/83, 29/71, 41/59, 50
- Consequent encroachment (50% level) analysis
- External range demarkers
- Institutional level identification
- Algorithm sequence tracking

**Usage**:
```python
from ict_goldbach import GoldbachLevels

goldbach = GoldbachLevels()
levels = goldbach.calculate_goldbach_levels(range_high, range_low)
nearest = goldbach.get_nearest_goldbach_level(current_price, levels)
```

**Key Methods**:
- `calculate_goldbach_levels()`: Generate all institutional levels
- `get_nearest_goldbach_level()`: Find closest significant level
- `identify_consequent_encroachment()`: Track 50% level interactions
- `calculate_institutional_levels()`: Extract key trading levels

### 3. AMD Cycles - `ict_amd_cycles.py`

**Purpose**: Analyze time-based market cycles using 3-6-9 pattern.

**Key Features**:
- Daily AMD cycle identification (9-6-9 hours)
- Session-based analysis (Asian/London/New York)
- Fractal AMD cycles (sub-cycles within main cycles)
- Manipulation phase analysis
- Time distortion detection
- 7-13-21 candle counting

**Usage**:
```python
from ict_amd_cycles import AMDCycles

amd = AMDCycles()
cycle = amd.identify_daily_amd_cycle(data, target_date)
manipulation = amd.analyze_manipulation_phase(manipulation_data)
```

**Key Methods**:
- `identify_daily_amd_cycle()`: Map daily sessions to AMD phases
- `analyze_manipulation_phase()`: Analyze London session characteristics
- `identify_fractal_amd()`: Find sub-cycles within main phases
- `identify_distortion_of_time()`: Detect timing anomalies

### 4. HIPPO Patterns - `ict_hippo.py`

**Purpose**: Identify Hidden Interbank Price Point Objectives using number 9 lookback periods.

**Key Features**:
- Monthly lookback partition calendar
- Two-bar gap pattern identification
- Hidden level calculation (connecting wicks)
- Lookback clue analysis
- Monthly trade plan generation

**Usage**:
```python
from ict_hippo import HIPPOPatterns

hippo = HIPPOPatterns()
partition = hippo.get_current_lookback_partition()
patterns = hippo.identify_hippo_patterns(data)
```

**Key Methods**:
- `get_current_lookback_partition()`: Get current month's number
- `identify_hippo_patterns()`: Find two-bar gap patterns
- `analyze_lookback_clues()`: Find clues matching partition number
- `generate_lookback_trade_plan()`: Create monthly trading plan

## Integrated ICT Strategy - `ict_strategy.py`

The main strategy class that combines all components:

**Key Features**:
- Comprehensive market analysis using all ICT components
- Signal generation with confluence scoring
- Multiple timeframe analysis
- Risk management integration
- Real-time market phase identification

**Usage**:
```python
from ict_strategy import ICTStrategy

config = {
    'trading_style': 'day_trading',
    'asset_type': 'forex',
    'risk_per_trade': 0.02,
    'max_daily_trades': 3
}

strategy = ICTStrategy(config)
analysis = strategy.analyze_market(data)
signals = strategy.generate_signals(data)
```

## Configuration

Add these settings to your `config.py`:

```python
# ICT Strategy Configuration
ICT_TRADING_STYLE = 'day_trading'  # 'scalping', 'day_trading', 'swing_trading', 'position_trading'
ICT_ASSET_TYPE = 'forex'  # 'forex', 'stocks', 'crypto', 'indices'
ICT_PO3_AUTO_SIZE = True  # Automatically determine optimal PO3 size
ICT_DEFAULT_PO3_SIZE = 81  # Default PO3 size if auto-sizing fails
ICT_CONFLUENCE_THRESHOLD = 0.6  # Minimum confluence score for signals
ICT_ENABLE_HIPPO = True  # Enable HIPPO pattern analysis
ICT_ENABLE_AMD = True  # Enable AMD cycle analysis
ICT_ENABLE_GOLDBACH = True  # Enable Goldbach level analysis
ICT_MAX_DAILY_TRADES = 3  # Maximum trades per day
ICT_RISK_PER_TRADE = 0.02  # 2% risk per trade
```

## Trading System Integration

The ICT strategy is integrated into the main trading system:

```python
from trading_system import TradingSystem

# Initialize with ICT strategy
system = TradingSystem(initial_capital=100000, strategy_name="ict")

# Run backtest
results = system.run_backtest(start_date="2023-01-01", end_date="2024-01-01")

# Get current signals
signals = system.get_current_signals()

# Execute live trading
system.execute_live_trading()
```

## Testing

Run the comprehensive test suite:

```bash
python test_ict_strategy.py
```

This will test:
- Individual component functionality
- Integrated strategy analysis
- Signal generation
- Trading system integration

## Key Concepts

### Tesla's 3-6-9 Pattern
- **3**: Power of Three dealing ranges
- **6**: Goldbach levels (6% increments)
- **9**: HIPPO lookback periods and AMD cycles

### Market Structure
- **Price**: PO3 ranges + Goldbach levels
- **Time**: AMD cycles + Lookback periods
- **Integration**: Confluence-based signal generation

### Trading Approach
1. **Analyze** (A phase): Study setup during Asian range
2. **Mark** (M phase): Enter trades during London manipulation
3. **Deliver** (D phase): Manage positions during New York distribution

## Signal Types

The strategy generates several signal types:
- `po3_discount_buy`: Buy in discount zone
- `po3_premium_sell`: Sell in premium zone
- `goldbach_level_reaction`: Reaction at institutional level
- `amd_manipulation_breakout`: Breakout during manipulation phase
- `hippo_pattern`: HIPPO pattern setup

## Risk Management

- Confluence scoring filters weak signals
- Maximum daily trade limits
- Position sizing based on PO3 ranges
- Stop losses at key structural levels
- Take profits at opposite PO3 levels

## Files Structure

```
├── ict_po3.py              # Power of Three implementation
├── ict_goldbach.py         # Goldbach/IPDA levels
├── ict_amd_cycles.py       # AMD cycles analysis
├── ict_hippo.py            # HIPPO patterns
├── ict_strategy.py         # Integrated ICT strategy
├── test_ict_strategy.py    # Comprehensive test suite
└── ICT_STRATEGY_README.md  # This documentation
```

## Next Steps

1. **Backtest** the strategy on historical data
2. **Paper trade** to validate signals in real-time
3. **Optimize** confluence thresholds and parameters
4. **Monitor** performance and adjust as needed
5. **Scale** to multiple instruments and timeframes

The ICT strategy provides a comprehensive framework for institutional-style trading based on mathematical principles and market structure analysis.
