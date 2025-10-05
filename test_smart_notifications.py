"""
Test script for Smart Notifications (Level 2) system.
Sends various reports to backend and verifies triggers are detected.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://military-hierarchy-backend.onrender.com/"

def send_test_report(soldier_id: str, report_type: str, structured_json: dict, text_content: str = ""):
    """Send a test report to the backend."""
    payload = {
        "report_type": report_type,
        "structured_json": structured_json,
        "text_content": text_content,
        "confidence": 0.85
    }
    
    print(f"\n{'='*60}")
    print(f"📤 Sending {report_type} report from soldier {soldier_id}")
    print(f"{'='*60}")
    print(json.dumps(structured_json, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/soldiers/{soldier_id}/reports",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Report created: {result['report_id']}")
        return result['report_id']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_suggestions():
    """Check for any pending suggestions."""
    print(f"\n{'='*60}")
    print("🔍 Checking for AI suggestions...")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/suggestions?status=pending")
        response.raise_for_status()
        data = response.json()
        
        suggestions = data.get('suggestions', [])
        print(f"Found {len(suggestions)} pending suggestions:\n")
        
        for i, sugg in enumerate(suggestions, 1):
            print(f"{i}. {sugg['suggestion_type']} - {sugg['urgency']}")
            print(f"   Reason: {sugg['reason']}")
            print(f"   Confidence: {sugg['confidence']*100:.0f}%")
            print(f"   Source reports: {len(sugg['source_reports'])}")
            print(f"   Created: {sugg['created_at']}")
            print()
        
        return suggestions
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_casevac_urgent():
    """Test URGENT CASEVAC trigger - critical casualties."""
    print("\n\n" + "🚨" * 30)
    print("TEST 1: URGENT CASEVAC - Critical Casualties")
    print("🚨" * 30)
    
    send_test_report(
        soldier_id="ALPHA_01",
        report_type="CASUALTY",
        structured_json={
            "casualties": 2,
            "severity": "critical",
            "location": "Grid NK 234 567",
            "description": "2x KIA from IED blast, severe bleeding, life-threatening injuries"
        },
        text_content="URGENT: 2 soldiers down, critical condition, need immediate CASEVAC"
    )
    
    time.sleep(2)
    check_suggestions()

def test_casevac_priority():
    """Test PRIORITY CASEVAC trigger - wounded soldiers."""
    print("\n\n" + "⚠️ " * 30)
    print("TEST 2: PRIORITY CASEVAC - Wounded Soldiers")
    print("⚠️ " * 30)
    
    send_test_report(
        soldier_id="BRAVO_01",
        report_type="CASUALTY",
        structured_json={
            "casualties": 1,
            "severity": "serious",
            "location": "Grid NK 123 456",
            "description": "1x gunshot wound to leg, stable but needs evacuation"
        },
        text_content="Soldier wounded in firefight, requesting MEDEVAC"
    )
    
    time.sleep(2)
    check_suggestions()

def test_eoincrep_high():
    """Test HIGH EOINCREP trigger - significant enemy force."""
    print("\n\n" + "👁️ " * 30)
    print("TEST 3: HIGH EOINCREP - Large Enemy Force")
    print("👁️ " * 30)
    
    send_test_report(
        soldier_id="ALPHA_03",
        report_type="CONTACT",
        structured_json={
            "enemy_count": 15,
            "vehicle_count": 3,
            "location": "Grid NK 345 678",
            "direction": "North",
            "equipment": ["BTR-80 APCs", "PKM machine guns", "RPG-7"],
            "description": "Large enemy mechanized infantry patrol moving south"
        },
        text_content="Enemy contact: 15 hostiles with 3 APCs, armed with heavy weapons"
    )
    
    time.sleep(2)
    check_suggestions()

def test_eoincrep_medium():
    """Test MEDIUM EOINCREP trigger - enemy patrol."""
    print("\n\n" + "👁️ " * 30)
    print("TEST 4: MEDIUM EOINCREP - Enemy Patrol")
    print("👁️ " * 30)
    
    send_test_report(
        soldier_id="ALPHA_02",
        report_type="CONTACT",
        structured_json={
            "enemy_count": 6,
            "location": "Grid NK 456 789",
            "direction": "East",
            "equipment": ["Small arms", "AK-47"],
            "description": "Enemy infantry patrol, 6 hostiles"
        },
        text_content="Spotted enemy patrol moving through grid NK 456 789"
    )
    
    time.sleep(2)
    check_suggestions()

def test_eoincrep_eod():
    """Test EOD EOINCREP trigger - explosive device."""
    print("\n\n" + "💣" * 30)
    print("TEST 5: EOD EOINCREP - Explosive Device")
    print("💣" * 30)
    
    send_test_report(
        soldier_id="BRAVO_02",
        report_type="INTELLIGENCE",
        structured_json={
            "location": "Grid NK 567 890",
            "description": "Suspected IED found on roadside, unexploded ordnance"
        },
        text_content="Found suspicious device, possible IED or mine, requesting EOD"
    )
    
    time.sleep(2)
    check_suggestions()

def test_no_trigger():
    """Test report that should NOT trigger suggestions."""
    print("\n\n" + "✅" * 30)
    print("TEST 6: No Trigger - Routine SITREP")
    print("✅" * 30)
    
    send_test_report(
        soldier_id="ALPHA_04",
        report_type="SITREP",
        structured_json={
            "location": "Grid NK 678 901",
            "status": "all clear",
            "description": "Routine patrol, no contact, all personnel accounted for"
        },
        text_content="Routine SITREP: patrol complete, returning to base"
    )
    
    time.sleep(2)
    suggestions = check_suggestions()
    if len(suggestions) == 0:
        print("✅ CORRECT: No suggestion triggered for routine report")

def dismiss_all_suggestions():
    """Dismiss all pending suggestions to clean up."""
    print("\n\n" + "🧹" * 30)
    print("CLEANUP: Dismissing all suggestions")
    print("🧹" * 30)
    
    response = requests.get(f"{BASE_URL}/api/suggestions?status=pending")
    suggestions = response.json().get('suggestions', [])
    
    for sugg in suggestions:
        try:
            requests.delete(f"{BASE_URL}/api/suggestions/{sugg['suggestion_id']}")
            print(f"✅ Dismissed: {sugg['suggestion_type']} - {sugg['reason']}")
        except Exception as e:
            print(f"❌ Error dismissing {sugg['suggestion_id']}: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SMART NOTIFICATIONS TEST SUITE - Level 2")
    print("Testing AI-triggered report suggestions")
    print("=" * 80)
    
    # Clean up old suggestions first
    dismiss_all_suggestions()
    time.sleep(1)
    
    # Run tests
    test_casevac_urgent()
    time.sleep(2)
    
    test_casevac_priority()
    time.sleep(2)
    
    test_eoincrep_high()
    time.sleep(2)
    
    test_eoincrep_medium()
    time.sleep(2)
    
    test_eoincrep_eod()
    time.sleep(2)
    
    test_no_trigger()
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    suggestions = check_suggestions()
    print(f"\n✅ Tests complete! {len(suggestions)} suggestions should be visible in the UI.")
    print("\nExpected results:")
    print("  - 2 CASEVAC suggestions (1 URGENT, 1 HIGH)")
    print("  - 2 EOINCREP suggestions (1 HIGH, 1 MEDIUM)")
    print("  - 1 EOINCREP_EOD suggestion (HIGH)")
    print("  - Total: 5 suggestions")
    print("\nOpen the dashboard to see notifications! 🚀")
