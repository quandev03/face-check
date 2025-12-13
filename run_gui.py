#!/usr/bin/env python3
"""
Entry point for GUI Application
Run this script from the project root directory
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main
from gui_app.main import main

if __name__ == "__main__":
    main()





