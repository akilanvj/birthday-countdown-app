import azure.functions as func
import logging
import json
from datetime import datetime, date, timedelta
import re
import os

# Application Insights integration
try:
    from applicationinsights import TelemetryClient
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    
    # Get Application Insights connection string from environment
    connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    instrumentation_key = os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY')
    
    if connection_string or instrumentation_key:
        # Configure Application Insights logging
        if connection_string:
            logger = logging.getLogger(__name__)
            logger.addHandler(AzureLogHandler(connection_string=connection_string))
            logger.setLevel(logging.INFO)
            
            # Create telemetry client for custom events
            tc = TelemetryClient(instrumentation_key=instrumentation_key or connection_string.split('InstrumentationKey=')[1].split(';')[0])
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            tc = None
            
        logger.info("🎂 Application Insights configured successfully")
    else:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        tc = None
        logger.warning("⚠️ Application Insights not configured - no connection string found")
        
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    tc = None
    logger.warning(f"⚠️ Application Insights dependencies not available: {e}")

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)

# Initialize the Azure Functions app using v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Add CORS headers for all responses
def add_cors_headers(response: func.HttpResponse) -> func.HttpResponse:
    """Add CORS headers to allow frontend access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Custom logging function that sends to both console and Application Insights
def log_custom_event(event_name: str, properties: dict = None, measurements: dict = None):
    """Log custom events to Application Insights"""
    if tc:
        tc.track_event(event_name, properties, measurements)
        tc.flush()
    
    # Also log to console for immediate debugging
    logger.info(f"🎂 CUSTOM EVENT: {event_name} | Properties: {properties} | Measurements: {measurements}")

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
    Supports both YYYY-MM-DD and DD/MM/YYYY formats.
    
    Args:
        date_str: Date string in YYYY-MM-DD or DD/MM/YYYY format
        
    Returns:
        tuple: (parsed_date, error_message) - error_message is None if successful
    """
    if not date_str:
        return None, "Missing date parameter"
    
    parsed_date = None
    
    # Try YYYY-MM-DD format first (ISO format)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, "Invalid date. Please provide a valid date in YYYY-MM-DD format"
    
    # Try DD/MM/YYYY format (European/UK format)
    elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
        try:
            parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return None, "Invalid date. Please provide a valid date in DD/MM/YYYY format"
    
    # Try DD-MM-YYYY format (alternative European format)
    elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
        try:
            parsed_date = datetime.strptime(date_str, '%d-%m-%Y').date()
        except ValueError:
            return None, "Invalid date. Please provide a valid date in DD-MM-YYYY format"
    
    else:
        return None, "Invalid date format. Expected DD/MM/YYYY or YYYY-MM-DD format"
    
    # Check if date is in the future
    current_date = date.today()
    if parsed_date > current_date:
        return None, "Date of birth cannot be in the future"
    
    # Check if date is not too far in the past (reasonable validation)
    min_year = current_date.year - 150
    if parsed_date.year < min_year:
        return None, f"Please enter a date after {min_year}"
    
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


