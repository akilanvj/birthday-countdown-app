"""
Edge case tests for birthday calculator functionality.
"""
import json
from unittest.mock import Mock, patch
from datetime import date
from function_app import nextbirthday


def test_birthday_today():
    """Test when today is the person's birthday."""
    # Mock today's date to be a specific date
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2023, 6, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '2000-06-15'}  # Birthday is today
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        # Today is the birthday, so next birthday is today (0 days)
        assert response_data['nextBirthdayDate'] == '2023-06-15'
        assert response_data['daysUntilNextBirthday'] == 0
        assert '🎉' in response_data['message']  # Should have birthday emoji
        assert 'Happy Birthday' in response_data['message']
        
        print("✅ Birthday today test passed!")


def test_birthday_tomorrow():
    """Test when birthday is tomorrow."""
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2023, 6, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '2000-06-15'}  # Birthday is tomorrow
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        assert response_data['nextBirthdayDate'] == '2023-06-15'
        assert response_data['daysUntilNextBirthday'] == 1
        assert '🎂' in response_data['message']
        assert 'tomorrow' in response_data['message']
        
        print("✅ Birthday tomorrow test passed!")


def test_new_years_birthday():
    """Test New Year's Day birthday."""
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2023, 6, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '1990-01-01'}  # New Year's Day birthday
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        assert response_data['ageYears'] == 33
        assert response_data['nextBirthdayDate'] == '2024-01-01'
        assert response_data['nextBirthdayDayOfWeek'] == 'Monday'
        
        print("✅ New Year's birthday test passed!")


def test_leap_day_birthday_non_leap_year():
    """Test February 29 birthday in a non-leap year (should use Feb 28)."""
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2023, 1, 15)  # 2023 is not a leap year
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '2000-02-29'}  # Leap day birthday
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        # In 2023 (non-leap year), should use February 28
        assert response_data['nextBirthdayDate'] == '2023-02-28'
        
        print("✅ Leap day birthday in non-leap year test passed!")


def test_leap_day_birthday_leap_year():
    """Test February 29 birthday in a leap year (should use Feb 29)."""
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2024, 1, 15)  # 2024 is a leap year
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '2000-02-29'}  # Leap day birthday
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        # In 2024 (leap year), should use February 29
        assert response_data['nextBirthdayDate'] == '2024-02-29'
        
        print("✅ Leap day birthday in leap year test passed!")


def test_very_old_person():
    """Test with a very old person's birthday."""
    with patch('function_app.date') as mock_date:
        mock_date.today.return_value = date(2023, 6, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        mock_request = Mock()
        mock_request.params = {'dob': '1920-12-25'}  # Born in 1920
        
        response = nextbirthday(mock_request)
        response_data = json.loads(response.get_body().decode())
        
        assert response_data['ageYears'] == 102
        assert response_data['nextBirthdayDate'] == '2023-12-25'
        assert response_data['nextBirthdayDayOfWeek'] == 'Monday'
        
        print("✅ Very old person test passed!")


if __name__ == '__main__':
    test_birthday_today()
    test_birthday_tomorrow()
    test_new_years_birthday()
    test_leap_day_birthday_non_leap_year()
    test_leap_day_birthday_leap_year()
    test_very_old_person()
    print("🎉 All edge case tests passed!")