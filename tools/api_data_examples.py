#!/usr/bin/env python3
"""
API Data Examples - How to Send Data to the Military Hierarchy System
This script demonstrates how to send various types of data to the API.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://10.3.35.27:8000"  # Use your network IP
# API_BASE = "https://military-hierarchy-backend.onrender.com/"  # Use this for local testing

def send_request(method, endpoint, data=None, description=""):
    """Send a request to the API and print the result."""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"📡 {description}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to API server")
        print("Make sure the backend is running on the correct IP/port")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Demonstrate various API operations."""
    print("🚀 Military Hierarchy API - Data Sending Examples")
    print(f"API Base URL: {API_BASE}")
    
    # Test 1: Check system status
    send_request("GET", "/", description="Check System Status")
    
    # Test 2: Get existing soldiers (to see what's available)
    soldiers_result = send_request("GET", "/soldiers", description="Get All Soldiers")
    
    if not soldiers_result:
        print("\n❌ Cannot proceed - API server is not responding")
        return
    
    # Find an existing soldier ID for testing
    existing_soldier_id = None
    if soldiers_result and "soldiers" in soldiers_result and soldiers_result["soldiers"]:
        existing_soldier_id = soldiers_result["soldiers"][0]["soldier_id"]
        print(f"\n📋 Using existing soldier: {existing_soldier_id}")
    else:
        print("\n⚠️  No existing soldiers found. Creating a new one...")
        
        # Test 3: Create a new soldier
        new_soldier_data = {
            "soldier_id": "TEST_01",
            "name": "Test Soldier",
            "rank": "Private",
            "unit_id": "PLT_1",  # Assuming this unit exists
            "device_id": "RADIO_TEST_01",
            "status": "active"
        }
        
        soldier_result = send_request("POST", "/soldiers", new_soldier_data, "Create New Soldier")
        if soldier_result:
            existing_soldier_id = "TEST_01"
    
    if not existing_soldier_id:
        print("\n❌ Cannot proceed - no soldier available for testing")
        return
    
    # Test 4: Send raw input from soldier
    raw_input_data = {
        "raw_text": "Enemy spotted at grid 123456, requesting backup",
        "input_type": "voice",
        "confidence": 0.95,
        "location_ref": "GPS_123456",
        "timestamp": datetime.now().isoformat()
    }
    
    send_request("POST", f"/soldiers/{existing_soldier_id}/raw_inputs", 
                raw_input_data, f"Send Raw Input from {existing_soldier_id}")
    
    # Test 5: Create a structured report
    report_data = {
        "report_type": "SITREP",
        "structured_json": {
            "enemy_contact": True,
            "location": "grid 123456",
            "threat_level": "medium",
            "casualties": 0,
            "ammunition_status": "adequate",
            "weather": "clear",
            "visibility": "good"
        },
        "confidence": 0.85
    }
    
    send_request("POST", f"/soldiers/{existing_soldier_id}/reports", 
                report_data, f"Create Structured Report for {existing_soldier_id}")
    
    # Test 6: Update soldier status
    status_data = {
        "status": "in_combat"
    }
    
    send_request("PUT", f"/soldiers/{existing_soldier_id}/status", 
                status_data, f"Update Status for {existing_soldier_id}")
    
    # Test 7: Send another raw input (simulating ongoing communication)
    time.sleep(1)  # Small delay to show different timestamps
    
    follow_up_input = {
        "raw_text": "Backup arrived, enemy retreating",
        "input_type": "voice",
        "confidence": 0.92,
        "location_ref": "GPS_123456"
    }
    
    send_request("POST", f"/soldiers/{existing_soldier_id}/raw_inputs", 
                follow_up_input, f"Send Follow-up Input from {existing_soldier_id}")
    
    # Test 8: Create a mission complete report
    mission_complete_data = {
        "report_type": "MISSION_COMPLETE",
        "structured_json": {
            "mission_status": "completed",
            "objectives_achieved": ["secure_area", "eliminate_threat"],
            "casualties": 0,
            "equipment_status": "all_operational",
            "next_objective": "return_to_base",
            "estimated_return_time": "15:30"
        },
        "confidence": 0.95
    }
    
    send_request("POST", f"/soldiers/{existing_soldier_id}/reports", 
                mission_complete_data, f"Create Mission Complete Report for {existing_soldier_id}")
    
    # Test 9: Update status to returning
    return_status_data = {
        "status": "returning"
    }
    
    send_request("PUT", f"/soldiers/{existing_soldier_id}/status", 
                return_status_data, f"Update Status to Returning for {existing_soldier_id}")
    
    # Test 10: Get the soldier's recent inputs and reports
    send_request("GET", f"/soldiers/{existing_soldier_id}/raw_inputs?limit=10", 
                description=f"Get Recent Raw Inputs for {existing_soldier_id}")
    
    send_request("GET", f"/soldiers/{existing_soldier_id}/reports?limit=10", 
                description=f"Get Recent Reports for {existing_soldier_id}")
    
    # Test 11: Get all recent reports
    send_request("GET", "/reports?limit=20", description="Get All Recent Reports")
    
    print(f"\n{'='*60}")
    print("🎉 API Testing Complete!")
    print(f"{'='*60}")
    print("\nNext Steps:")
    print("1. Check the dashboard at http://10.3.35.27:3000")
    print("2. View the interactive API docs at http://10.3.35.27:8000/docs")
    print("3. Use the examples above to integrate with your own applications")

def test_network_connectivity():
    """Test if the API is accessible from the network."""
    print("🔍 Testing Network Connectivity...")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible from the network!")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("Make sure:")
        print("  1. The backend is running (python backend.py)")
        print("  2. The IP address is correct")
        print("  3. Windows Firewall allows the connection")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Test network connectivity only")
    print("2. Run full API examples")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_network_connectivity()
    else:
        if test_network_connectivity():
            main()
        else:
            print("\n❌ Cannot proceed without network connectivity")
