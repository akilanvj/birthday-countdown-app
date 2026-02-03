#!/usr/bin/env python3
"""
Test script to verify Application Insights is working
"""

import requests
import time
import json

# Your Function App URL
FUNCTION_URL = "https://funchttptrigger1-fvbnfye7bac5bgd5.eastus-01.azurewebsites.net/api/nextbirthday"

def test_api_call():
    """Test the API and generate logs"""
    print("🎂 Testing Birthday Countdown API...")
    print(f"🔗 URL: {FUNCTION_URL}")
    
    # Test data
    test_cases = [
        "1990-05-15",  # Valid date
        "2000-12-25",  # Valid date
        "invalid-date",  # Invalid date to test error logging
        "2030-01-01"   # Future date to test validation
    ]
    
    for i, dob in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: DOB = {dob} ---")
        
        try:
            response = requests.get(f"{FUNCTION_URL}?dob={dob}", timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
            except:
                print(f"Raw Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait between requests to see logs clearly
        time.sleep(2)
    
    print("\n🎯 Test completed! Check Application Insights for logs:")
    print("1. Go to Azure Portal")
    print("2. Navigate to 'birthday-countdown-insights' Application Insights")
    print("3. Click 'Logs' in the left menu")
    print("4. Run this query:")
    print("""
    traces
    | where timestamp > ago(10m)
    | where message contains "🎂"
    | order by timestamp desc
    """)

if __name__ == "__main__":
    test_api_call()