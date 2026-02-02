#!/usr/bin/env python3
"""
Pre-deployment testing script.
This script runs comprehensive tests before deploying to Azure.
"""

import sys
import os
import subprocess
import json
import requests
import time
from datetime import datetime

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def test_local_server():
    """Test the local development server."""
    print("🧪 Testing local development server...")
    
    # Start local server in background
    print("  Starting local server...")
    server_process = subprocess.Popen([sys.executable, "scripts/local_server.py"], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test API endpoint
        print("  Testing API endpoint...")
        response = requests.get("http://localhost:8000/api/nextbirthday?dob=1990-05-15", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["inputDob", "ageYears", "nextBirthdayDate", 
                             "nextBirthdayDayOfWeek", "daysUntilNextBirthday", "message"]
            
            if all(field in data for field in required_fields):
                print("  ✅ API endpoint working correctly")
                return True
            else:
                print("  ❌ API response missing required fields")
                return False
        else:
            print(f"  ❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API request failed: {e}")
        return False
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait()

def test_azure_functions_structure():
    """Test Azure Functions project structure."""
    print("🔍 Validating Azure Functions structure...")
    
    required_files = [
        "src/api/function_app.py",
        "src/api/host.json",
        "src/api/local.settings.json",
        "src/api/requirements.txt"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"  ❌ Missing required file: {file_path}")
            return False
        print(f"  ✅ Found: {file_path}")
    
    # Validate host.json
    try:
        with open("src/api/host.json", "r") as f:
            host_config = json.load(f)
            if "version" in host_config and host_config["version"] == "2.0":
                print("  ✅ host.json is valid")
            else:
                print("  ❌ host.json missing version 2.0")
                return False
    except json.JSONDecodeError:
        print("  ❌ host.json is not valid JSON")
        return False
    
    return True

def test_static_web_app_structure():
    """Test Static Web App project structure."""
    print("🌐 Validating Static Web App structure...")
    
    required_files = [
        "src/web/index.html",
        "src/web/app.js",
        "src/web/styles.css",
        "src/web/staticwebapp.config.json"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"  ❌ Missing required file: {file_path}")
            return False
        print(f"  ✅ Found: {file_path}")
    
    # Validate staticwebapp.config.json
    try:
        with open("src/web/staticwebapp.config.json", "r") as f:
            config = json.load(f)
            if "routes" in config:
                print("  ✅ staticwebapp.config.json is valid")
            else:
                print("  ❌ staticwebapp.config.json missing routes")
                return False
    except json.JSONDecodeError:
        print("  ❌ staticwebapp.config.json is not valid JSON")
        return False
    
    return True

def run_unit_tests():
    """Run the unit test suite."""
    print("🧪 Running unit tests...")
    
    # Try different Python commands
    python_commands = ["python3", "python"]
    
    for cmd in python_commands:
        success, stdout, stderr = run_command(f"{cmd} -m pytest tests/ -v")
        if success:
            print("  ✅ All unit tests passed")
            return True
        elif "command not found" not in stderr.lower():
            # Python was found but tests failed
            print("  ❌ Unit tests failed")
            print(f"  Error: {stderr}")
            return False
    
    print("  ⚠️  Python/pytest not found, skipping unit tests")
    return True  # Don't fail deployment for missing test tools

def main():
    """Run all pre-deployment tests."""
    print("🎂 Birthday Countdown - Pre-Deployment Testing")
    print("=" * 50)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Azure Functions Structure", test_azure_functions_structure),
        ("Static Web App Structure", test_static_web_app_structure),
        ("Unit Tests", run_unit_tests),
        ("Local Server", test_local_server),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())