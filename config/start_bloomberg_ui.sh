#!/bin/bash
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
