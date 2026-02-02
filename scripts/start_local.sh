#!/bin/bash

echo "🎂 Starting Birthday Countdown Local Server..."
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.7+ and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "src/web/index.html" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Make sure you can see the 'src' folder from here"
    exit 1
fi

# Start the server
python3 scripts/start_local.py