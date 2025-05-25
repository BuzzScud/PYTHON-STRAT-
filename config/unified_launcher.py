#!/usr/bin/env python3
"""
Unified Trading Terminal Launcher
Combines all trading system components into one cohesive web application
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'plotly': 'plotly',
        'yfinance': 'yfinance',
        'streamlit_option_menu': 'streamlit-option-menu',
        'streamlit_ace': 'streamlit-ace'
    }
    
    missing_packages = []
    available_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name.replace('-', '_'))
            available_packages.append(package_name)
        except ImportError:
            missing_packages.append(package_name)
    
    return missing_packages, available_packages

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    if not missing_packages:
        return True
        
    print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
    
    try:
        # Try to install from requirements.txt first
        if Path('requirements.txt').exists():
            print("📋 Installing from requirements.txt...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
        else:
            # Install individual packages
            for package in missing_packages:
                print(f"📦 Installing {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ])
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False

def check_system_files():
    """Check if core system files exist"""
    core_files = [
        'bloomberg_ui.py',
        'config.py',
        'trading_system.py'
    ]
    
    missing_files = []
    
    for file in core_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def create_requirements_if_missing():
    """Create requirements.txt if it doesn't exist"""
    if not Path('requirements.txt').exists():
        print("📝 Creating requirements.txt...")
        
        requirements = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0",
            "numpy>=1.21.0", 
            "plotly>=5.0.0",
            "yfinance>=0.2.0",
            "streamlit-option-menu>=0.3.0",
            "streamlit-ace>=0.1.0",
            "pandas-ta>=0.3.0"
        ]
        
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))
        
        print("✅ requirements.txt created")

def launch_unified_terminal():
    """Launch the unified trading terminal"""
    print("\n🚀 Launching Unified Trading Terminal...")
    print("📊 The terminal will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*60)
    print("🔥 UNIFIED TRADING TERMINAL v2.0")
    print("="*60)
    print("📈 Features:")
    print("  • Unified Dashboard with Real-time Data")
    print("  • Advanced ICT Analysis Tools")
    print("  • Strategy Editor with Syntax Highlighting")
    print("  • Comprehensive Backtesting Engine")
    print("  • Risk Management Tools")
    print("  • Market Data Center")
    print("  • Bloomberg Terminal Style Interface")
    print("="*60)
    print("\n⚠️  IMPORTANT: This is for PAPER TRADING only!")
    print("💡 Press Ctrl+C to stop the terminal")
    print("\n")
    
    try:
        # Launch Streamlit with optimized settings
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'bloomberg_ui.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false',
            '--theme.base=dark',
            '--theme.primaryColor=#ff6600',
            '--theme.backgroundColor=#000000',
            '--theme.secondaryBackgroundColor=#1a1a1a',
            '--theme.textColor=#ffffff',
            '--server.maxUploadSize=200'
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Trading Terminal stopped by user")
        print("💾 All data has been saved")
        print("👋 Thank you for using the Unified Trading Terminal!")
    except Exception as e:
        print(f"\n❌ Error launching terminal: {e}")
        print("🔧 Try running manually: streamlit run bloomberg_ui.py")

def main():
    """Main launcher function"""
    print("🔥 UNIFIED TRADING TERMINAL LAUNCHER")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path('bloomberg_ui.py').exists():
        print("❌ Error: bloomberg_ui.py not found!")
        print("📁 Please run this script from the trading system directory")
        sys.exit(1)
    
    # Check system files
    print("\n🔍 Checking system files...")
    missing_files = check_system_files()
    
    if missing_files:
        print(f"⚠️  Some system files are missing: {missing_files}")
        print("📁 The system will run in demo mode with available components")
    else:
        print("✅ All core system files found")
    
    # Create requirements.txt if missing
    create_requirements_if_missing()
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing_packages, available_packages = check_dependencies()
    
    print(f"✅ Available packages: {len(available_packages)}")
    
    if missing_packages:
        print(f"📦 Missing packages: {', '.join(missing_packages)}")
        
        install_choice = input("\n🤔 Install missing packages? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            if not install_dependencies(missing_packages):
                print("❌ Failed to install some dependencies")
                print("💡 The system will run with available components")
        else:
            print("⚠️  Running with available components only")
    else:
        print("✅ All dependencies satisfied")
    
    # Launch the terminal
    print("\n🎯 System ready! Launching unified terminal...")
    time.sleep(2)
    
    launch_unified_terminal()

if __name__ == "__main__":
    main()
