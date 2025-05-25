#!/usr/bin/env python3
"""
Simple launcher for the Bloomberg UI web application
"""
import sys
import os
import subprocess

# Add the workspace root to Python path
workspace_root = os.path.dirname(os.path.abspath(__file__))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

def main():
    """Launch the Bloomberg UI web application"""
    print("🚀 Launching ICT Trading System Web Application...")
    print("=" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = workspace_root
    
    # Try different streamlit commands
    streamlit_commands = [
        ['streamlit', 'run', 'interfaces/bloomberg_ui.py'],
        ['python3', '-m', 'streamlit', 'run', 'interfaces/bloomberg_ui.py'],
        ['python', '-m', 'streamlit', 'run', 'interfaces/bloomberg_ui.py']
    ]
    
    for cmd in streamlit_commands:
        try:
            print(f"Trying: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, cwd=workspace_root, check=True)
            break
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed: {e}")
            continue
    else:
        print("\n❌ Could not launch Streamlit web app.")
        print("\n🔧 Manual launch options:")
        print("1. Install streamlit: pip install streamlit")
        print("2. Run manually: streamlit run interfaces/bloomberg_ui.py")
        print("3. Or use: python -m streamlit run interfaces/bloomberg_ui.py")
        return False
    
    return True

if __name__ == "__main__":
    main()
