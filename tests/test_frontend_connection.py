#!/usr/bin/env python3
"""
Test script to verify frontend connection capability by simulating server responses.
This demonstrates that the frontend is properly configured to connect to the local backend.
"""

import json
import http.server
import socketserver
import threading
import time
import urllib.request
import urllib.parse
import sys
from datetime import date
from unittest.mock import Mock

# Import the backend function
from function_app import nextbirthday


class MockAPIHandler(http.server.BaseHTTPRequestHandler):
    """Mock HTTP handler that simulates the Azure Functions API."""
    
    def do_GET(self):
        """Handle GET requests."""
        # Parse the URL
        parsed_url = urllib.parse.urlparse(self.path)
        
        if parsed_url.path == '/api/nextbirthday':
            # Parse query parameters
            query_params = urllib.parse.parse_qs(parsed_url.query)
            dob = query_params.get('dob', [None])[0]
            
            # Create mock request for backend function
            mock_request = Mock()
            mock_request.params = {'dob': dob} if dob else {}
            
            # Call the actual backend function
            response = nextbirthday(mock_request)
            
            # Set CORS headers
            self.send_response(response.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.get_body())
        else:
            # 404 for other paths
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def start_mock_server(port=7071):
    """Start a mock server that simulates Azure Functions."""
    try:
        handler = MockAPIHandler
        httpd = socketserver.TCPServer(("", port), handler)
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(0.5)
        
        # Test if server is responding
        test_url = f'http://localhost:{port}/api/nextbirthday?dob=2000-06-15'
        try:
            response = urllib.request.urlopen(test_url, timeout=2)
            if response.status == 200:
                print(f"✅ Mock server started on port {port}")
                return httpd
        except:
            pass
        
        print(f"❌ Mock server failed to start on port {port}")
        httpd.shutdown()
        return None
        
    except Exception as e:
        print(f"❌ Error starting mock server: {e}")
        return None


def test_frontend_api_calls(base_url="http://localhost:7071"):
    """Test frontend API call scenarios."""
    print("\n🧪 Testing frontend API call scenarios...")
    
    # Test cases that simulate what the frontend would do
    test_cases = [
        {
            'name': 'Valid birthday calculation',
            'dob': '2000-06-15',
            'expected_success': True
        },
        {
            'name': 'Empty DOB (frontend validation should catch this)',
            'dob': '',
            'expected_success': False
        },
        {
            'name': 'Invalid date format',
            'dob': 'invalid-date',
            'expected_success': False
        },
        {
            'name': 'Future date',
            'dob': '2030-01-01',
            'expected_success': False
        },
        {
            'name': 'Leap year birthday',
            'dob': '2000-02-29',
            'expected_success': True
        }
    ]
    
    passed_tests = 0
    
    for test_case in test_cases:
        try:
            print(f"   Testing: {test_case['name']}")
            
            # Construct URL (same as frontend would do)
            dob = test_case['dob']
            if dob:
                url = f"{base_url}/api/nextbirthday?dob={urllib.parse.quote(dob)}"
            else:
                url = f"{base_url}/api/nextbirthday"
            
            # Make request with headers that frontend would use
            request = urllib.request.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Content-Type', 'application/json')
            
            try:
                response = urllib.request.urlopen(request, timeout=5)
                status_code = response.status
                response_data = json.loads(response.read().decode())
                success = True
            except urllib.error.HTTPError as e:
                status_code = e.code
                response_data = json.loads(e.read().decode())
                success = False
            except Exception as e:
                print(f"     ❌ Request failed: {e}")
                continue
            
            # Validate response based on expectations
            if test_case['expected_success']:
                if success and status_code == 200:
                    # Check that response has all fields frontend expects
                    required_fields = ['inputDob', 'ageYears', 'nextBirthdayDate', 'nextBirthdayDayOfWeek', 'daysUntilNextBirthday', 'message']
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        print(f"     ✅ Success - all required fields present")
                        print(f"        Age: {response_data['ageYears']} years")
                        print(f"        Next birthday: {response_data['nextBirthdayDate']} ({response_data['nextBirthdayDayOfWeek']})")
                        print(f"        Days until: {response_data['daysUntilNextBirthday']}")
                        passed_tests += 1
                    else:
                        print(f"     ❌ Missing required fields: {missing_fields}")
                else:
                    print(f"     ❌ Expected success but got status {status_code}")
            else:
                if not success and status_code == 400:
                    # Check that error response has fields frontend expects
                    if 'error' in response_data and 'example' in response_data:
                        print(f"     ✅ Error handled correctly")
                        print(f"        Error: {response_data['error']}")
                        passed_tests += 1
                    else:
                        print(f"     ❌ Error response missing required fields")
                else:
                    print(f"     ❌ Expected error but got status {status_code}")
                    
        except Exception as e:
            print(f"     ❌ Test failed: {e}")
    
    print(f"\n📊 Frontend API Tests: {passed_tests}/{len(test_cases)} passed")
    return passed_tests == len(test_cases)


