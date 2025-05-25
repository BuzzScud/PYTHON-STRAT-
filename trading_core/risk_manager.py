"""
Risk Management System for Algorithmic Trading
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from config.config import trading_config, instrument_config

class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, initial_capital: float = 100000):
        self.logger = logging.getLogger(__name__)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_drawdown_reached = 0
        self.daily_pnl = 0
        self.positions = {}  # Track current positions
        self.trade_history = []
        
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float, 
                              account_balance: float) -> int:
        """Calculate position size based on risk per trade"""
        try:
            # Risk amount per trade
            risk_amount = account_balance * trading_config.RISK_PER_TRADE
            
            # Price difference (risk per unit)
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                self.logger.warning(f"Zero price difference for {symbol}, cannot calculate position size")
                return 0
            
            # Determine if futures or forex
            if symbol in trading_config.FUTURES_SYMBOLS:
                # Futures position sizing
                specs = instrument_config.FUTURES_SPECS[symbol]
                tick_value = specs['tick_value']
                tick_size = specs['tick_size']
                
                # Calculate ticks at risk
                ticks_at_risk = price_diff / tick_size
                risk_per_contract = ticks_at_risk * tick_value
                
                # Position size (number of contracts)
                position_size = int(risk_amount / risk_per_contract)
                
                # Check margin requirements
                margin_required = position_size * specs['margin_requirement']
                if margin_required > account_balance * 0.3:  # Max 30% of capital for margin
                    position_size = int((account_balance * 0.3) / specs['margin_requirement'])
                    
            else:
                # Forex position sizing
                specs = instrument_config.FOREX_SPECS[symbol]
                pip_value = specs['pip_value']
                
                # Assume standard lot size (100,000 units)
                standard_lot = 100000
                
                # Calculate pips at risk
                pips_at_risk = price_diff / pip_value
                
                # Risk per standard lot
                risk_per_lot = pips_at_risk * 10  # $10 per pip for standard lot
                
                # Position size (in lots)
                lots = risk_amount / risk_per_lot
                position_size = int(lots * standard_lot)  # Convert to units
            
            self.logger.info(f"Calculated position size for {symbol}: {position_size}")
            return max(0, position_size)
            
        except Exception as e:
            self.logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0
    
    def check_risk_limits(self, symbol: str, position_size: int, entry_price: float) -> bool:
        """Check if trade meets risk management criteria"""
        try:
            # Check maximum positions limit
            if len(self.positions) >= trading_config.MAX_POSITIONS:
                self.logger.warning("Maximum positions limit reached")
                return False
            
            # Check if already have position in this symbol
            if symbol in self.positions:
                self.logger.warning(f"Already have position in {symbol}")
                return False
            
            # Check maximum drawdown
            current_drawdown = self.initial_capital - self.current_capital
            if current_drawdown >= trading_config.MAX_DRAWDOWN_USD:
                self.logger.warning(f"Maximum drawdown limit reached: ${current_drawdown}")
                return False
            
            # Check correlation limits (simplified)
            if self._check_correlation_limits(symbol):
                return False
            
            # Check position size is reasonable
            if position_size <= 0:
                self.logger.warning(f"Invalid position size: {position_size}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return False
    
    def _check_correlation_limits(self, symbol: str) -> bool:
        """Check if adding this position would violate correlation limits"""
        # Simplified correlation check
        # In practice, you'd calculate actual correlations
        
        if symbol in trading_config.FUTURES_SYMBOLS:
            # Check if already have other futures positions
            futures_positions = [s for s in self.positions.keys() if s in trading_config.FUTURES_SYMBOLS]
            if len(futures_positions) >= 2:  # Max 2 futures positions
                return True
                
        if symbol in trading_config.FOREX_SYMBOLS:
            # Check if already have other forex positions
            forex_positions = [s for s in self.positions.keys() if s in trading_config.FOREX_SYMBOLS]
            if len(forex_positions) >= 2:  # Max 2 forex positions
                return True
        
        return False
    
    def add_position(self, symbol: str, position_size: int, entry_price: float, 
                    stop_loss: float, take_profit: Optional[float] = None, 
                    direction: str = 'LONG') -> bool:
        """Add a new position to the portfolio"""
        try:
            if not self.check_risk_limits(symbol, position_size, entry_price):
                return False
            
            position = {
                'symbol': symbol,
                'size': position_size,
                'direction': direction,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_time': datetime.now(),
                'unrealized_pnl': 0,
                'max_favorable': 0,
                'max_adverse': 0
            }
            
            self.positions[symbol] = position
            self.logger.info(f"Added position: {symbol} {direction} {position_size} @ {entry_price}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding position: {e}")
            return False
    
    def update_position_pnl(self, symbol: str, current_price: float):
        """Update unrealized P&L for a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        size = position['size']
        direction = position['direction']
        
        # Calculate unrealized P&L
        if symbol in trading_config.FUTURES_SYMBOLS:
            specs = instrument_config.FUTURES_SPECS[symbol]
            tick_size = specs['tick_size']
            tick_value = specs['tick_value']
            
            price_diff = current_price - entry_price
            if direction == 'SHORT':
                price_diff = -price_diff
                
            ticks = price_diff / tick_size
            unrealized_pnl = ticks * tick_value * size
            
        else:  # Forex
            specs = instrument_config.FOREX_SPECS[symbol]
            pip_value = specs['pip_value']
            
            price_diff = current_price - entry_price
            if direction == 'SHORT':
                price_diff = -price_diff
                
            pips = price_diff / pip_value
            unrealized_pnl = pips * 10 * (size / 100000)  # Assuming $10 per pip per standard lot
        
        position['unrealized_pnl'] = unrealized_pnl
        
        # Track maximum favorable/adverse excursion
        if unrealized_pnl > position['max_favorable']:
            position['max_favorable'] = unrealized_pnl
        if unrealized_pnl < position['max_adverse']:
            position['max_adverse'] = unrealized_pnl
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """Check if stop loss should be triggered"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        stop_loss = position['stop_loss']
        direction = position['direction']
        
        if direction == 'LONG' and current_price <= stop_loss:
            return True
        elif direction == 'SHORT' and current_price >= stop_loss:
            return True
            
        return False
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """Check if take profit should be triggered"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        take_profit = position.get('take_profit')
        
        if take_profit is None:
            return False
        
        direction = position['direction']
        
        if direction == 'LONG' and current_price >= take_profit:
            return True
        elif direction == 'SHORT' and current_price <= take_profit:
            return True
            
        return False
    
    def close_position(self, symbol: str, exit_price: float, reason: str = 'MANUAL') -> Dict:
        """Close a position and calculate realized P&L"""
        if symbol not in self.positions:
            self.logger.warning(f"No position found for {symbol}")
            return {}
        
        position = self.positions[symbol]
        
        # Calculate final P&L
        self.update_position_pnl(symbol, exit_price)
        realized_pnl = position['unrealized_pnl']
        
        # Update capital
        self.current_capital += realized_pnl
        
        # Create trade record
        trade_record = {
            'symbol': symbol,
            'direction': position['direction'],
            'size': position['size'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'realized_pnl': realized_pnl,
            'max_favorable': position['max_favorable'],
            'max_adverse': position['max_adverse'],
            'exit_reason': reason
        }
        
        self.trade_history.append(trade_record)
        
        # Remove position
        del self.positions[symbol]
        
        self.logger.info(f"Closed position: {symbol} P&L: ${realized_pnl:.2f} Reason: {reason}")
        
        return trade_record
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_unrealized = sum(pos['unrealized_pnl'] for pos in self.positions.values())
        current_drawdown = self.initial_capital - self.current_capital
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'unrealized_pnl': total_unrealized,
            'total_equity': self.current_capital + total_unrealized,
            'current_drawdown': current_drawdown,
            'max_drawdown_limit': trading_config.MAX_DRAWDOWN_USD,
            'positions_count': len(self.positions),
            'max_positions': trading_config.MAX_POSITIONS,
            'trades_completed': len(self.trade_history)
        }
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trade_history:
            return {}
        
        pnls = [trade['realized_pnl'] for trade in self.trade_history]
        
        total_return = sum(pnls)
        win_rate = len([pnl for pnl in pnls if pnl > 0]) / len(pnls)
        avg_win = np.mean([pnl for pnl in pnls if pnl > 0]) if any(pnl > 0 for pnl in pnls) else 0
        avg_loss = np.mean([pnl for pnl in pnls if pnl < 0]) if any(pnl < 0 for pnl in pnls) else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        return {
            'total_trades': len(self.trade_history),
            'total_return': total_return,
            'win_rate': win_rate,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'return_percentage': (total_return / self.initial_capital) * 100
        }
