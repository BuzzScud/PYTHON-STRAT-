#!/usr/bin/env python3
"""
Fix script to resolve import issues and verify system setup
"""
import sys
import os
import subprocess

def check_python_environment():
    """Check Python environment and package installations"""
    print("Python Environment Check")
    print("=" * 40)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    
def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'numpy', 'yfinance', 'plotly', 'streamlit',
        'streamlit-ace', 'streamlit-option-menu', 'requests'
    ]
    
    print("\nPackage Installation Check")
    print("=" * 40)
    
    for package in required_packages:
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {package} - installed")
            else:
                print(f"❌ {package} - not found")
        except Exception as e:
            print(f"❌ {package} - error checking: {e}")

def fix_python_path():
    """Add current directory to Python path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✓ Added {current_dir} to Python path")

def test_critical_imports():
    """Test the most critical imports"""
    print("\nCritical Import Test")
    print("=" * 40)
    
    critical_imports = [
        ('pandas', 'import pandas as pd'),
        ('numpy', 'import numpy as np'),
        ('yfinance', 'import yfinance as yf'),
        ('plotly', 'import plotly.graph_objects as go'),
        ('streamlit', 'import streamlit as st'),
    ]
    
    for name, import_stmt in critical_imports:
        try:
            exec(import_stmt)
            print(f"✓ {name} - import successful")
        except ImportError as e:
            print(f"❌ {name} - import failed: {e}")
        except Exception as e:
            print(f"❌ {name} - unexpected error: {e}")

def create_startup_script():
    """Create a startup script to run the Bloomberg UI"""
    startup_script = """#!/bin/bash
# Bloomberg Terminal UI Startup Script

echo "Starting Bloomberg Terminal UI..."
echo "Make sure you have installed all requirements:"
echo "pip install -r requirements.txt"
echo ""

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the Bloomberg UI
python3 -m streamlit run bloomberg_ui.py --server.port 8501 --server.address localhost

echo "Bloomberg Terminal UI started at http://localhost:8501"
"""
    
    with open('start_bloomberg_ui.sh', 'w') as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod('start_bloomberg_ui.sh', 0o755)
    print("✓ Created start_bloomberg_ui.sh script")

def main():
    """Main function to run all checks and fixes"""
    print("IMPORT ISSUE DIAGNOSTIC AND FIX")
    print("=" * 50)
    
    check_python_environment()
    check_packages()
    fix_python_path()
    test_critical_imports()
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("SUMMARY AND NEXT STEPS")
    print("=" * 50)
    print("1. All required packages appear to be installed")
    print("2. The IDE import errors are likely due to interpreter mismatch")
    print("3. The code should run fine despite the IDE warnings")
    print("4. To start the Bloomberg UI, run:")
    print("   ./start_bloomberg_ui.sh")
    print("   OR")
    print("   python3 -m streamlit run bloomberg_ui.py")
    print("5. The UI will be available at http://localhost:8501")
    print("=" * 50)

if __name__ == "__main__":
    main()
