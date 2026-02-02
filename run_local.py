#!/usr/bin/env python3
"""
Main entry point for running the Birthday Countdown application locally.
This script provides a simple way to start the local development server.
"""

import sys
import os

def main():
    # Add scripts directory to path
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    sys.path.insert(0, scripts_dir)
    
    # Import and run the startup script
    try:
        from start_local import main as start_main
        start_main()
    except ImportError as e:
        print(f"❌ Error importing startup script: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()