#!/usr/bin/env python3
"""
Launch script for Bloomberg Terminal Style Trading UI
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit',
        'streamlit-ace',
        'streamlit-aggrid', 
        'streamlit-option-menu',
        'pandas',
        'numpy',
        'plotly',
        'yfinance',
        'pandas-ta'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("🔧 Installing required dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_system_files():
    """Check if all system files exist"""
    required_files = [
        'config.py',
        'data_manager.py',
        'technical_indicators.py',
        'risk_manager.py',
        'strategy_framework.py',
        'backtesting_engine.py',
        'trading_system.py',
        'bloomberg_ui.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not Path('.env').exists():
        print("📝 Creating .env configuration file...")
        
        env_content = """# Trading System Configuration
PAPER_TRADING=True
LOG_LEVEL=INFO
DATABASE_PATH=trading_data.db

# Risk Management
RISK_PER_TRADE=0.0025
MAX_DRAWDOWN_USD=1500
MAX_POSITIONS=6

# API Keys (Optional)
ALPHA_VANTAGE_KEY=
FRED_API_KEY=
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")

def launch_ui():
    """Launch the Streamlit UI"""
    print("🚀 Launching Bloomberg Terminal Style Trading UI...")
    print("📊 The terminal will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*60)
    print("🔥 ALGORITHMIC TRADING TERMINAL")
    print("="*60)
    print("📈 Features:")
    print("  • Real-time Dashboard")
    print("  • Strategy Editor with Syntax Highlighting")
    print("  • Advanced Backtesting Engine")
    print("  • Risk Management Tools")
    print("  • Bloomberg Terminal Style Interface")
    print("="*60)
    print("\n⚠️  IMPORTANT: This is for PAPER TRADING only!")
    print("💡 Press Ctrl+C to stop the terminal")
    print("\n")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'bloomberg_ui.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false',
            '--theme.base=dark',
            '--theme.primaryColor=#ff6600',
            '--theme.backgroundColor=#000000',
            '--theme.secondaryBackgroundColor=#1a1a1a',
            '--theme.textColor=#ffffff'
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Trading Terminal stopped by user")
        print("💾 All data has been saved")
        print("👋 Thank you for using the Algorithmic Trading Terminal!")
    except Exception as e:
        print(f"\n❌ Error launching UI: {e}")
        print("🔧 Try running: streamlit run bloomberg_ui.py")

def main():
    """Main launcher function"""
    print("🔥 ALGORITHMIC TRADING TERMINAL LAUNCHER")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path('bloomberg_ui.py').exists():
        print("❌ Error: bloomberg_ui.py not found!")
        print("📁 Please run this script from the trading system directory")
        sys.exit(1)
    
    # Check system files
    print("🔍 Checking system files...")
    missing_files = check_system_files()
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("📁 Please ensure all trading system files are present")
        sys.exit(1)
    
    print("✅ All system files found")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"📦 Missing packages: {missing_packages}")
        
        install_choice = input("🤔 Install missing packages? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            if not install_dependencies():
                print("❌ Failed to install dependencies")
                sys.exit(1)
        else:
            print("❌ Cannot proceed without required packages")
            print("💡 Run: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies satisfied")
    
    # Create .env file if needed
    create_env_file()
    
    # Launch the UI
    print("\n🎯 System ready! Launching terminal...")
    time.sleep(2)
    
    launch_ui()

if __name__ == "__main__":
    main()
