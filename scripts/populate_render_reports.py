#!/usr/bin/env python3
"""
Populate Render Deployment with Sample Reports
Sends test reports to the deployed backend API
"""

import requests
import json
from datetime import datetime, timedelta
import random

# Deployed backend URL
API_BASE_URL = "https://military-hierarchy-backend.onrender.com"

# Sample soldier IDs from the database
SOLDIERS = [
    {"id": "ALPHA_01", "name": "Lt. John Smith", "unit": "PLT_1"},
    {"id": "ALPHA_02", "name": "Sgt. Mike Johnson", "unit": "SQD_1"},
    {"id": "ALPHA_03", "name": "Pvt. David Wilson", "unit": "SQD_1"},
    {"id": "ALPHA_04", "name": "Cpl. Sarah Brown", "unit": "SQD_2"},
    {"id": "BRAVO_01", "name": "Capt. Tom Davis", "unit": "CO_B"},
]

# Sample CASEVAC Reports
CASEVAC_REPORTS = [
    {
        "report_type": "CASEVAC",
        "structured_json": {
            "casualties": [
                {
                    "name": "Pvt. Williams",
                    "injury": "Gunshot wound to left leg",
                    "severity": "URGENT",
                    "status": "Stable"
                }
            ],
            "location": "Grid 38SMB 123 456",
            "evacuation_point": "LZ Alpha",
            "urgency": "URGENT",
            "enemy_activity": "Sporadic small arms fire",
            "security": "Secured by squad element"
        },
        "confidence": 0.92
    },
    {
        "report_type": "CASEVAC",
        "structured_json": {
            "casualties": [
                {
                    "name": "Sgt. Martinez",
                    "injury": "Shrapnel wounds to torso and arms",
                    "severity": "URGENT SURGICAL",
                    "status": "Critical"
                },
                {
                    "name": "Cpl. Jenkins",
                    "injury": "Broken ankle",
                    "severity": "PRIORITY",
                    "status": "Stable"
                }
            ],
            "location": "Grid 38SMB 234 567",
            "evacuation_point": "LZ Bravo",
            "urgency": "URGENT SURGICAL",
            "enemy_activity": "Heavy contact, enemy retreating",
            "security": "LZ secured"
        },
        "confidence": 0.88
    },
    {
        "report_type": "MEDEVAC",
        "structured_json": {
            "casualties": [
                {
                    "name": "Pvt. Anderson",
                    "injury": "Heat exhaustion",
                    "severity": "ROUTINE",
                    "status": "Conscious"
                }
            ],
            "location": "Grid 38SMB 345 678",
            "evacuation_point": "Patrol Base Charlie",
            "urgency": "ROUTINE",
            "enemy_activity": "None",
            "security": "Secure area"
        },
        "confidence": 0.95
    }
]

# Sample EOINCREP Reports (Explosive Ordnance Incident Reports)
EOINCREP_REPORTS = [
    {
        "report_type": "EOINCREP",
        "structured_json": {
            "incident_type": "IED Discovery",
            "location": "Grid 38SMB 456 789",
            "description": "Suspected IED found buried at roadside, wires visible",
            "threat_level": "HIGH",
            "action_taken": "Area cordoned off, EOD team requested",
            "casualties": "None",
            "time_discovered": "14:30"
        },
        "confidence": 0.91
    },
    {
        "report_type": "EOINCREP",
        "structured_json": {
            "incident_type": "UXO Discovery",
            "location": "Grid 38SMB 567 890",
            "description": "Artillery shell found in field, appears old but unstable",
            "threat_level": "MEDIUM",
            "action_taken": "Marked with red smoke, EOD notified",
            "casualties": "None",
            "time_discovered": "09:15"
        },
        "confidence": 0.87
    }
]

# Sample SITREP Reports
SITREP_REPORTS = [
    {
        "report_type": "SITREP",
        "structured_json": {
            "unit": "1st Platoon",
            "location": "Checkpoint Delta",
            "situation": "Maintaining checkpoint security, light civilian traffic",
            "enemy_activity": "None observed in past 6 hours",
            "friendly_forces": "Full strength, morale high",
            "logistics": "Supplies adequate, water resupply needed in 24hrs",
            "next_action": "Continue checkpoint ops until relief at 0600"
        },
        "confidence": 0.94
    },
    {
        "report_type": "SITREP",
        "structured_json": {
            "unit": "2nd Squad",
            "location": "Patrol Route Whiskey",
            "situation": "Completed patrol, returning to base",
            "enemy_activity": "Suspicious vehicle observed at grid 38SMB 678 901, did not engage",
            "friendly_forces": "All personnel accounted for",
            "logistics": "Ammunition count good, comms functioning",
            "next_action": "Return to FOB for debrief"
        },
        "confidence": 0.89
    }
]

