import unittest
from datetime import date
from function_app import (
    calculate_age_years,
    calculate_next_birthday_date,
    calculate_days_until_birthday,
    get_day_of_week,
    generate_birthday_message,
    create_success_response
)


class TestBirthdayCalculator(unittest.TestCase):
    """Unit tests for birthday calculator functions."""
    
    def test_calculate_age_years_basic(self):
        """Test basic age calculation."""
        # Test case: Born 2000-01-01, current date 2023-06-15
        birth_date = date(2000, 1, 1)
        current_date = date(2023, 6, 15)
        age = calculate_age_years(birth_date, current_date)
        self.assertEqual(age, 23)
    
    def test_calculate_age_years_birthday_not_yet(self):
        """Test age calculation when birthday hasn't occurred this year."""
        # Test case: Born 2000-12-25, current date 2023-06-15
        birth_date = date(2000, 12, 25)
        current_date = date(2023, 6, 15)
        age = calculate_age_years(birth_date, current_date)
        self.assertEqual(age, 22)  # Birthday hasn't happened yet this year
    
    def test_calculate_age_years_birthday_today(self):
        """Test age calculation when today is the birthday."""
        # Test case: Born 2000-06-15, current date 2023-06-15
        birth_date = date(2000, 6, 15)
        current_date = date(2023, 6, 15)
        age = calculate_age_years(birth_date, current_date)
        self.assertEqual(age, 23)
    
    def test_calculate_next_birthday_date_future_this_year(self):
        """Test next birthday calculation when birthday is later this year."""
        # Test case: Born 2000-12-25, current date 2023-06-15
        birth_date = date(2000, 12, 25)
        current_date = date(2023, 6, 15)
        next_birthday = calculate_next_birthday_date(birth_date, current_date)
        self.assertEqual(next_birthday, date(2023, 12, 25))
    
    def test_calculate_next_birthday_date_past_this_year(self):
        """Test next birthday calculation when birthday already passed this year."""
        # Test case: Born 2000-01-01, current date 2023-06-15
        birth_date = date(2000, 1, 1)
        current_date = date(2023, 6, 15)
        next_birthday = calculate_next_birthday_date(birth_date, current_date)
        self.assertEqual(next_birthday, date(2024, 1, 1))
    
    def test_calculate_next_birthday_date_today(self):
        """Test next birthday calculation when today is the birthday."""
        # Test case: Born 2000-06-15, current date 2023-06-15
        birth_date = date(2000, 6, 15)
        current_date = date(2023, 6, 15)
        next_birthday = calculate_next_birthday_date(birth_date, current_date)
        self.assertEqual(next_birthday, date(2023, 6, 15))  # Today since it's the birthday
    
    def test_calculate_days_until_birthday(self):
        """Test days until birthday calculation."""
        current_date = date(2023, 6, 15)
        next_birthday = date(2023, 12, 25)
        days_until = calculate_days_until_birthday(current_date, next_birthday)
        # From June 15 to December 25, 2023
        expected_days = (next_birthday - current_date).days
        self.assertEqual(days_until, expected_days)
        self.assertEqual(days_until, 193)  # Verified calculation
    
    def test_calculate_days_until_birthday_zero(self):
        """Test days until birthday when today is birthday."""
        current_date = date(2023, 6, 15)
        next_birthday = date(2023, 6, 15)  # Today is the birthday
        days_until = calculate_days_until_birthday(current_date, next_birthday)
        expected_days = 0  # Today is the birthday
        self.assertEqual(days_until, expected_days)
    
    def test_get_day_of_week(self):
        """Test day of week determination."""
        # June 15, 2023 is a Thursday
        test_date = date(2023, 6, 15)
        day_name = get_day_of_week(test_date)
        self.assertEqual(day_name, "Thursday")
        
        # December 25, 2023 is a Monday
        test_date = date(2023, 12, 25)
        day_name = get_day_of_week(test_date)
        self.assertEqual(day_name, "Monday")
    
    def test_generate_birthday_message_today(self):
        """Test message generation for birthday today."""
        message = generate_birthday_message(0)
        self.assertIn("Happy Birthday", message)
        self.assertIn("🎉", message)
    
    def test_generate_birthday_message_tomorrow(self):
        """Test message generation for birthday tomorrow."""
        message = generate_birthday_message(1)
        self.assertIn("tomorrow", message)
        self.assertIn("🎂", message)
    
    def test_generate_birthday_message_future(self):
        """Test message generation for future birthday."""
        message = generate_birthday_message(30)
        self.assertIn("30 days", message)
        self.assertIn("🎈", message)
    
    def test_create_success_response(self):
        """Test success response creation."""
        response = create_success_response(
            input_dob="2000-01-01",
            age_years=23,
            next_birthday_date=date(2024, 1, 1),
            next_birthday_day_of_week="Monday",
            days_until_next_birthday=200,
            message="🎈 Your birthday is in 200 days! Time to start planning the celebration!"
        )
        
        expected_response = {
            "inputDob": "2000-01-01",
            "ageYears": 23,
            "nextBirthdayDate": "2024-01-01",
            "nextBirthdayDayOfWeek": "Monday",
            "daysUntilNextBirthday": 200,
            "message": "🎈 Your birthday is in 200 days! Time to start planning the celebration!"
        }
        
        self.assertEqual(response, expected_response)


