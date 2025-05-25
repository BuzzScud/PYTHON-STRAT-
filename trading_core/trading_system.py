"""
Main Trading System - Orchestrates all components
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Optional imports
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

from trading_core.data_manager import DataManager
from trading_core.risk_manager import RiskManager
from trading_core.strategy_framework import CustomStrategy, MomentumStrategy, MeanReversionStrategy
from trading_core.backtesting_engine import BacktestEngine
from config.config import trading_config
from ict_strategy.ict_strategy import ICTStrategy

class TradingSystem:
    """Main trading system orchestrator"""

    def __init__(self, initial_capital: float = 100000, strategy_name: str = "custom"):
        self.initial_capital = initial_capital
        self.setup_logging()

        # Initialize components
        self.data_manager = DataManager()
        self.risk_manager = RiskManager(initial_capital)
        self.backtest_engine = BacktestEngine(initial_capital)

        # Initialize strategy
        self.strategy = self._initialize_strategy(strategy_name)

        self.logger.info(f"Trading system initialized with {strategy_name} strategy")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, trading_config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(trading_config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_strategy(self, strategy_name: str):
        """Initialize the selected strategy"""
        strategies = {
            'custom': CustomStrategy,
            'momentum': MomentumStrategy,
            'mean_reversion': MeanReversionStrategy,
            'ict': ICTStrategy
        }

        if strategy_name not in strategies:
            self.logger.warning(f"Unknown strategy: {strategy_name}, using custom")
            strategy_name = 'custom'

        # ICT strategy needs special configuration
        if strategy_name == 'ict':
            ict_config = {
                'trading_style': trading_config.get('ICT_TRADING_STYLE', 'day_trading'),
                'asset_type': trading_config.get('ICT_ASSET_TYPE', 'forex'),
                'risk_per_trade': trading_config.get('RISK_PER_TRADE', 0.02),
                'max_daily_trades': trading_config.get('MAX_DAILY_TRADES', 3)
            }
            return strategies[strategy_name](ict_config)
        else:
            return strategies[strategy_name](self.risk_manager)

    def run_backtest(self, start_date: str = "2023-01-01", end_date: str = "2024-01-01",
                    timeframe: str = "1d") -> Dict:
        """Run backtest on historical data"""
        self.logger.info(f"Running backtest from {start_date} to {end_date}")

        results = self.backtest_engine.run_backtest(
            self.strategy, start_date, end_date, timeframe
        )

        # Plot results
        if results:
            self.backtest_engine.plot_results(results, self.strategy.name)

        return results

    def get_current_signals(self) -> List[Dict]:
        """Get current trading signals"""
        try:
            # Update data
            daily_data, hourly_data = self.data_manager.update_data()

            # Use appropriate timeframe
            if trading_config.PRIMARY_TIMEFRAME == '1d':
                current_data = daily_data
            else:
                current_data = hourly_data

            # Generate signals
            signals = self.strategy.execute_strategy(current_data)

            return signals

        except Exception as e:
            self.logger.error(f"Error getting current signals: {e}")
            return []

    def execute_live_trading(self):
        """Execute live trading (paper trading mode)"""
        if not trading_config.PAPER_TRADING:
            self.logger.warning("Live trading not enabled. Set PAPER_TRADING=False in config")
            return

        self.logger.info("Starting live trading session")

        # Get current signals
        signals = self.get_current_signals()

        if not signals:
            self.logger.info("No signals generated")
            return

        # Process each signal
        for signal in signals:
            self._process_signal(signal)

        # Update portfolio status
        self._log_portfolio_status()

    def _process_signal(self, signal: Dict):
        """Process a trading signal"""
        symbol = signal['symbol']

        # Get current data for the symbol
        if symbol in trading_config.FUTURES_SYMBOLS:
            data = self.data_manager.get_futures_data(symbol, period="60d", interval="1d")
        else:
            data = self.data_manager.get_forex_data(symbol, period="60d", interval="1d")

        if data.empty:
            self.logger.warning(f"No data available for {symbol}")
            return

        # Prepare data with indicators
        prepared_data = {symbol: self.strategy.prepare_data({symbol: data})[symbol]}

        # Calculate entry, stop loss, take profit
        entry_price, stop_loss, take_profit = self.strategy.calculate_entry_exit(
            symbol, prepared_data[symbol], signal
        )

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            symbol, entry_price, stop_loss, self.risk_manager.current_capital
        )

        # Try to add position
        if self.risk_manager.add_position(
            symbol, position_size, entry_price, stop_loss,
            take_profit, signal['direction']
        ):
            self.logger.info(f"Signal executed: {symbol} {signal['direction']} @ {entry_price}")
        else:
            self.logger.warning(f"Signal rejected: {symbol} {signal['direction']}")

    def _log_portfolio_status(self):
        """Log current portfolio status"""
        summary = self.risk_manager.get_portfolio_summary()

        self.logger.info("Portfolio Status:")
        self.logger.info(f"  Current Capital: ${summary['current_capital']:,.2f}")
        self.logger.info(f"  Unrealized P&L: ${summary['unrealized_pnl']:,.2f}")
        self.logger.info(f"  Total Equity: ${summary['total_equity']:,.2f}")
        self.logger.info(f"  Open Positions: {summary['positions_count']}")
        self.logger.info(f"  Current Drawdown: ${summary['current_drawdown']:,.2f}")

    def schedule_trading(self):
        """Schedule automated trading"""
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Schedule module not available. Install with: pip install schedule")
            return

        # Schedule daily analysis
        schedule.every().day.at("09:00").do(self.execute_live_trading)

        # Schedule 4-hour analysis (if using 4h timeframe)
        if trading_config.SECONDARY_TIMEFRAME == '4h':
            schedule.every(4).hours.do(self.execute_live_trading)

        self.logger.info("Trading schedule configured")

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_performance_report(self) -> Dict:
        """Get current performance report"""
        portfolio_summary = self.risk_manager.get_portfolio_summary()
        performance_metrics = self.risk_manager.get_performance_metrics()

        return {
            'portfolio_summary': portfolio_summary,
            'performance_metrics': performance_metrics,
            'strategy_name': self.strategy.name,
            'timestamp': datetime.now()
        }

    def export_trades(self, filename: str = None) -> str:
        """Export trade history to CSV"""
        if not filename:
            filename = f"trades_{self.strategy.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if self.risk_manager.trade_history:
            trades_df = pd.DataFrame(self.risk_manager.trade_history)
            trades_df.to_csv(filename, index=False)
            self.logger.info(f"Trades exported to {filename}")
        else:
            self.logger.info("No trades to export")

        return filename

def main():
    """Example usage of the trading system"""
    print("Algorithmic Trading Strategy System")
    print("="*50)

    # Initialize trading system
    system = TradingSystem(initial_capital=100000, strategy_name="custom")

    # Run backtest
    print("\n1. Running Backtest...")
    backtest_results = system.run_backtest(
        start_date="2023-01-01",
        end_date="2024-01-01",
        timeframe="1d"
    )

    # Get current signals
    print("\n2. Getting Current Signals...")
    current_signals = system.get_current_signals()

    if current_signals:
        print(f"Found {len(current_signals)} signals:")
        for signal in current_signals:
            print(f"  {signal['symbol']}: {signal['direction']} (confidence: {signal['confidence']:.2f})")
    else:
        print("  No signals found")

    # Show portfolio status
    print("\n3. Portfolio Status:")
    report = system.get_performance_report()
    portfolio = report['portfolio_summary']

    print(f"  Current Capital: ${portfolio['current_capital']:,.2f}")
    print(f"  Total Equity: ${portfolio['total_equity']:,.2f}")
    print(f"  Open Positions: {portfolio['positions_count']}")
    print(f"  Max Drawdown Limit: ${portfolio['max_drawdown_limit']:,.2f}")

    # Export trades if any
    if report['performance_metrics']:
        print(f"\n4. Performance Metrics:")
        metrics = report['performance_metrics']
        print(f"  Total Trades: {metrics.get('total_trades', 0)}")
        print(f"  Win Rate: {metrics.get('win_rate', 0)*100:.1f}%")
        print(f"  Total Return: {metrics.get('return_percentage', 0):.2f}%")

    print("\nSystem ready for live trading!")
    print("To start automated trading, call: system.schedule_trading()")

if __name__ == "__main__":
    main()
