#!/usr/bin/env python3
"""
Simple local server for the Birthday Countdown frontend
Run this while fixing Azure deployment issues
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8080
DIRECTORY = "src/web"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Disable caching for development
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    # Check if the web directory exists
    web_dir = Path(DIRECTORY)
    if not web_dir.exists():
        print(f"❌ Directory '{DIRECTORY}' not found!")
        print("Make sure you're running this from the project root.")
        return
    
    # Check if index.html exists
    index_file = web_dir / "index.html"
    if not index_file.exists():
        print(f"❌ index.html not found in '{DIRECTORY}'!")
        return
    
    print(f"🎂 Starting Birthday Countdown local server...")
    print(f"📁 Serving files from: {web_dir.absolute()}")
    print(f"🌐 Server running at: http://localhost:{PORT}")
    print(f"🔗 Direct link: http://localhost:{PORT}/index.html")
    print("\n💡 This is a temporary solution while you fix Azure deployment")
    print("📖 See fix-azure-deployment.md for deployment fix instructions")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            # Try to open browser automatically
            try:
                webbrowser.open(f"http://localhost:{PORT}")
                print("🚀 Browser opened automatically")
            except:
                print("🔧 Please open http://localhost:{PORT} in your browser")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print(f"Try a different port or stop the other server first.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()