if __name__ == '__main__':
    unittest.main()

class TestLeapYearHandling(unittest.TestCase):
    """Unit tests for leap year handling functions."""
    
    def test_is_leap_year(self):
        """Test leap year detection."""
        from function_app import is_leap_year
        
        # Test leap years
        self.assertTrue(is_leap_year(2000))  # Divisible by 400
        self.assertTrue(is_leap_year(2004))  # Divisible by 4, not by 100
        self.assertTrue(is_leap_year(2020))  # Divisible by 4, not by 100
        self.assertTrue(is_leap_year(2024))  # Divisible by 4, not by 100
        
        # Test non-leap years
        self.assertFalse(is_leap_year(1900))  # Divisible by 100, not by 400
        self.assertFalse(is_leap_year(2001))  # Not divisible by 4
        self.assertFalse(is_leap_year(2023))  # Not divisible by 4
        self.assertFalse(is_leap_year(2100))  # Divisible by 100, not by 400
    
    def test_handle_leap_year_birthday_regular_date(self):
        """Test leap year handler with regular (non-Feb 29) birthdays."""
        from function_app import handle_leap_year_birthday
        
        birth_date = date(2000, 6, 15)  # Regular birthday
        
        # Should work the same for leap and non-leap years
        result_leap = handle_leap_year_birthday(birth_date, 2024)
        result_non_leap = handle_leap_year_birthday(birth_date, 2023)
        
        self.assertEqual(result_leap, date(2024, 6, 15))
        self.assertEqual(result_non_leap, date(2023, 6, 15))
    
    def test_handle_leap_year_birthday_feb_29_leap_year(self):
        """Test leap year handler with Feb 29 birthday in leap year."""
        from function_app import handle_leap_year_birthday
        
        birth_date = date(2000, 2, 29)  # Leap day birthday
        
        # In leap year, should use Feb 29
        result = handle_leap_year_birthday(birth_date, 2024)
        self.assertEqual(result, date(2024, 2, 29))
    
    def test_handle_leap_year_birthday_feb_29_non_leap_year(self):
        """Test leap year handler with Feb 29 birthday in non-leap year."""
        from function_app import handle_leap_year_birthday
        
        birth_date = date(2000, 2, 29)  # Leap day birthday
        
        # In non-leap year, should use Feb 28
        result = handle_leap_year_birthday(birth_date, 2023)
        self.assertEqual(result, date(2023, 2, 28))
    
    def test_calculate_next_birthday_date_leap_day(self):
        """Test next birthday calculation for Feb 29 birthdays."""
        birth_date = date(2000, 2, 29)  # Leap day birthday
        
        # Test in non-leap year (2023)
        current_date = date(2023, 1, 15)
        next_birthday = calculate_next_birthday_date(birth_date, current_date)
        self.assertEqual(next_birthday, date(2023, 2, 28))  # Should use Feb 28
        
        # Test in leap year (2024)
        current_date = date(2024, 1, 15)
        next_birthday = calculate_next_birthday_date(birth_date, current_date)
        self.assertEqual(next_birthday, date(2024, 2, 29))  # Should use Feb 29