# Sample SPOTREP Reports
SPOTREP_REPORTS = [
    {
        "report_type": "SPOTREP",
        "structured_json": {
            "what": "Enemy patrol, 8-10 personnel with small arms",
            "when": "15:45 local time",
            "where": "Grid 38SMB 789 012",
            "activity": "Moving north along ridgeline",
            "assessment": "Likely reconnaissance element",
            "action_taken": "Observation only, remained concealed"
        },
        "confidence": 0.90
    },
    {
        "report_type": "SPOTREP",
        "structured_json": {
            "what": "Civilian gathering, approximately 30 people",
            "when": "11:20 local time",
            "where": "Village center, grid 38SMB 890 123",
            "activity": "Market day activities, normal pattern",
            "assessment": "No hostile indicators",
            "action_taken": "Continued observation"
        },
        "confidence": 0.93
    }
]


def create_raw_input(soldier_id, text, input_type="voice"):
    """Create a raw input entry"""
    timestamp = datetime.utcnow() - timedelta(minutes=random.randint(5, 60))
    
    payload = {
        "soldier_id": soldier_id,
        "raw_text": text,
        "input_type": input_type,
        "confidence": round(random.uniform(0.85, 0.98), 2),
        "timestamp": timestamp.isoformat()
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/raw_inputs", json=payload)
        if response.status_code == 200:
            return response.json()["input_id"]
        else:
            print(f"Failed to create raw input: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error creating raw input: {e}")
        return None


def create_report(soldier, report_data):
    """Create a report for a soldier"""
    timestamp = datetime.utcnow() - timedelta(minutes=random.randint(1, 30))
    
    # First create a raw input
    raw_text = f"Report from {soldier['name']}: {report_data['report_type']} incident"
    input_id = create_raw_input(soldier['id'], raw_text)
    
    # Create the report
    payload = {
        "soldier_id": soldier['id'],
        "unit_id": soldier['unit'],
        "report_type": report_data['report_type'],
        "structured_json": json.dumps(report_data['structured_json']),
        "confidence": report_data['confidence'],
        "timestamp": timestamp.isoformat(),
        "source_input_id": input_id,
        "status": "generated"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/reports", json=payload)
        if response.status_code == 200:
            print(f"✅ Created {report_data['report_type']} report for {soldier['name']}")
            return response.json()
        else:
            print(f"❌ Failed to create report: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating report: {e}")
        return None


def populate_reports():
    """Populate the database with sample reports"""
    print(f"🚀 Starting to populate reports to {API_BASE_URL}\n")
    
    # Test connection
    try:
        response = requests.get(f"{API_BASE_URL}/hierarchy")
        print(f"✅ Backend is reachable: {response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        return
    
    reports_created = 0
    
    # Create CASEVAC reports
    print("📋 Creating CASEVAC/MEDEVAC reports...")
    for report_data in CASEVAC_REPORTS:
        soldier = random.choice(SOLDIERS)
        if create_report(soldier, report_data):
            reports_created += 1
    
    # Create EOINCREP reports
    print("\n💣 Creating EOINCREP reports...")
    for report_data in EOINCREP_REPORTS:
        soldier = random.choice(SOLDIERS)
        if create_report(soldier, report_data):
            reports_created += 1
    
    # Create SITREP reports
    print("\n📊 Creating SITREP reports...")
    for report_data in SITREP_REPORTS:
        soldier = random.choice(SOLDIERS)
        if create_report(soldier, report_data):
            reports_created += 1
    
    # Create SPOTREP reports
    print("\n👁️ Creating SPOTREP reports...")
    for report_data in SPOTREP_REPORTS:
        soldier = random.choice(SOLDIERS)
        if create_report(soldier, report_data):
            reports_created += 1
    
    print(f"\n🎉 Completed! Created {reports_created} reports")
    print(f"\n📊 Check your reports at:")
    print(f"   {API_BASE_URL}/reports")
    print(f"   {API_BASE_URL}/docs")


if __name__ == "__main__":
    populate_reports()
