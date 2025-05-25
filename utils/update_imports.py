#!/usr/bin/env python3
"""
Import Path Update Utility

This script helps update import statements after the workspace reorganization.
Run this script to automatically update import paths in all Python files.
"""

import os
import re
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # ICT Strategy imports
    'from ict_strategy.ict_strategy import': 'from ict_strategy.ict_strategy import',
    'from ict_strategy.ict_po3 import': 'from ict_strategy.ict_po3 import',
    'from ict_strategy.ict_goldbach import': 'from ict_strategy.ict_goldbach import',
    'from ict_strategy.ict_amd_cycles import': 'from ict_strategy.ict_amd_cycles import',
    'from ict_strategy.ict_hippo import': 'from ict_strategy.ict_hippo import',
    'from ict_strategy.standalone_ict_strategy import': 'from ict_strategy.standalone_ict_strategy import',
    
    # Trading Core imports
    'from trading_core.trading_system import': 'from trading_core.trading_system import',
    'from trading_core.strategy_framework import': 'from trading_core.strategy_framework import',
    'from trading_core.backtesting_engine import': 'from trading_core.backtesting_engine import',
    'from trading_core.risk_manager import': 'from trading_core.risk_manager import',
    'from trading_core.data_manager import': 'from trading_core.data_manager import',
    'from trading_core.market_data_api import': 'from trading_core.market_data_api import',
    'from trading_core.enhanced_market_data import': 'from trading_core.enhanced_market_data import',
    'from trading_core.technical_indicators import': 'from trading_core.technical_indicators import',
    
    # Configuration imports
    'from config.config import': 'from config.config import',
    
    # Import statements without 'from'
    'import ict_strategy.ict_strategy.ict_strategy.ict_strategy': 'import ict_strategy.ict_strategy.ict_strategy.ict_strategy.ict_strategy',
    'import trading_core.trading_system': 'import trading_core.trading_system',
    'import config.config.config.config': 'import config.config.config.config.config',
}

def update_file_imports(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated imports in: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def find_python_files(root_dir):
    """Find all Python files in the workspace."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function to update all import statements."""
    print("🔄 Starting import path updates...")
    print("=" * 50)
    
    # Get workspace root (parent of utils folder)
    workspace_root = Path(__file__).parent.parent
    
    # Find all Python files
    python_files = find_python_files(workspace_root)
    
    print(f"📁 Found {len(python_files)} Python files")
    print("=" * 50)
    
    updated_count = 0
    
    # Update each file
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_count += 1
    
    print("=" * 50)
    print(f"✨ Import update complete!")
    print(f"📊 Updated {updated_count} out of {len(python_files)} files")
    
    if updated_count > 0:
        print("\n⚠️  Important Notes:")
        print("1. Review the changes before running your code")
        print("2. Test all functionality after import updates")
        print("3. Some imports may need manual adjustment")
        print("4. Check for any circular import issues")

if __name__ == "__main__":
    main()
