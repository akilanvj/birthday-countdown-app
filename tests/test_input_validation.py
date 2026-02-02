import unittest
from unittest.mock import Mock
from datetime import date, datetime, timedelta
import json
from function_app import validate_dob_parameter, nextbirthday, create_error_response, create_http_error_response
import azure.functions as func


class TestErrorResponseFormatter(unittest.TestCase):
    """Unit tests for error response formatting functions."""
    
    def test_create_error_response_structure(self):
        """Test that create_error_response returns correct structure."""
        # Arrange
        error_message = "Test error message"
        
        # Act
        error_response = create_error_response(error_message)
        
        # Assert
        self.assertIsInstance(error_response, dict)
        self.assertEqual(len(error_response), 2)  # Should have exactly 2 fields
        self.assertIn("error", error_response)
        self.assertIn("example", error_response)
        self.assertEqual(error_response["error"], error_message)
        self.assertEqual(error_response["example"], "/api/nextbirthday?dob=2002-08-14")
    
    def test_create_error_response_different_messages(self):
        """Test create_error_response with different error messages."""
        test_messages = [
            "Missing required parameter 'dob'",
            "Invalid date format. Expected YYYY-MM-DD",
            "Date of birth cannot be in the future"
        ]
        
        for message in test_messages:
            with self.subTest(message=message):
                # Act
                error_response = create_error_response(message)
                
                # Assert
                self.assertEqual(error_response["error"], message)
                self.assertEqual(error_response["example"], "/api/nextbirthday?dob=2002-08-14")
    
    def test_create_http_error_response_default_status(self):
        """Test create_http_error_response with default status code."""
        # Arrange
        error_dict = {"error": "Test error", "example": "/api/nextbirthday?dob=2002-08-14"}
        
        # Act
        response = create_http_error_response(error_dict)
        
        # Assert
        self.assertIsInstance(response, func.HttpResponse)
        self.assertEqual(response.status_code, 400)  # Default should be 400
        self.assertEqual(response.mimetype, "application/json")
        
        # Verify JSON content
        response_data = json.loads(response.get_body().decode())
        self.assertEqual(response_data, error_dict)
    
    def test_create_http_error_response_custom_status(self):
        """Test create_http_error_response with custom status code."""
        # Arrange
        error_dict = {"error": "Server error", "example": "/api/nextbirthday?dob=2002-08-14"}
        custom_status = 500
        
        # Act
        response = create_http_error_response(error_dict, custom_status)
        
        # Assert
        self.assertEqual(response.status_code, custom_status)
        self.assertEqual(response.mimetype, "application/json")
        
        # Verify JSON content
        response_data = json.loads(response.get_body().decode())
        self.assertEqual(response_data, error_dict)


