#!/usr/bin/env python3
"""
Test the /ai/chat endpoint with proper JSON formatting.
This tests both local and deployed backends.
"""

import requests
import json

# Test against deployed backend
BACKEND_URL = "https://military-hierarchy-backend.onrender.com"
# Or test locally: BACKEND_URL = "https://military-hierarchy-backend.onrender.com/"

def test_ai_chat_minimal():
    """Test with minimal valid request."""
    print("\n" + "="*60)
    print("TEST 1: Minimal AI Chat Request")
    print("="*60)
    
    request_data = {
        "message": "What is the current tactical situation?",
        "context": {
            "node": {
                "name": "1st Infantry Battalion",
                "unit_id": "unit-001"
            },
            "reports": []  # Empty reports array
        }
    }
    
    print("\nRequest URL:", f"{BACKEND_URL}/ai/chat")
    print("\nRequest Body (formatted):")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/ai/chat",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            print("\nResponse Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("\n✗ FAILED!")
            print("\nError Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

def test_ai_chat_with_reports():
    """Test with sample reports."""
    print("\n" + "="*60)
    print("TEST 2: AI Chat Request with Sample Reports")
    print("="*60)
    
    request_data = {
        "message": "What threats are we facing?",
        "context": {
            "node": {
                "name": "1st Infantry Battalion",
                "unit_id": "unit-001"
            },
            "reports": [
                {
                    "report_type": "CONTACT",
                    "timestamp": "2025-10-04T22:47:17",
                    "soldier_name": "Cpl. Smith",
                    "structured_json": json.dumps({
                        "enemy_count": 15,
                        "location": "Grid 1234 5678",
                        "enemy_type": "infantry",
                        "activity": "patrol movement"
                    })
                },
                {
                    "report_type": "SITREP",
                    "timestamp": "2025-10-04T23:15:00",
                    "soldier_name": "Sgt. Johnson",
                    "structured_json": json.dumps({
                        "status": "All units operational",
                        "location": "Forward operating base",
                        "engagement_status": "No contact"
                    })
                }
            ]
        }
    }
    
    print("\nRequest URL:", f"{BACKEND_URL}/ai/chat")
    print(f"\nRequest has {len(request_data['context']['reports'])} reports")
    
    # Validate JSON before sending
    try:
        json_str = json.dumps(request_data)
        print(f"Request JSON size: {len(json_str)} bytes")
        print("\nValidating JSON structure...")
        json.loads(json_str)  # Verify it can be parsed
        print("✓ JSON is valid")
    except json.JSONDecodeError as e:
        print(f"✗ JSON validation failed: {e}")
        return
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/ai/chat",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            print("\nResponse Body:")
            result = response.json()
            print(f"  - Timestamp: {result.get('timestamp')}")
            print(f"  - Reports Analyzed: {result.get('reports_analyzed')}")
            print(f"\n  AI Response:\n  {result.get('response')[:200]}...")
        else:
            print("\n✗ FAILED!")
            print("\nError Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

def test_ai_chat_frontend_format():
    """Test with the exact format the frontend sends."""
    print("\n" + "="*60)
    print("TEST 3: AI Chat Request (Frontend Format)")
    print("="*60)
    
    # This mimics what ai-chat.tsx sends
    request_data = {
        "message": "what is up with the 1st infantry battalion",
        "context": {
            "node": {
                "name": "1st Infantry Battalion",
                "unit_id": "unit-001",
                "level": 3
            },
            "reports": [
                {
                    "type": "CONTACT",
                    "time": "2025-10-04T22:47:17",
                    "from": "Cpl. Smith",
                    "data": {
                        "enemy_count": 15,
                        "location": "Grid 1234 5678",
                        "enemy_type": "infantry",
                        "activity": "patrol movement"
                    }
                }
            ]
        }
    }
    
    print("\nRequest URL:", f"{BACKEND_URL}/ai/chat")
    print("\nThis uses the transformed frontend format (type/time/from/data)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/ai/chat",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            print("\nResponse Body:")
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print("\n✗ FAILED!")
            print("\nError Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI CHAT ENDPOINT TESTING")
    print("="*60)
    print(f"\nTesting against: {BACKEND_URL}")
    print("\nThis will test the /ai/chat endpoint with different request formats")
    print("to identify JSON parsing issues.")
    
    # Run tests
    test_ai_chat_minimal()
    test_ai_chat_with_reports()
    test_ai_chat_frontend_format()
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nIf you see 422 errors, check:")
    print("  1. JSON structure matches ChatMessage Pydantic model")
    print("  2. No double-encoded JSON strings")
    print("  3. All required fields are present")
    print("  4. GEMINI_API_KEY is set in Render environment")

if __name__ == "__main__":
    main()
