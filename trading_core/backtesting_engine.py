"""
Backtesting Engine for Strategy Validation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from trading_core.strategy_framework import BaseStrategy
from trading_core.risk_manager import RiskManager
from trading_core.data_manager import DataManager
from config.config import trading_config

class BacktestEngine:
    """Comprehensive backtesting engine"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(__name__)
        self.results = {}
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, strategy: BaseStrategy, start_date: str, end_date: str, 
                    timeframe: str = '1d') -> Dict:
        """Run comprehensive backtest"""
        self.logger.info(f"Starting backtest for {strategy.name}")
        
        # Initialize components
        data_manager = DataManager()
        risk_manager = RiskManager(self.initial_capital)
        
        # Get historical data
        all_data = self._get_backtest_data(data_manager, start_date, end_date, timeframe)
        
        if not all_data:
            self.logger.error("No data available for backtesting")
            return {}
        
        # Run simulation
        results = self._simulate_trading(strategy, risk_manager, all_data, timeframe)
        
        # Calculate performance metrics
        performance = self._calculate_performance_metrics(results, risk_manager)
        
        # Generate reports
        self._generate_backtest_report(strategy, performance, risk_manager)
        
        return performance
    
    def _get_backtest_data(self, data_manager: DataManager, start_date: str, 
                          end_date: str, timeframe: str) -> Dict[str, pd.DataFrame]:
        """Get historical data for backtesting"""
        all_data = {}
        
        # Calculate period for yfinance
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        days_diff = (end - start).days
        
        if days_diff <= 365:
            period = "1y"
        elif days_diff <= 730:
            period = "2y"
        else:
            period = "5y"
        
        # Get data for all instruments
        for symbol in trading_config.FUTURES_SYMBOLS + trading_config.FOREX_SYMBOLS:
            try:
                if symbol in trading_config.FUTURES_SYMBOLS:
                    data = data_manager.get_futures_data(symbol, period=period, interval=timeframe)
                else:
                    data = data_manager.get_forex_data(symbol, period=period, interval=timeframe)
                
                if not data.empty:
                    # Filter by date range
                    data = data.loc[start_date:end_date]
                    all_data[symbol] = data
                    self.logger.info(f"Loaded {len(data)} records for {symbol}")
                    
            except Exception as e:
                self.logger.error(f"Error loading data for {symbol}: {e}")
        
        return all_data
    
    def _simulate_trading(self, strategy: BaseStrategy, risk_manager: RiskManager, 
                         all_data: Dict[str, pd.DataFrame], timeframe: str) -> Dict:
        """Simulate trading with the strategy"""
        # Get all unique timestamps
        all_timestamps = set()
        for df in all_data.values():
            all_timestamps.update(df.index)
        
        timestamps = sorted(all_timestamps)
        
        equity_history = []
        trade_log = []
        
        for i, timestamp in enumerate(timestamps):
            # Get current data slice (up to current timestamp)
            current_data = {}
            for symbol, df in all_data.items():
                if timestamp in df.index:
                    # Get data up to current timestamp
                    current_slice = df.loc[:timestamp]
                    if len(current_slice) >= 20:  # Minimum data for indicators
                        current_data[symbol] = current_slice
            
            if not current_data:
                continue
            
            # Update existing positions with current prices
            for symbol in list(risk_manager.positions.keys()):
                if symbol in current_data:
                    current_price = current_data[symbol].iloc[-1]['close']
                    risk_manager.update_position_pnl(symbol, current_price)
                    
                    # Check stop loss and take profit
                    if risk_manager.check_stop_loss(symbol, current_price):
                        trade = risk_manager.close_position(symbol, current_price, 'STOP_LOSS')
                        trade_log.append(trade)
                        
                    elif risk_manager.check_take_profit(symbol, current_price):
                        trade = risk_manager.close_position(symbol, current_price, 'TAKE_PROFIT')
                        trade_log.append(trade)
            
            # Generate new signals
            signals = strategy.execute_strategy(current_data)
            
            # Process signals
            for signal in signals:
                symbol = signal['symbol']
                
                if symbol not in current_data:
                    continue
                
                # Calculate entry, stop loss, take profit
                entry_price, stop_loss, take_profit = strategy.calculate_entry_exit(
                    symbol, current_data[symbol], signal
                )
                
                # Calculate position size
                position_size = risk_manager.calculate_position_size(
                    symbol, entry_price, stop_loss, risk_manager.current_capital
                )
                
                # Try to add position
                if risk_manager.add_position(
                    symbol, position_size, entry_price, stop_loss, 
                    take_profit, signal['direction']
                ):
                    self.logger.info(f"Opened position: {symbol} {signal['direction']} @ {entry_price}")
            
            # Record equity
            portfolio_summary = risk_manager.get_portfolio_summary()
            equity_history.append({
                'timestamp': timestamp,
                'equity': portfolio_summary['total_equity'],
                'cash': portfolio_summary['current_capital'],
                'unrealized_pnl': portfolio_summary['unrealized_pnl'],
                'positions': portfolio_summary['positions_count']
            })
        
        return {
            'equity_history': equity_history,
            'trade_log': trade_log,
            'final_portfolio': risk_manager.get_portfolio_summary(),
            'performance_metrics': risk_manager.get_performance_metrics()
        }
    
    def _calculate_performance_metrics(self, results: Dict, risk_manager: RiskManager) -> Dict:
        """Calculate comprehensive performance metrics"""
        equity_df = pd.DataFrame(results['equity_history'])
        
        if equity_df.empty:
            return {}
        
        equity_df.set_index('timestamp', inplace=True)
        
        # Basic metrics
        total_return = (equity_df['equity'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns
        equity_df['daily_return'] = equity_df['equity'].pct_change()
        
        # Risk metrics
        volatility = equity_df['daily_return'].std() * np.sqrt(252)  # Annualized
        sharpe_ratio = (equity_df['daily_return'].mean() * 252) / (equity_df['daily_return'].std() * np.sqrt(252))
        
        # Drawdown calculation
        equity_df['peak'] = equity_df['equity'].expanding().max()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        
        # Trade-based metrics
        trade_metrics = risk_manager.get_performance_metrics()
        
        performance = {
            'total_return_pct': total_return * 100,
            'total_return_usd': equity_df['equity'].iloc[-1] - self.initial_capital,
            'volatility_pct': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown * 100,
            'calmar_ratio': (total_return * 100) / abs(max_drawdown * 100) if max_drawdown != 0 else 0,
            'final_equity': equity_df['equity'].iloc[-1],
            'equity_curve': equity_df,
            **trade_metrics
        }
        
        return performance
    
    def _generate_backtest_report(self, strategy: BaseStrategy, performance: Dict, 
                                 risk_manager: RiskManager):
        """Generate comprehensive backtest report"""
        print("\n" + "="*60)
        print(f"BACKTEST REPORT - {strategy.name}")
        print("="*60)
        
        print(f"\nPERFORMANCE SUMMARY:")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Equity: ${performance.get('final_equity', 0):,.2f}")
        print(f"Total Return: {performance.get('total_return_pct', 0):.2f}%")
        print(f"Total Return ($): ${performance.get('total_return_usd', 0):,.2f}")
        
        print(f"\nRISK METRICS:")
        print(f"Volatility: {performance.get('volatility_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {performance.get('max_drawdown_pct', 0):.2f}%")
        print(f"Calmar Ratio: {performance.get('calmar_ratio', 0):.2f}")
        
        print(f"\nTRADE STATISTICS:")
        print(f"Total Trades: {performance.get('total_trades', 0)}")
        print(f"Win Rate: {performance.get('win_rate', 0)*100:.1f}%")
        print(f"Average Win: ${performance.get('average_win', 0):.2f}")
        print(f"Average Loss: ${performance.get('average_loss', 0):.2f}")
        print(f"Profit Factor: {performance.get('profit_factor', 0):.2f}")
        
        print("\n" + "="*60)
    
    def plot_results(self, performance: Dict, strategy_name: str):
        """Plot backtest results"""
        if 'equity_curve' not in performance:
            return
        
        equity_df = performance['equity_curve']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Backtest Results - {strategy_name}', fontsize=16)
        
        # Equity curve
        axes[0, 0].plot(equity_df.index, equity_df['equity'])
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].grid(True)
        
        # Drawdown
        axes[0, 1].fill_between(equity_df.index, equity_df['drawdown'] * 100, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True)
        
        # Daily returns distribution
        axes[1, 0].hist(equity_df['daily_return'].dropna() * 100, bins=50, alpha=0.7)
        axes[1, 0].set_title('Daily Returns Distribution')
        axes[1, 0].set_xlabel('Daily Return (%)')
        axes[1, 0].grid(True)
        
        # Rolling Sharpe ratio
        rolling_sharpe = equity_df['daily_return'].rolling(30).mean() / equity_df['daily_return'].rolling(30).std() * np.sqrt(252)
        axes[1, 1].plot(equity_df.index, rolling_sharpe)
        axes[1, 1].set_title('30-Day Rolling Sharpe Ratio')
        axes[1, 1].set_ylabel('Sharpe Ratio')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
        
        return fig
