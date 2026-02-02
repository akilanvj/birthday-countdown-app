import azure.functions as func
import logging
import json
from datetime import datetime, date, timedelta
import re

# Initialize the Azure Functions app using v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ============================================================================
# SHARED UTILITY FUNCTIONS
# ============================================================================

def calculate_age_years(birth_date: date, current_date: date) -> int:
    """
    Calculate the current age in complete years.
    
    Args:
        birth_date: The person's date of birth
        current_date: The current date
        
    Returns:
        int: Age in complete years
    """
    age = current_date.year - birth_date.year
    
    # Check if birthday has occurred this year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


def parse_date_string(date_str: str) -> tuple:
    """
    Parse and validate a date string.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        tuple: (parsed_date, error_message) - error_message is None if successful
    """
    if not date_str:
        return None, "Missing date parameter"
    
    # Validate format using regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return None, "Invalid date format. Expected YYYY-MM-DD"
    
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None, "Invalid date. Please provide a valid date"
    
    # Check if date is in the future
    current_date = date.today()
    if parsed_date > current_date:
        return None, "Date of birth cannot be in the future"
    
    return parsed_date, None


# ============================================================================
# AGE CALCULATOR FUNCTION (Restored)
# ============================================================================

@app.route(route="age", methods=["GET"])
def age_calculator(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function for age calculation.
    
    This function calculates the current age based on date of birth.
    
    Query Parameters:
        dob (str): Date of birth in YYYY-MM-DD format
        
    Returns:
        JSON response with age information
    """
    logging.info('Age calculator function processed a request.')
    
    try:
        # Get the date of birth parameter
        dob_param = req.params.get('dob')
        
        # Parse and validate the date
        parsed_date, error_message = parse_date_string(dob_param)
        if error_message:
            return func.HttpResponse(
                json.dumps({
                    "error": error_message,
                    "example": "/api/age?dob=1990-05-15"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Calculate age
        current_date = date.today()
        age_years = calculate_age_years(parsed_date, current_date)
        
        # Calculate additional age information
        age_months = (current_date.year - parsed_date.year) * 12 + (current_date.month - parsed_date.month)
        if current_date.day < parsed_date.day:
            age_months -= 1
        
        age_days = (current_date - parsed_date).days
        
        response_data = {
            "inputDob": dob_param,
            "currentDate": current_date.strftime('%Y-%m-%d'),
            "ageYears": age_years,
            "ageMonths": age_months,
            "ageDays": age_days,
            "message": f"You are {age_years} years old!"
        }
        
        logging.info(f'Successfully calculated age for {dob_param}: {age_years} years')
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in age calculator function: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Internal server error: {str(e)}",
                "example": "/api/age?dob=1990-05-15"
            }),
            status_code=500,
            mimetype="application/json"
        )


# ============================================================================
# BIRTHDAY COUNTDOWN FUNCTIONS
# ============================================================================

def is_leap_year(year: int) -> bool:
    """Check if a given year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def handle_leap_year_birthday(birth_date: date, target_year: int) -> date:
    """Handle February 29 birthdays for years that may not be leap years."""
    if birth_date.month == 2 and birth_date.day == 29:
        if is_leap_year(target_year):
            return date(target_year, 2, 29)
        else:
            return date(target_year, 2, 28)
    else:
        return date(target_year, birth_date.month, birth_date.day)


def calculate_next_birthday(birth_date: date, current_date: date) -> date:
    """Calculate the next birthday date."""
    current_year = current_date.year
    
    # Try this year first
    this_year_birthday = handle_leap_year_birthday(birth_date, current_year)
    
    if this_year_birthday >= current_date:
        return this_year_birthday
    else:
        # Birthday has passed this year, calculate for next year
        return handle_leap_year_birthday(birth_date, current_year + 1)


def generate_birthday_message(days_until: int) -> str:
    """Generate a friendly birthday message based on days until birthday."""
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


@app.route(route="nextbirthday", methods=["GET"])
def nextbirthday(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function for birthday countdown calculations.
    
    This function calculates when someone's next birthday will occur,
    including their current age, days until birthday, and handles
    leap year birthdays correctly.
    
    Query Parameters:
        dob (str): Date of birth in YYYY-MM-DD format
        
    Returns:
        JSON response with birthday information or error details
    """
    logging.info('Birthday countdown function processed a request.')
    
    try:
        # Get and validate the date of birth parameter
        dob_param = req.params.get('dob')
        
        # Parse and validate the date
        parsed_date, error_message = parse_date_string(dob_param)
        if error_message:
            return func.HttpResponse(
                json.dumps({
                    "error": error_message,
                    "example": "/api/nextbirthday?dob=1990-05-15"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Calculate birthday information
        current_date = date.today()
        
        # Calculate current age in complete years
        age_years = calculate_age_years(parsed_date, current_date)
        
        # Calculate next birthday date
        next_birthday_date = calculate_next_birthday(parsed_date, current_date)
        
        # Calculate days until next birthday
        days_until_next_birthday = (next_birthday_date - current_date).days
        
        # Get day of week for next birthday
        next_birthday_day_of_week = next_birthday_date.strftime('%A')
        
        # Generate friendly message
        message = generate_birthday_message(days_until_next_birthday)
        
        # Create success response
        response_data = {
            "inputDob": dob_param,
            "ageYears": age_years,
            "nextBirthdayDate": next_birthday_date.strftime('%Y-%m-%d'),
            "nextBirthdayDayOfWeek": next_birthday_day_of_week,
            "daysUntilNextBirthday": days_until_next_birthday,
            "message": message
        }
        
        logging.info(f'Successfully calculated birthday for {dob_param}')
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in birthday countdown function: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Internal server error: {str(e)}",
                "example": "/api/nextbirthday?dob=1990-05-15"
            }),
            status_code=500,
            mimetype="application/json"
        )