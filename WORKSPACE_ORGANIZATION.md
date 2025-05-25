# Workspace Organization Guide

This document describes the organized structure of the ICT Trading Strategy workspace.

## 📁 Folder Structure

```
STRAT TEST 1/
├── ict_strategy/           # ICT Strategy Components
├── trading_core/           # Trading System Core Infrastructure  
├── interfaces/             # User Interfaces & Web Apps
├── tests/                  # Testing & Validation Scripts
├── config/                 # Configuration & Setup Files
├── data/                   # Data Files, Logs & Cache
├── docs/                   # Documentation & References
├── utils/                  # Utilities & Helper Scripts
├── requirements.txt        # Python Dependencies
└── WORKSPACE_ORGANIZATION.md  # This file
```

## 📂 Detailed Folder Contents

### 🎯 `ict_strategy/` - ICT Strategy Components
Core ICT (Inner Circle Trader) strategy implementation files:

- `ict_strategy.py` - Main integrated ICT strategy
- `ict_po3.py` - Power of Three (PO3) dealing ranges
- `ict_goldbach.py` - Goldbach/IPDA institutional levels
- `ict_amd_cycles.py` - AMD cycles (Accumulation, Manipulation, Distribution)
- `ict_hippo.py` - HIPPO patterns (Hidden Interbank Price Point Objectives)
- `standalone_ict_strategy.py` - Simplified standalone version
- `ict_demo.py` - ICT strategy demonstration
- `ict_live_example.py` - Live trading example

### ⚙️ `trading_core/` - Trading System Infrastructure
Core trading system components and frameworks:

- `trading_system.py` - Main trading system orchestrator
- `strategy_framework.py` - Base strategy classes and framework
- `backtesting_engine.py` - Backtesting and performance analysis
- `risk_manager.py` - Risk management and position sizing
- `data_manager.py` - Data acquisition and management
- `market_data_api.py` - Market data API interfaces
- `enhanced_market_data.py` - Enhanced data processing
- `technical_indicators.py` - Technical analysis indicators

### 🖥️ `interfaces/` - User Interfaces
Web applications and user interface components:

- `bloomberg_ui.py` - Bloomberg-style Streamlit web interface
- `simple_ui.py` - Simplified web interface
- `ict_analysis_demo.html` - ICT analysis HTML demo

### 🧪 `tests/` - Testing & Validation
Test scripts and validation tools:

- `test_ict_strategy.py` - ICT strategy comprehensive tests
- `test_system.py` - Trading system tests
- `test_imports.py` - Import validation tests
- `test_ict_web_integration.py` - Web integration tests
- `simple_ict_test.py` - Simple ICT functionality tests

### ⚙️ `config/` - Configuration & Setup
Configuration files, setup scripts, and launchers:

- `config.py` - Main configuration settings
- `setup.py` - Package setup configuration
- `unified_launcher.py` - Unified application launcher
- `launch_terminal.py` - Terminal launcher
- `start_bloomberg_ui.sh` - Bloomberg UI startup script
- `run_unified_terminal.bat/.sh` - Terminal runners

### 💾 `data/` - Data & Logs
Data files, logs, and cache:

- `trading_data.db` - SQLite trading database
- `trading_strategy.log` - Strategy execution logs
- `__pycache__/` - Python bytecode cache

### 📚 `docs/` - Documentation
Documentation, references, and guides:

- `README.md` - Main project documentation
- `ICT_STRATEGY_README.md` - ICT strategy detailed guide
- `IMPORT_FIXES_SUMMARY.md` - Import fixes documentation
- `633208806-demystified.pdf/.txt` - ICT reference materials

### 🛠️ `utils/` - Utilities & Tools
Helper scripts and utility tools:

- `demo_market_api.py` - Market API demonstration
- `example_custom_strategy.py` - Custom strategy template
- `fix_imports.py` - Import fixing utility

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Bloomberg-style Interface
```bash
cd config
./start_bloomberg_ui.sh
```

### 3. Test ICT Strategy
```bash
python tests/test_ict_strategy.py
```

### 4. Run Unified Launcher
```bash
python config/unified_launcher.py
```

## 🔧 Import Path Updates

Due to the reorganization, import statements need to be updated. Use relative imports:

```python
# ICT Strategy imports
from ict_strategy.ict_strategy import ICTStrategy
from ict_strategy.ict_po3 import PowerOfThree

# Trading Core imports  
from trading_core.trading_system import TradingSystem
from trading_core.strategy_framework import BaseStrategy

# Configuration imports
from config.config import trading_config
```

## 📋 Benefits of This Organization

1. **Clear Separation of Concerns** - Each folder has a specific purpose
2. **Easier Navigation** - Related files are grouped together
3. **Better Maintainability** - Easier to find and modify specific components
4. **Scalability** - Easy to add new components in appropriate folders
5. **Professional Structure** - Follows Python project best practices

## 🔄 Migration Notes

- All files have been moved to appropriate folders
- Python packages created with `__init__.py` files
- Import paths need updating in existing scripts
- Configuration and launcher scripts moved to `config/`
- All documentation consolidated in `docs/`

## 📞 Support

For questions about the workspace organization or file locations, refer to this guide or check the individual folder README files.