class TestInputValidation(unittest.TestCase):
    """Unit tests for DOB parameter input validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_request = Mock(spec=func.HttpRequest)
    
    def test_missing_dob_parameter(self):
        """Test validation when DOB parameter is missing."""
        # Arrange
        self.mock_request.params.get.return_value = None
        
        # Act
        parsed_date, error = validate_dob_parameter(self.mock_request)
        
        # Assert
        self.assertIsNone(parsed_date)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "Missing required parameter 'dob'")
        self.assertIn("example", error)
    
    def test_empty_dob_parameter(self):
        """Test validation when DOB parameter is empty string."""
        # Arrange
        self.mock_request.params.get.return_value = ""
        
        # Act
        parsed_date, error = validate_dob_parameter(self.mock_request)
        
        # Assert
        self.assertIsNone(parsed_date)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "Missing required parameter 'dob'")
    
    def test_invalid_date_format_wrong_pattern(self):
        """Test validation with invalid date format patterns."""
        invalid_formats = [
            "2002/08/14",  # Wrong separators
            "08-14-2002",  # Wrong order
            "2002-8-14",   # Missing leading zeros
            "02-08-14",    # Two-digit year
            "2002-08",     # Missing day
            "not-a-date",  # Non-date string
            "2002-13-01",  # Invalid month
            "2002-02-30",  # Invalid day for February
        ]
        
        for invalid_format in invalid_formats:
            with self.subTest(format=invalid_format):
                # Arrange
                self.mock_request.params.get.return_value = invalid_format
                
                # Act
                parsed_date, error = validate_dob_parameter(self.mock_request)
                
                # Assert
                self.assertIsNone(parsed_date)
                self.assertIsNotNone(error)
                self.assertEqual(error["error"], "Invalid date format. Expected YYYY-MM-DD")
    
    def test_future_date_validation(self):
        """Test validation when DOB is in the future."""
        # Arrange - use tomorrow's date
        tomorrow = date.today() + timedelta(days=1)
        future_date_str = tomorrow.strftime('%Y-%m-%d')
        self.mock_request.params.get.return_value = future_date_str
        
        # Act
        parsed_date, error = validate_dob_parameter(self.mock_request)
        
        # Assert
        self.assertIsNone(parsed_date)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "Date of birth cannot be in the future")
    
    def test_valid_dob_parameter(self):
        """Test validation with valid DOB parameters."""
        valid_dates = [
            "2002-08-14",  # Standard date
            "1990-01-01",  # New Year's Day
            "1985-12-31",  # New Year's Eve
            "2000-02-29",  # Leap year February 29
        ]
        
        for valid_date_str in valid_dates:
            with self.subTest(date=valid_date_str):
                # Arrange
                self.mock_request.params.get.return_value = valid_date_str
                
                # Act
                parsed_date, error = validate_dob_parameter(self.mock_request)
                
                # Assert
                self.assertIsNotNone(parsed_date)
                self.assertIsNone(error)
                self.assertEqual(parsed_date, datetime.strptime(valid_date_str, '%Y-%m-%d').date())
    
    def test_today_as_dob(self):
        """Test validation when DOB is today (edge case)."""
        # Arrange
        today_str = date.today().strftime('%Y-%m-%d')
        self.mock_request.params.get.return_value = today_str
        
        # Act
        parsed_date, error = validate_dob_parameter(self.mock_request)
        
        # Assert
        self.assertIsNotNone(parsed_date)
        self.assertIsNone(error)
        self.assertEqual(parsed_date, date.today())


class TestHTTPEndpointValidation(unittest.TestCase):
    """Integration tests for the HTTP endpoint validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_request = Mock(spec=func.HttpRequest)
    
    def test_endpoint_returns_400_for_missing_dob(self):
        """Test that the endpoint returns HTTP 400 for missing DOB."""
        # Arrange
        self.mock_request.params.get.return_value = None
        
        # Act
        response = nextbirthday(self.mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        
        # Parse and validate JSON response
        response_data = json.loads(response.get_body().decode())
        self.assertIn("error", response_data)
        self.assertIn("example", response_data)
    
    def test_endpoint_returns_400_for_invalid_format(self):
        """Test that the endpoint returns HTTP 400 for invalid date format."""
        # Arrange
        self.mock_request.params.get.return_value = "invalid-date"
        
        # Act
        response = nextbirthday(self.mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        
        # Parse and validate JSON response
        response_data = json.loads(response.get_body().decode())
        self.assertEqual(response_data["error"], "Invalid date format. Expected YYYY-MM-DD")
    
    def test_endpoint_returns_400_for_future_date(self):
        """Test that the endpoint returns HTTP 400 for future date."""
        # Arrange
        tomorrow = date.today() + timedelta(days=1)
        future_date_str = tomorrow.strftime('%Y-%m-%d')
        self.mock_request.params.get.return_value = future_date_str
        
        # Act
        response = nextbirthday(self.mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        
        # Parse and validate JSON response
        response_data = json.loads(response.get_body().decode())
        self.assertEqual(response_data["error"], "Date of birth cannot be in the future")
    
    def test_endpoint_returns_200_for_valid_dob(self):
        """Test that the endpoint returns HTTP 200 for valid DOB."""
        # Arrange
        self.mock_request.params.get.return_value = "2002-08-14"
        
        # Act
        response = nextbirthday(self.mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        # Response body should contain the birthday calculation results
        response_body = response.get_body().decode()
        response_data = json.loads(response_body)
        
        # Verify all required fields are present
        required_fields = [
            'inputDob', 'ageYears', 'nextBirthdayDate', 
            'nextBirthdayDayOfWeek', 'daysUntilNextBirthday', 'message'
        ]
        for field in required_fields:
            self.assertIn(field, response_data)
        
        # Verify the input DOB is preserved
        self.assertEqual(response_data['inputDob'], "2002-08-14")


if __name__ == '__main__':
    unittest.main()