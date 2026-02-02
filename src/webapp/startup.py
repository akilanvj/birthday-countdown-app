#!/usr/bin/env python3
"""
Startup script for Azure App Service.
This file is used by Azure to start the Flask application.
"""

from app import app

if __name__ == "__main__":
    app.run()