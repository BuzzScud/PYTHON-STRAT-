#!/bin/bash
# Unified Trading Terminal Startup Script

echo "🔥 UNIFIED TRADING TERMINAL LAUNCHER"
echo "====================================="

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Run the unified launcher
echo "🚀 Starting Unified Trading Terminal..."
python3 unified_launcher.py

echo "👋 Unified Trading Terminal stopped"
