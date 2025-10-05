#!/usr/bin/env python3
"""
Test script to trigger AI suggestions by sending reports with specific keywords.
This will demonstrate the Smart Notifications feature.
"""

import requests
import json
from datetime import datetime
import time

# Backend URL
API_BASE = "https://military-hierarchy-backend.onrender.com/"

def send_casualty_report():
    """Send a report that should trigger URGENT CASEVAC suggestion"""
    print("\n🩹 Sending CASUALTY report (should trigger URGENT CASEVAC suggestion)...")
    report = {
        "report_type": "CASUALTY",
        "structured_json": {
            "casualties": 2,
            "severity": "critical",
            "location": "Grid 38.9072, 77.0369",
            "description": "2 soldiers wounded by IED. Critical bleeding, need immediate medevac.",
            "timestamp": datetime.now().isoformat()
        },
        "text_content": "URGENT: 2 soldiers critically wounded, severe bleeding, requesting immediate CASEVAC",
        "confidence": 0.95
    }
    
    response = requests.post(f"{API_BASE}/soldiers/ALPHA_01/reports", json=report)
    print(f"   ✅ Response: {response.json()}")
    return response.json()

def send_contact_report():
    """Send a contact report that should trigger EOINCREP suggestion"""
    print("\n👁️  Sending CONTACT report (should trigger HIGH EOINCREP suggestion)...")
    report = {
        "report_type": "CONTACT",
        "structured_json": {
            "enemy_count": 15,
            "vehicle_count": 3,
            "location": "Grid 38.8850, 77.0340",
            "description": "Enemy patrol spotted: 15 infantry with 3 armored vehicles moving north",
            "engagement_status": "observing",
            "timestamp": datetime.now().isoformat()
        },
        "text_content": "Contact! Enemy patrol detected: approximately 15 hostiles with 3 armored vehicles",
        "confidence": 0.92
    }
    
    response = requests.post(f"{API_BASE}/soldiers/ALPHA_02/reports", json=report)
    print(f"   ✅ Response: {response.json()}")
    return response.json()

def send_ied_report():
    """Send a report that should trigger EOINCREP_EOD suggestion"""
    print("\n💣 Sending IED report (should trigger HIGH EOINCREP_EOD suggestion)...")
    report = {
        "report_type": "INTELLIGENCE",
        "structured_json": {
            "location": "Grid 38.8900, 77.0350",
            "description": "Suspected IED discovered on main supply route. Unexploded ordnance visible.",
            "threat_level": "high",
            "timestamp": datetime.now().isoformat()
        },
        "text_content": "IED discovered! Unexploded explosive device found on MSR. Area cordoned off.",
        "confidence": 0.88
    }
    
    response = requests.post(f"{API_BASE}/soldiers/ALPHA_03/reports", json=report)
    print(f"   ✅ Response: {response.json()}")
    return response.json()

def check_suggestions():
    """Check what suggestions were created"""
    print("\n🔍 Checking AI suggestions...")
    
    try:
        response = requests.get(f"{API_BASE}/api/suggestions?status=pending")
        data = response.json()
        
        suggestions = data.get("suggestions", [])
        print(f"\n📊 Found {len(suggestions)} pending suggestions:\n")
        
        if not suggestions:
            print("   ⚠️  No suggestions found! This might mean:")
            print("      1. The reports didn't contain trigger keywords")
            print("      2. The backend had an error (check backend logs)")
            print("      3. Suggestions were already dismissed")
        
        for idx, suggestion in enumerate(suggestions, 1):
            print(f"   {idx}. 🔔 {suggestion['suggestion_type']} - {suggestion['urgency']}")
            print(f"      Reason: {suggestion['reason']}")
            print(f"      Confidence: {suggestion['confidence']}")
            print(f"      Created: {suggestion['created_at']}")
            print()
        
        return suggestions
        
    except Exception as e:
        print(f"   ❌ Error checking suggestions: {e}")
        return []

def main():
    print("=" * 70)
    print("🤖 AI SUGGESTIONS TEST SCRIPT")
    print("=" * 70)
    print("\nThis script will:")
    print("1. Send 3 test reports with trigger keywords")
    print("2. Check if AI suggestions were created")
    print("3. You should see them in the dashboard's bell icon 🔔")
    print("\nMake sure:")
    print("✓ Backend is running at https://military-hierarchy-backend.onrender.com/")
    print("✓ Frontend is running at http://localhost:3000")
    print("\n" + "=" * 70)
    
    try:
        # Send test reports
        send_casualty_report()
        time.sleep(0.5)
        
        send_contact_report()
        time.sleep(0.5)
        
        send_ied_report()
        time.sleep(1)
        
        # Check suggestions
        suggestions = check_suggestions()
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE!")
        print("=" * 70)
        
        if suggestions:
            print(f"\n🎉 SUCCESS! {len(suggestions)} AI suggestions were created!")
            print("\n📱 Next steps:")
            print("1. Open the dashboard: http://localhost:3000")
            print("2. Look for the bell icon 🔔 in the top right")
            print("3. You should see a red badge with the number of suggestions")
            print("4. Click the bell to see the suggestions")
            print("5. Click 'Create Report' on any suggestion to open the builder")
        else:
            print("\n⚠️  No suggestions were created.")
            print("\n🔧 Troubleshooting:")
            print("1. Check backend terminal for any errors")
            print("2. Make sure the suggestions table exists in the database")
            print("3. Try running: sqlite3 military_hierarchy.db 'SELECT * FROM suggestions;'")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("Make sure the backend is running:")
        print("   python backend.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