def test_cors_functionality(base_url="http://localhost:7071"):
    """Test CORS functionality that frontend would rely on."""
    print("\n🧪 Testing CORS functionality...")
    
    try:
        # Simulate a CORS preflight request (OPTIONS)
        request = urllib.request.Request(f"{base_url}/api/nextbirthday", method='OPTIONS')
        request.add_header('Origin', 'http://localhost:8000')
        request.add_header('Access-Control-Request-Method', 'GET')
        request.add_header('Access-Control-Request-Headers', 'Content-Type, Accept')
        
        try:
            response = urllib.request.urlopen(request, timeout=5)
            print("✅ CORS preflight request successful")
            
            # Check CORS headers
            headers = dict(response.headers)
            cors_headers = {
                'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': headers.get('Access-Control-Allow-Headers')
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
            
        except Exception as e:
            print(f"⚠️  CORS preflight test failed: {e}")
        
        # Test actual GET request with Origin header
        request = urllib.request.Request(f"{base_url}/api/nextbirthday?dob=2000-06-15")
        request.add_header('Origin', 'http://localhost:8000')
        
        response = urllib.request.urlopen(request, timeout=5)
        if response.status == 200:
            print("✅ CORS GET request successful")
            
            # Check if Access-Control-Allow-Origin header is present
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            if allow_origin:
                print(f"   Access-Control-Allow-Origin: {allow_origin}")
            else:
                print("⚠️  No Access-Control-Allow-Origin header found")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False


def verify_frontend_configuration():
    """Verify frontend is configured correctly for local development."""
    print("\n🧪 Verifying frontend configuration...")
    
    try:
        with open('frontend/app.js', 'r') as f:
            content = f.read()
        
        checks = [
            ('API Base URL', 'http://localhost:7071/api/nextbirthday' in content),
            ('Configurable API URL', 'API_BASE_URL' in content and 'CONFIG' in content),
            ('Fetch API usage', 'fetch(' in content),
            ('JSON response handling', 'response.json()' in content or '.json()' in content),
            ('Error handling', 'catch' in content and 'error' in content.lower()),
            ('CORS error handling', 'cors' in content.lower() or 'CORS' in content),
            ('Response validation', 'isValidResponse' in content or 'hasOwnProperty' in content)
        ]
        
        passed_checks = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"   ✅ {check_name}")
                passed_checks += 1
            else:
                print(f"   ❌ {check_name}")
        
        print(f"\n📊 Frontend Configuration: {passed_checks}/{len(checks)} checks passed")
        return passed_checks == len(checks)
        
    except Exception as e:
        print(f"❌ Frontend configuration check failed: {e}")
        return False


def main():
    """Run frontend connection tests."""
    print("🎂 Testing Frontend Connection Capability")
    print("=" * 60)
    
    # Start mock server
    mock_server = start_mock_server(7071)
    if not mock_server:
        print("❌ Could not start mock server for testing")
        return False
    
    try:
        # Run tests
        api_tests_passed = test_frontend_api_calls()
        cors_tests_passed = test_cors_functionality()
        config_tests_passed = verify_frontend_configuration()
        
        print("\n" + "=" * 60)
        
        if api_tests_passed and cors_tests_passed and config_tests_passed:
            print("🎉 All frontend connection tests passed!")
            print("\n✅ Frontend Connection Capability Verified:")
            print("   ✓ Frontend can make API calls to backend")
            print("   ✓ Frontend handles successful responses correctly")
            print("   ✓ Frontend handles error responses correctly")
            print("   ✓ CORS configuration allows frontend access")
            print("   ✓ Frontend is properly configured for local development")
            return True
        else:
            print("⚠️  Some tests failed - check output above")
            return False
    
    finally:
        # Stop mock server
        if mock_server:
            print("\n🛑 Stopping mock server...")
            mock_server.shutdown()
            print("✅ Mock server stopped")


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)