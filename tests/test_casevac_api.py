"""
Test script for CASEVAC API endpoint
Run this after starting the backend to test if the suggest endpoint works
"""
import requests
import json

def test_casevac_suggest():
    """Test the CASEVAC suggest endpoint"""
    
    # Sample test data
    test_payload = {
        "unit_id": "test-unit-1",
        "unit_name": "Test Battalion",
        "soldier_ids": ["soldier-1", "soldier-2"],
        "reports": [
            {
                "report_id": "test-1",
                "soldier_id": "soldier-1",
                "unit_id": "test-unit-1",
                "timestamp": "2025-10-04T12:00:00",
                "report_type": "CASUALTY",
                "structured_json": json.dumps({
                    "location": "Grid NV123456",
                    "casualty_type": "combat",
                    "casualty_count": 2,
                    "severity": "critical",
                    "injuries": "gunshot wounds",
                    "immediate_care_given": "pressure dressing applied"
                }),
                "confidence": 0.95
            }
        ],
        "suggestion_id": None
    }
    
    print("Testing CASEVAC suggest endpoint...")
    print(f"Sending request with {len(test_payload['reports'])} reports")
    
    try:
        response = requests.post(
            "https://military-hierarchy-backend.onrender.com//casevac/suggest",
            json=test_payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Suggested fields:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\n❌ ERROR {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend at https://military-hierarchy-backend.onrender.com/")
        print("Make sure the backend is running: .\.venv\Scripts\python.exe backend.py")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_casevac_suggest()
