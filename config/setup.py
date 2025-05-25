#!/usr/bin/env python3
"""
Quick setup script for the Algorithmic Trading System
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🔥 ALGORITHMIC TRADING SYSTEM - QUICK SETUP")
    print("="*55)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"📍 Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages"):
        print("💡 Try running manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file
    if not Path('.env').exists():
        print("\n📝 Creating configuration file...")
        env_content = """# Trading System Configuration
PAPER_TRADING=True
LOG_LEVEL=INFO
DATABASE_PATH=trading_data.db

# Risk Management
RISK_PER_TRADE=0.0025
MAX_DRAWDOWN_USD=1500
MAX_POSITIONS=6

# API Keys (Optional - leave empty to use free data)
ALPHA_VANTAGE_KEY=
FRED_API_KEY=
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Configuration file created (.env)")
    
    # Test the system
    print("\n🧪 Testing system components...")
    if run_command(f"{sys.executable} test_system.py", "Running system tests"):
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed, but you can still proceed")
    
    # Setup complete
    print("\n" + "="*55)
    print("🎉 SETUP COMPLETE!")
    print("="*55)
    
    print("\n🚀 NEXT STEPS:")
    print("1. Launch the Bloomberg Terminal UI:")
    print("   python launch_terminal.py")
    print("\n2. Or run individual components:")
    print("   python trading_system.py        # Command line interface")
    print("   python test_system.py          # Run tests")
    print("\n3. Access the web interface at:")
    print("   http://localhost:8501")
    
    print("\n📚 FEATURES:")
    print("• 📊 Real-time Dashboard")
    print("• 🧠 Strategy Editor")
    print("• 📈 Advanced Backtesting")
    print("• 🛡️ Risk Management")
    print("• ⚙️ System Configuration")
    
    print("\n⚠️  IMPORTANT:")
    print("• System starts in PAPER TRADING mode")
    print("• Never risk more than you can afford to lose")
    print("• Test thoroughly before any live trading")
    
    print("\n🔥 Ready to start trading!")

if __name__ == "__main__":
    main()
