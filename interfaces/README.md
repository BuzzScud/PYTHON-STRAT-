# User Interfaces

This folder contains web applications and user interface components for the trading system.

## Files Overview

### Web Applications
- **`bloomberg_ui.py`** - Bloomberg-style Streamlit web interface with comprehensive trading dashboard
- **`simple_ui.py`** - Simplified web interface for basic trading operations
- **`ict_analysis_demo.html`** - Static HTML demo for ICT analysis visualization

## Bloomberg-Style Interface (`bloomberg_ui.py`)

A comprehensive Streamlit web application featuring:

### Features
- **Dashboard** - Portfolio overview, performance metrics, recent trades
- **Market Data** - Real-time market data display and analysis
- **ICT Analysis** - Interactive ICT strategy analysis and visualization
- **Strategy Editor** - Custom strategy creation and modification
- **Backtesting** - Historical strategy performance testing
- **Risk Management** - Risk controls and position sizing
- **Settings** - System configuration and preferences

### Pages Available
1. Dashboard - Main overview and quick actions
2. Market Data - Symbol analysis and data visualization
3. ICT Analysis - ICT strategy components and signals
4. Strategy Editor - Custom strategy development
5. Backtesting - Performance analysis and optimization
6. Risk Management - Risk controls and monitoring
7. Settings - Configuration and system settings

## Quick Start

### Run Bloomberg Interface
```bash
# From project root
cd config
./start_bloomberg_ui.sh

# Or directly
streamlit run interfaces/bloomberg_ui.py
```

### Run Simple Interface
```bash
streamlit run interfaces/simple_ui.py
```

## Interface Features

### Bloomberg UI Highlights
- Professional Bloomberg-inspired design
- Real-time market data integration
- Interactive ICT strategy analysis
- Comprehensive backtesting tools
- Risk management dashboard
- Strategy performance visualization
- Multi-timeframe analysis
- Symbol search and selection

### Simple UI Features
- Clean, minimal interface
- Basic trading operations
- Essential market data display
- Simplified strategy controls

## Configuration

The interfaces use configuration from `config/config.py`:

```python
# UI Configuration
STREAMLIT_CONFIG = {
    'page_title': 'ICT Trading System',
    'page_icon': '📈',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}
```

## Dependencies

- **streamlit** - Web application framework
- **plotly** - Interactive charts and visualizations
- **pandas** - Data manipulation
- **numpy** - Numerical computations

## Customization

### Adding New Pages
1. Create new page function in `bloomberg_ui.py`
2. Add navigation option in main menu
3. Route to new page in main function

### Styling
- Bloomberg color scheme defined in `BLOOMBERG_COLORS`
- Custom CSS styling for professional appearance
- Responsive design for different screen sizes

## Browser Compatibility

Tested and optimized for:
- Chrome (recommended)
- Firefox
- Safari
- Edge
