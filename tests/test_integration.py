"""
Integration test for the birthday API functionality.
This test simulates HTTP requests to verify the complete flow.
"""
import json
from datetime import date
from unittest.mock import Mock
from function_app import nextbirthday


def test_api_integration():
    """Test the complete API integration with a valid request."""
    # Create a mock HTTP request
    mock_request = Mock()
    mock_request.params = {'dob': '2000-01-01'}
    
    # Call the function
    response = nextbirthday(mock_request)
    
    # Verify response status
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    
    # Parse and verify response content
    response_data = json.loads(response.get_body().decode())
    
    # Verify all required fields are present
    required_fields = [
        'inputDob', 'ageYears', 'nextBirthdayDate', 
        'nextBirthdayDayOfWeek', 'daysUntilNextBirthday', 'message'
    ]
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"
    
    # Verify field types and formats
    assert isinstance(response_data['inputDob'], str)
    assert isinstance(response_data['ageYears'], int)
    assert isinstance(response_data['nextBirthdayDate'], str)
    assert isinstance(response_data['nextBirthdayDayOfWeek'], str)
    assert isinstance(response_data['daysUntilNextBirthday'], int)
    assert isinstance(response_data['message'], str)
    
    # Verify date format
    assert len(response_data['nextBirthdayDate']) == 10  # YYYY-MM-DD format
    assert response_data['nextBirthdayDate'][4] == '-'
    assert response_data['nextBirthdayDate'][7] == '-'
    
    # Verify input DOB matches
    assert response_data['inputDob'] == '2000-01-01'
    
    # Verify age is reasonable (should be 23 or 24 depending on current date)
    current_year = date.today().year
    expected_age_range = [current_year - 2000 - 1, current_year - 2000]
    assert response_data['ageYears'] in expected_age_range
    
    # Verify days until birthday is positive
    assert response_data['daysUntilNextBirthday'] >= 0
    
    # Verify message contains emoji
    assert any(char in response_data['message'] for char in ['🎉', '🎂', '🎈'])
    
    print("✅ API integration test passed!")
    print(f"Response: {json.dumps(response_data, indent=2)}")


def test_api_error_handling():
    """Test API error handling with invalid input."""
    # Test missing parameter
    mock_request = Mock()
    mock_request.params = {}
    
    response = nextbirthday(mock_request)
    assert response.status_code == 400
    
    response_data = json.loads(response.get_body().decode())
    assert 'error' in response_data
    assert 'example' in response_data
    
    # Test invalid date format
    mock_request.params = {'dob': 'invalid-date'}
    response = nextbirthday(mock_request)
    assert response.status_code == 400
    
    # Test future date
    mock_request.params = {'dob': '2030-01-01'}
    response = nextbirthday(mock_request)
    assert response.status_code == 400
    
    print("✅ API error handling test passed!")


if __name__ == '__main__':
    test_api_integration()
    test_api_error_handling()
    print("🎉 All integration tests passed!")