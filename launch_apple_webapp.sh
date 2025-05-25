#!/bin/bash

# Apple-compatible launcher for ICT Trading System Web Application
# This script is optimized for macOS systems

echo "Starting ICT Trading System Web Application..."
echo "================================================"

# Set environment variables for Apple compatibility
export PYTHONPATH="$(pwd)"
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system - using Apple-optimized settings"
    
    # Use Homebrew Python if available
    if command -v /usr/local/bin/python3 &> /dev/null; then
        PYTHON_CMD="/usr/local/bin/python3"
        echo "Using Homebrew Python: $PYTHON_CMD"
    elif command -v /opt/homebrew/bin/python3 &> /dev/null; then
        PYTHON_CMD="/opt/homebrew/bin/python3"
        echo "Using Apple Silicon Homebrew Python: $PYTHON_CMD"
    else
        PYTHON_CMD="python3"
        echo "Using system Python: $PYTHON_CMD"
    fi
else
    PYTHON_CMD="python3"
    echo "Using system Python: $PYTHON_CMD"
fi

# Check if Streamlit is installed
if ! $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo "Streamlit not found. Installing..."
    $PYTHON_CMD -m pip install streamlit plotly pandas numpy yfinance
fi

# Launch the web application
echo "Launching web application on http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo "================================================"

$PYTHON_CMD -m streamlit run interfaces/bloomberg_ui.py \
    --server.port 8501 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

echo "Web application stopped."
