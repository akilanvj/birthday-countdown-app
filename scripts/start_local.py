#!/usr/bin/env python3
"""
Simple startup script for the Birthday Countdown local development server.
"""

import sys
import os

def main():
    # Check if we're in the right directory
    if not os.path.exists('src/web/index.html'):
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure you can see the 'src' folder from here")
        sys.exit(1)
    
    # Import and run the server
    try:
        sys.path.append('scripts')
        from local_server import run_server
        run_server(port=8000)
    except ImportError as e:
        print(f"❌ Error importing local_server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()