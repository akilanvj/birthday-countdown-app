import azure.functions as func
import logging
import json
from datetime import datetime, date, timedelta
import re

# Initialize the Azure Functions app using v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ============================================================================
# BIRTHDAY COUNTDOWN FUNCTIONS
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


def is_leap_year(year: int) -> bool:
    """
    Check if a given year is a leap year.
    
    Args:
        year: The year to check
        
    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def handle_leap_year_birthday(birth_date: date, target_year: int) -> date:
    """
    Handle February 29 birthdays for years that may not be leap years.
    
    Args:
        birth_date: The original birth date (February 29)
        target_year: The year to calculate the birthday for
        
    Returns:
        date: The birthday date for the target year
    """
    if birth_date.month == 2 and birth_date.day == 29:
        if is_leap_year(target_year):
            return date(target_year, 2, 29)
        else:
            return date(target_year, 2, 28)
    else:
        return date(target_year, birth_date.month, birth_date.day)


def calculate_next_birthday(birth_date: date, current_date: date) -> date:
    """
    Calculate the next birthday date.
    
    Args:
        birth_date: The person's date of birth
        current_date: The current date
        
    Returns:
        date: The next birthday date
    """
    current_year = current_date.year
    
    # Try this year first
    this_year_birthday = handle_leap_year_birthday(birth_date, current_year)
    
    if this_year_birthday >= current_date:
        return this_year_birthday
    else:
        # Birthday has passed this year, calculate for next year
        return handle_leap_year_birthday(birth_date, current_year + 1)


def calculate_days_until_birthday(current_date: date, next_birthday_date: date) -> int:
    """
    Calculate the number of days until the next birthday.
    
    Args:
        current_date: The current date
        next_birthday_date: The next birthday date
        
    Returns:
        int: Number of days until next birthday
    """
    return (next_birthday_date - current_date).days


def get_day_of_week(date_obj: date) -> str:
    """
    Get the full day name for a given date.
    
    Args:
        date_obj: The date object
        
    Returns:
        str: Full day name (e.g., "Monday")
    """
    return date_obj.strftime('%A')


def generate_birthday_message(days_until: int) -> str:
    """
    Generate a friendly birthday message based on days until birthday.
    
    Args:
        days_until: Number of days until birthday
        
    Returns:
        str: Friendly message with emoji
    """
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
    """
    Parse and validate the date of birth string.
    
    Args:
        dob_str: Date string in YYYY-MM-DD format
        
    Returns:
        tuple: (parsed_date, error_response) - error_response is None if successful
    """
    # Validate format using regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob_str):
        return None, create_error_response("Invalid date format. Expected YYYY-MM-DD")
    
    try:
        parsed_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        return None, create_error_response("Invalid date. Please provide a valid date")
    
    # Check if date is in the future
    current_date = date.today()
    if parsed_date > current_date:
        return None, create_error_response("Date of birth cannot be in the future")
    
    return parsed_date, None


def create_error_response(error_message: str) -> dict:
    """
    Create a consistent error response structure.
    
    Args:
        error_message: The error message to include
        
    Returns:
        dict: Error response dictionary
    """
    return {
        "error": error_message,
        "example": "/api/nextbirthday?dob=1990-05-15"
    }


def create_http_error_response(error_dict: dict, status_code: int = 400) -> func.HttpResponse:
    """
    Creates a consistent HTTP error response.
    
    Args:
        error_dict: Dictionary containing error information
        status_code: HTTP status code (default: 400 for validation errors)
        
    Returns:
        func.HttpResponse: HTTP response with JSON error and appropriate status
    """
    return func.HttpResponse(
        json.dumps(error_dict),
        status_code=status_code,
        mimetype="application/json"
    )


def create_success_response(
    input_dob: str,
    age_years: int,
    next_birthday_date: date,
    next_birthday_day_of_week: str,
    days_until_next_birthday: int,
    message: str
) -> dict:
    """
    Creates a consistent success response structure.
    
    Args:
        input_dob: Original input date string
        age_years: Current age in complete years
        next_birthday_date: Next birthday date
        next_birthday_day_of_week: Full day name for next birthday
        days_until_next_birthday: Days until next birthday
        message: Friendly message with emoji
        
    Returns:
        dict: Success response with all required fields
    """
    return {
        "inputDob": input_dob,
        "ageYears": age_years,
        "nextBirthdayDate": next_birthday_date.strftime('%Y-%m-%d'),
        "nextBirthdayDayOfWeek": next_birthday_day_of_week,
        "daysUntilNextBirthday": days_until_next_birthday,
        "message": message
    }


# ============================================================================
# AZURE FUNCTIONS HTTP TRIGGERS
# ============================================================================

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
        
        if not dob_param:
            error_response = create_error_response("Missing required parameter 'dob'")
            return create_http_error_response(error_response)
        
        # Parse and validate the date
        parsed_date, error_response = parse_and_validate_date(dob_param)
        if error_response:
            return create_http_error_response(error_response)
        
        # Calculate birthday information
        current_date = date.today()
        
        # Calculate current age in complete years
        age_years = calculate_age_years(parsed_date, current_date)
        
        # Calculate next birthday date
        next_birthday_date = calculate_next_birthday(parsed_date, current_date)
        
        # Calculate days until next birthday
        days_until_next_birthday = calculate_days_until_birthday(current_date, next_birthday_date)
        
        # Get day of week for next birthday
        next_birthday_day_of_week = get_day_of_week(next_birthday_date)
        
        # Generate friendly message
        message = generate_birthday_message(days_until_next_birthday)
        
        # Create success response
        response_data = create_success_response(
            dob_param,
            age_years,
            next_birthday_date,
            next_birthday_day_of_week,
            days_until_next_birthday,
            message
        )
        
        logging.info(f'Successfully calculated birthday for {dob_param}')
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in birthday countdown function: {str(e)}')
        error_response = create_error_response(f"Internal server error: {str(e)}")
        return create_http_error_response(error_response, 500)


# ============================================================================
# EXISTING AGE CALCULATOR FUNCTION (Placeholder - will be preserved)
# ============================================================================
# Note: The existing age_calculator function will be preserved during deployment
# This is just a placeholder to show the structure