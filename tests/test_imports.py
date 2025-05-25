#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing core data libraries...")
        import pandas as pd
        import numpy as np
        print("✓ pandas and numpy imported successfully")
        
        print("Testing market data libraries...")
        import yfinance as yf
        print("✓ yfinance imported successfully")
        
        print("Testing visualization libraries...")
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        print("✓ plotly imported successfully")
        
        print("Testing streamlit libraries...")
        import streamlit as st
        from streamlit_option_menu import option_menu
        from streamlit_ace import st_ace
        print("✓ streamlit libraries imported successfully")
        
        print("Testing other libraries...")
        import requests
        import sqlalchemy
        print("✓ requests and sqlalchemy imported successfully")
        
        print("Testing local modules...")
        from trading_core.market_data_api import MarketDataAPI, SymbolInfo
        print("✓ market_data_api imported successfully")
        
        print("\n🎉 All imports successful! The system is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nTesting basic functionality...")
        
        # Test pandas
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        print(f"✓ pandas DataFrame created: {len(df)} rows")
        
        # Test numpy
        import numpy as np
        arr = np.array([1, 2, 3])
        print(f"✓ numpy array created: {arr.shape}")
        
        # Test market data API
        from trading_core.market_data_api import MarketDataAPI
        api = MarketDataAPI()
        print("✓ MarketDataAPI instance created")
        
        print("\n🎉 Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("IMPORT AND FUNCTIONALITY TEST")
    print("=" * 50)
    
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if imports_ok and functionality_ok:
        print("✅ ALL TESTS PASSED - System is ready!")
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
    print("=" * 50)
