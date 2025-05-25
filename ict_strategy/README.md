# ICT Strategy Components

This folder contains the core ICT (Inner Circle Trader) strategy implementation files.

## Files Overview

### Core Strategy Files
- **`ict_strategy.py`** - Main integrated ICT strategy combining all components
- **`standalone_ict_strategy.py`** - Simplified standalone version without full trading system dependency

### ICT Component Modules
- **`ict_po3.py`** - Power of Three (PO3) dealing ranges using powers of 3
- **`ict_goldbach.py`** - Goldbach/IPDA institutional levels using number 6
- **`ict_amd_cycles.py`** - AMD cycles (Accumulation, Manipulation, Distribution) using 3-6-9 pattern
- **`ict_hippo.py`** - HIPPO patterns (Hidden Interbank Price Point Objectives) using number 9

### Demo & Examples
- **`ict_demo.py`** - ICT strategy demonstration script
- **`ict_live_example.py`** - Live trading example implementation

## Quick Usage

```python
from ict_strategy.ict_strategy import ICTStrategy

# Initialize strategy
config = {
    'trading_style': 'day_trading',
    'asset_type': 'forex',
    'risk_per_trade': 0.02
}

strategy = ICTStrategy(config)

# Analyze market
analysis = strategy.analyze_market(data)
signals = strategy.generate_signals(data)
```

## Key Concepts

The ICT strategy integrates four main components based on the significance of numbers 3, 6, and 9:

1. **Power of Three (PO3)** - Price partitions using powers of 3 (3, 9, 27, 81, 243, 729)
2. **Goldbach/IPDA Levels** - Institutional levels using number 6 relationships
3. **AMD Cycles** - Time-based cycles following 3-6-9 pattern (9-6-9 hours daily)
4. **HIPPO Patterns** - Hidden levels using 9-period lookbacks

## Dependencies

These modules depend on:
- `trading_core.strategy_framework` - Base strategy classes
- `trading_core.technical_indicators` - Technical analysis tools
- Standard libraries: pandas, numpy, datetime, logging
