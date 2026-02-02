import azure.functions as func
import logging
import json
from datetime import datetime, date, timedelta
import re

# Initialize the Azure Functions app using v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def calculate_age_years(birth_date: date, current_date: date) -> int:
    """
    Calculate the current age in complete years.
    
    Args:
        birth_date: The person's date of birth
        current_date: The current date
        
    Returns:
        int: Age in complete years
        
    Requirements: 3.1
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
        
    Requirements: 4.1
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def handle_leap_year_birthday(birth_date: date, target_year: int) -> date:
    """
    Handle February 29 birthdays for years that may not be leap years.
    
    Args:
        birth_date: The person's date of birth
        target_year: The year to calculate the birthday for
        
    Returns:
        date: The birthday date, using Feb 28 if target year is not leap year
        
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    if birth_date.month == 2 and birth_date.day == 29:
        # Person was born on February 29
        if is_leap_year(target_year):
            # Target year is leap year, use February 29
            return date(target_year, 2, 29)
        else:
            # Target year is not leap year, use February 28
            return date(target_year, 2, 28)
    else:
        # Regular birthday, no special handling needed
        return date(target_year, birth_date.month, birth_date.day)


def calculate_next_birthday_date(birth_date: date, current_date: date) -> date:
    """
    Calculate the next occurrence of the birthday.
    
    Args:
        birth_date: The person's date of birth
        current_date: The current date
        
    Returns:
        date: The next birthday date
        
    Requirements: 3.2
    """
    # Start with this year's birthday, handling leap year cases
    next_birthday = handle_leap_year_birthday(birth_date, current_date.year)
    
    # If this year's birthday has already passed, use next year
    if next_birthday < current_date:
        next_birthday = handle_leap_year_birthday(birth_date, current_date.year + 1)
    
    return next_birthday


def calculate_days_until_birthday(current_date: date, next_birthday_date: date) -> int:
    """
    Calculate the number of days until the next birthday.
    
    Args:
        current_date: The current date
        next_birthday_date: The next birthday date
        
    Returns:
        int: Number of calendar days until next birthday
        
    Requirements: 3.3
    """
    delta = next_birthday_date - current_date
    return delta.days


def get_day_of_week(target_date: date) -> str:
    """
    Get the full day name for a given date.
    
    Args:
        target_date: The date to get the day of week for
        
    Returns:
        str: Full day name (e.g., "Friday")
        
    Requirements: 3.4
    """
    return target_date.strftime("%A")


def generate_birthday_message(days_until: int) -> str:
    """
    Generate a friendly message with emoji indicating days until birthday.
    
    Args:
        days_until: Number of days until next birthday
        
    Returns:
        str: Friendly message with emoji
        
    Requirements: 3.5, 5.5
    """
    if days_until == 0:
        return "🎉 Happy Birthday! Today is your special day!"
    elif days_until == 1:
        return "🎂 Your birthday is tomorrow! Get ready to celebrate!"
    else:
        return f"🎈 Your birthday is in {days_until} days! Time to start planning the celebration!"


def create_error_response(error_message: str) -> dict:
    """
    Creates a consistent error response structure.
    
    Args:
        error_message: Human-readable error message
        
    Returns:
        dict: Error response with 'error' and 'example' fields
        
    Requirements: 6.1, 6.3, 6.4, 6.5
    """
    return {
        "error": error_message,
        "example": "/api/nextbirthday?dob=2002-08-14"
    }


def validate_dob_parameter(req: func.HttpRequest) -> tuple[date, dict]:
    """
    Validates the DOB parameter from the HTTP request.
    
    Args:
        req: The HTTP request object
        
    Returns:
        tuple: (parsed_date, error_response) where error_response is None if valid
        
    Validation Rules:
        - DOB parameter must be present
        - DOB must be in ISO YYYY-MM-DD format
        - DOB must not be in the future
    """
    # Check if DOB parameter is missing
    dob_param = req.params.get('dob')
    if not dob_param:
        return None, create_error_response("Missing required parameter 'dob'")
    
    # Validate ISO YYYY-MM-DD format using regex
    iso_date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(iso_date_pattern, dob_param):
        return None, create_error_response("Invalid date format. Expected YYYY-MM-DD")
    
    # Parse the date to ensure it's a valid date
    try:
        parsed_date = datetime.strptime(dob_param, '%Y-%m-%d').date()
    except ValueError:
        return None, create_error_response("Invalid date format. Expected YYYY-MM-DD")
    
    # Check if the date is in the future
    current_date = date.today()
    if parsed_date > current_date:
        return None, create_error_response("Date of birth cannot be in the future")
    
    return parsed_date, None


def create_http_error_response(error_dict: dict, status_code: int = 400) -> func.HttpResponse:
    """
    Creates a consistent HTTP error response.
    
    Args:
        error_dict: Dictionary containing error information
        status_code: HTTP status code (default: 400 for validation errors)
        
    Returns:
        func.HttpResponse: HTTP response with JSON error and appropriate status
        
    Requirements: 6.4, 6.5
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
        
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    return {
        "inputDob": input_dob,
        "ageYears": age_years,
        "nextBirthdayDate": next_birthday_date.strftime("%Y-%m-%d"),
        "nextBirthdayDayOfWeek": next_birthday_day_of_week,
        "daysUntilNextBirthday": days_until_next_birthday,
        "message": message
    }


@app.route(route="nextbirthday", methods=["GET"])
def nextbirthday(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function for birthday countdown calculations.
    
    This function handles:
    - Input validation for DOB parameter
    - Birthday calculation logic
    - Leap year handling
    - JSON response formatting
    
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    logging.info('NextBirthdayCountdown HTTP trigger function processed a request.')
    
    # Validate DOB parameter
    parsed_dob, validation_error = validate_dob_parameter(req)
    if validation_error:
        return create_http_error_response(validation_error)
    
    # Get current date for calculations
    current_date = date.today()
    
    # Perform birthday calculations
    age_years = calculate_age_years(parsed_dob, current_date)
    next_birthday_date = calculate_next_birthday_date(parsed_dob, current_date)
    days_until = calculate_days_until_birthday(current_date, next_birthday_date)
    day_of_week = get_day_of_week(next_birthday_date)
    message = generate_birthday_message(days_until)
    
    # Create success response
    response_data = create_success_response(
        input_dob=req.params.get('dob'),
        age_years=age_years,
        next_birthday_date=next_birthday_date,
        next_birthday_day_of_week=day_of_week,
        days_until_next_birthday=days_until,
        message=message
    )
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )