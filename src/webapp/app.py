#!/usr/bin/env python3
"""
Flask web application version of the Birthday Countdown app.
This version is designed for Azure App Service deployment.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from datetime import datetime, date, timedelta
import re
import json

# Create Flask app
app = Flask(__name__, 
           static_folder='../web',
           template_folder='../web')

def calculate_age_years(birth_date: date, current_date: date) -> int:
    """Calculate the current age in complete years."""
    age = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def calculate_next_birthday(birth_date: date, current_date: date) -> date:
    """Calculate the next birthday date."""
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

def generate_message(days_until: int) -> str:
    """Generate a friendly message based on days until birthday."""
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

def parse_and_validate_date(dob_str: str):
    """Parse and validate the date of birth."""
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

# Routes
@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS)."""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/nextbirthday', methods=['GET'])
def nextbirthday():
    """API endpoint for birthday calculations."""
    try:
        # Get date of birth parameter
        dob_param = request.args.get('dob')
        
        if not dob_param:
            error_response = {
                "error": "Missing required parameter 'dob'",
                "message": "Please provide your date of birth in YYYY-MM-DD format",
                "example": "GET /api/nextbirthday?dob=1990-05-15"
            }
            return jsonify(error_response), 400
        
        # Parse and validate date
        parsed_date, error_response = parse_and_validate_date(dob_param)
        if error_response:
            return jsonify(error_response), 400
        
        # Calculate birthday information
        current_date = date.today()
        age_years = calculate_age_years(parsed_date, current_date)
        next_birthday_date = calculate_next_birthday(parsed_date, current_date)
        days_until = (next_birthday_date - current_date).days
        day_of_week = next_birthday_date.strftime('%A')
        message = generate_message(days_until)
        
        result = {
            "inputDob": dob_param,
            "ageYears": age_years,
            "nextBirthdayDate": next_birthday_date.strftime('%Y-%m-%d'),
            "nextBirthdayDayOfWeek": day_of_week,
            "daysUntilNextBirthday": days_until,
            "message": message
        }
        
        return jsonify(result)
        
    except Exception as e:
        error_response = {
            "error": "Internal server error",
            "message": str(e)
        }
        return jsonify(error_response), 500

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))