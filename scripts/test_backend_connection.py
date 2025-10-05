#!/usr/bin/env python3
"""
Test Backend Connection and Add Sample Data
"""

import requests
import json
from datetime import datetime, timedelta

# Test both local and deployed backend
BACKEND_URLS = [
    "https://military-hierarchy-backend.onrender.com/",
    "https://military-hierarchy-backend.onrender.com"
]

def test_backend_health(url):
    """Test if backend is responding"""
    try:
        response = requests.get(f"{url}/hierarchy", timeout=10)
        print(f"✅ {url} - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Units found: {len(data.get('units', []))}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {url} - Connection failed: {e}")
        return False

def add_sample_report(url, soldier_id="ALPHA_01"):
    """Add a simple test report"""
    
    # First add a raw input
    raw_input_data = {
        "soldier_id": soldier_id,
        "raw_text": "CASEVAC request - soldier down with gunshot wound",
        "input_type": "voice",
        "confidence": 0.95,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(f"{url}/soldiers/{soldier_id}/raw_inputs", 
                               json=raw_input_data, timeout=10)
        if response.status_code == 200:
            input_id = response.json()["input_id"]
            print(f"✅ Created raw input: {input_id}")
        else:
            print(f"❌ Failed to create raw input: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating raw input: {e}")
        return False
    
    # Then add a report
    report_data = {
        "soldier_id": soldier_id,
        "unit_id": "PLT_1",
        "report_type": "CASEVAC",
        "structured_json": json.dumps({
            "casualties": [{
                "name": "Pvt. Test",
                "injury": "Gunshot wound",
                "severity": "URGENT",
                "status": "Stable"
            }],
            "location": "Grid 123456",
            "urgency": "URGENT"
        }),
        "confidence": 0.9,
        "timestamp": datetime.utcnow().isoformat(),
        "source_input_id": input_id,
        "status": "generated"
    }
    
    try:
        response = requests.post(f"{url}/soldiers/{soldier_id}/reports", 
                               json=report_data, timeout=10)
        if response.status_code == 200:
            report_id = response.json()["report_id"]
            print(f"✅ Created report: {report_id}")
            return True
        else:
            print(f"❌ Failed to create report: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating report: {e}")
        return False

def main():
    print("🔍 Testing backend connections...\n")
    
    working_url = None
    for url in BACKEND_URLS:
        if test_backend_health(url):
            working_url = url
            break
        print()
    
    if not working_url:
        print("💀 No working backend found!")
        print("\n🛠️  Try:")
        print("1. Start local backend: python backend/backend.py")
        print("2. Check Render dashboard for backend service status")
        return
    
    print(f"\n🎯 Using backend: {working_url}")
    print("\n📝 Adding sample report...")
    
    if add_sample_report(working_url):
        print("\n🎉 Success! Check your reports at:")
        print(f"   {working_url}/reports")
        print(f"   {working_url}/docs")
    else:
        print("\n💀 Failed to add sample data")

if __name__ == "__main__":
    main()