@app.route(route="nextbirthday", methods=["GET", "OPTIONS"])
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
    # Enhanced logging for debugging
    logger.info('🎂 ===== BIRTHDAY COUNTDOWN FUNCTION STARTED =====')
    logger.info(f'🎂 Request method: {req.method}')
    logger.info(f'🎂 Request URL: {req.url}')
    logger.info(f'🎂 Request headers: {dict(req.headers)}')
    logger.info(f'🎂 Request params: {dict(req.params)}')
    logger.info(f'🎂 Timestamp: {datetime.now().isoformat()}')
    
    # Log custom event to Application Insights
    log_custom_event('BirthdayCalculationStarted', {
        'method': req.method,
        'url': str(req.url),
        'user_agent': req.headers.get('User-Agent', 'Unknown'),
        'timestamp': datetime.now().isoformat()
    })
    
    # Handle CORS preflight requests
    if req.method == "OPTIONS":
        logger.info('🎂 Handling CORS preflight request')
        log_custom_event('CORSPreflightHandled')
        response = func.HttpResponse("", status_code=200)
        return add_cors_headers(response)
    
    try:
        # Get and validate the date of birth parameter
        dob_param = req.params.get('dob')
        logger.info(f'🎂 DOB parameter received: {dob_param}')
        
        # Parse and validate the date
        parsed_date, error_message = parse_date_string(dob_param)
        if error_message:
            logger.warning(f'🎂 Date validation failed: {error_message}')
            log_custom_event('ValidationError', {
                'error': error_message,
                'dob_param': dob_param
            })
            
            response = func.HttpResponse(
                json.dumps({
                    "error": error_message,
                    "example": "/api/nextbirthday?dob=12/06/2000 or /api/nextbirthday?dob=1990-05-15",
                    "received": dob_param,
                    "timestamp": datetime.now().isoformat(),
                    "source": "Azure Functions",
                    "version": "2.3"
                }),
                status_code=400,
                mimetype="application/json"
            )
            return add_cors_headers(response)
        
        logger.info(f'🎂 Date parsed successfully: {parsed_date}')
        
        # Calculate birthday information
        current_date = date.today()
        logger.info(f'🎂 Current date: {current_date}')
        
        # Calculate current age in complete years
        age_years = calculate_age_years(parsed_date, current_date)
        logger.info(f'🎂 Age calculated: {age_years} years')
        
        # Calculate next birthday date
        next_birthday_date = calculate_next_birthday(parsed_date, current_date)
        logger.info(f'🎂 Next birthday date: {next_birthday_date}')
        
        # Calculate days until next birthday
        days_until_next_birthday = (next_birthday_date - current_date).days
        logger.info(f'🎂 Days until next birthday: {days_until_next_birthday}')
        
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
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "debug": {
                "parsedDate": parsed_date.strftime('%Y-%m-%d'),
                "currentDate": current_date.strftime('%Y-%m-%d'),
                "environment": "Azure Functions",
                "version": "2.3",
                "applicationInsights": "enabled" if tc else "disabled"
            }
        }
        
        logger.info(f'🎂 Successfully calculated birthday for {dob_param}')
        logger.info(f'🎂 Response data: {json.dumps(response_data, indent=2)}')
        
        # Log success event to Application Insights
        log_custom_event('BirthdayCalculationSuccess', {
            'dob': dob_param,
            'age_years': age_years,
            'days_until_birthday': days_until_next_birthday
        }, {
            'age_years': age_years,
            'days_until_birthday': days_until_next_birthday
        })
        
        response = func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
        logger.info('🎂 ===== BIRTHDAY COUNTDOWN FUNCTION COMPLETED SUCCESSFULLY =====')
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f'🎂 CRITICAL ERROR in birthday countdown function: {str(e)}', exc_info=True)
        logger.error(f'🎂 Error type: {type(e).__name__}')
        logger.error(f'🎂 Error args: {e.args}')
        
        # Log error event to Application Insights
        log_custom_event('BirthdayCalculationError', {
            'error': str(e),
            'error_type': type(e).__name__,
            'dob_param': req.params.get('dob', 'None'),
            'request_url': str(req.url)
        })
        
        response = func.HttpResponse(
            json.dumps({
                "error": f"Internal server error: {str(e)}",
                "errorType": type(e).__name__,
                "example": "/api/nextbirthday?dob=12/06/2000 or /api/nextbirthday?dob=1990-05-15",
                "timestamp": datetime.now().isoformat(),
                "debug": {
                    "environment": "Azure Functions",
                    "version": "2.3",
                    "requestMethod": req.method,
                    "requestUrl": str(req.url),
                    "applicationInsights": "enabled" if tc else "disabled"
                }
            }),
            status_code=500,
            mimetype="application/json"
        )
        
        logger.error('🎂 ===== BIRTHDAY COUNTDOWN FUNCTION COMPLETED WITH ERROR =====')
        return add_cors_headers(response)