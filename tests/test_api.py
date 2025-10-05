#!/usr/bin/env python3
"""
Test script for the Military Hierarchy API
Tests all endpoints to ensure they work correctly
"""

import requests
import json
import time

API_BASE = "https://military-hierarchy-backend.onrender.com/"

def test_endpoint(endpoint, description):
    """Test a single API endpoint."""
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}")
            print(f"   Response: {len(str(data))} characters")
            return True
        else:
            print(f"❌ {description}")
            print(f"   Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}")
        print("   Error: Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {e}")
        return False

def main():
    print("🧪 Testing Military Hierarchy API...")
    print(f"API Base URL: {API_BASE}")
    print("")
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Test endpoints
    endpoints = [
        ("/", "Root endpoint"),
        ("/soldiers", "Get all soldiers"),
        ("/units", "Get all units"),
        ("/reports", "Get all reports"),
        ("/hierarchy", "Get military hierarchy"),
        ("/soldiers/ALPHA_01/raw_inputs", "Get raw inputs for ALPHA_01"),
        ("/soldiers/ALPHA_01/reports", "Get reports for ALPHA_01"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, description in endpoints:
        if test_endpoint(endpoint, description):
            passed += 1
        print("")
    
    print(f"📊 Test Results: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("")
        print("Next steps:")
        print("1. Start the frontend: cd mil_dashboard && npm run dev")
        print("2. Visit http://localhost:3000 to see the dashboard")
        print("3. (Optional) Start MQTT broker and run soldier_simulator.py")
    else:
        print("⚠️  Some tests failed. Check the backend server.")

if __name__ == "__main__":
    main()
