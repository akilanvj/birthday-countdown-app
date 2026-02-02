#!/usr/bin/env python3
"""
Local development server for Birthday Countdown application.
This server mimics the Azure Functions behavior for local testing.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from datetime import datetime, date, timedelta
import re

class BirthdayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        # Handle API endpoint
        if parsed_url.path == '/api/nextbirthday':
            self.handle_birthday_api(parsed_url)
        # Serve static files
        elif parsed_url.path == '/' or parsed_url.path == '/index.html':
            self.serve_file('src/web/index.html', 'text/html')
        elif parsed_url.path == '/app.js':
            self.serve_file('src/web/app.js', 'application/javascript')
        elif parsed_url.path == '/styles.css':
            self.serve_file('src/web/styles.css', 'text/css')
        else:
            self.send_error(404, "File not found")
    
    def handle_birthday_api(self, parsed_url):
        """Handle the birthday API endpoint"""
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)
            dob_param = query_params.get('dob', [None])[0]
            
            # Validate input
            if not dob_param:
                error_response = {
                    "error": "Missing required parameter 'dob'",
                    "message": "Please provide your date of birth in YYYY-MM-DD format",
                    "example": "GET /api/nextbirthday?dob=1990-05-15"
                }
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Parse and validate date
            parsed_date, error_response = self.parse_and_validate_date(dob_param)
            if error_response:
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Calculate birthday information
            result = self.calculate_birthday_info(dob_param, parsed_date)
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_response = {
                "error": "Internal server error",
                "message": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_file(self, filepath, content_type):
        """Serve static files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, f"File {filepath} not found")
    
    def parse_and_validate_date(self, dob_str):
        """Parse and validate the date of birth"""
        # Validate format using regex
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob_str):
            return None, {
                "error": "Invalid date format",
                "message": "Date must be in YYYY-MM-DD format",
                "example": "GET /api/nextbirthday?dob=1990-05-15"
            }
        
        try:
            parsed_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return None, {
                "error": "Invalid date",
                "message": "Please provide a valid date in YYYY-MM-DD format",
                "example": "GET /api/nextbirthday?dob=1990-05-15"
            }
        
        # Check if date is in the future
        current_date = date.today()
        if parsed_date > current_date:
            return None, {
                "error": "Date of birth cannot be in the future",
                "message": "Please provide a valid past date",
                "example": "GET /api/nextbirthday?dob=1990-05-15"
            }
        
        return parsed_date, None
    
    def calculate_birthday_info(self, input_dob, birth_date):
        """Calculate all birthday information"""
        current_date = date.today()
        
        # Calculate age in complete years
        age_years = self.calculate_age_years(birth_date, current_date)
        
        # Calculate next birthday
        next_birthday_date = self.calculate_next_birthday(birth_date, current_date)
        
        # Calculate days until next birthday
        days_until = (next_birthday_date - current_date).days
        
        # Get day of week
        day_of_week = next_birthday_date.strftime('%A')
        
        # Generate message
        message = self.generate_message(days_until)
        
        return {
            "inputDob": input_dob,
            "ageYears": age_years,
            "nextBirthdayDate": next_birthday_date.strftime('%Y-%m-%d'),
            "nextBirthdayDayOfWeek": day_of_week,
            "daysUntilNextBirthday": days_until,
            "message": message
        }
    
    def calculate_age_years(self, birth_date, current_date):
        """Calculate current age in complete years"""
        age = current_date.year - birth_date.year
        if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    
    def calculate_next_birthday(self, birth_date, current_date):
        """Calculate the next birthday date"""
        current_year = current_date.year
        
        # Try this year first
        try:
            next_birthday = date(current_year, birth_date.month, birth_date.day)
            if next_birthday >= current_date:
                return next_birthday
        except ValueError:
            # Handle Feb 29 in non-leap year
            if birth_date.month == 2 and birth_date.day == 29:
                next_birthday = date(current_year, 2, 28)
                if next_birthday >= current_date:
                    return next_birthday
        
        # Try next year
        next_year = current_year + 1
        try:
            return date(next_year, birth_date.month, birth_date.day)
        except ValueError:
            # Handle Feb 29 in non-leap year
            if birth_date.month == 2 and birth_date.day == 29:
                return date(next_year, 2, 28)
            raise
    
    def generate_message(self, days_until):
        """Generate a friendly message based on days until birthday"""
        if days_until == 0:
            return "🎉 Happy Birthday! It's your special day!"
        elif days_until == 1:
            return "🎂 Your birthday is tomorrow! Get ready to celebrate!"
        elif days_until <= 7:
            return f"🎈 Your birthday is in {days_until} days! The countdown begins!"
        elif days_until <= 30:
            return f"🗓️ Your birthday is in {days_until} days. Mark your calendar!"
        elif days_until <= 90:
            return f"⏰ Your birthday is in {days_until} days. Time to start planning!"
        else:
            return f"📅 Your birthday is in {days_until} days. Plenty of time to prepare!"

def run_server(port=8000):
    """Run the local development server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BirthdayHandler)
    
    print(f"🎂 Birthday Countdown Local Server")
    print(f"📍 Server running at: http://localhost:{port}")
    print(f"🌐 Frontend: http://localhost:{port}")
    print(f"🔗 API: http://localhost:{port}/api/nextbirthday?dob=1990-05-15")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server()