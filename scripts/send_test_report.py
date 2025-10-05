#!/usr/bin/env python3
"""
Quick test script to send a report to the backend API
"""

import requests
import json
from datetime import datetime

# Backend URL
API_BASE = "https://military-hierarchy-backend.onrender.com/"

# Example report data
def send_sitrep():
    """Send a Situation Report"""
    report = {
        "report_type": "SITREP",
        "structured_json": {
            "location": "Grid 38.8977, 77.0365",
            "status": "Perimeter secure, all checkpoints manned",
            "personnel_count": 12,
            "equipment_status": "Operational",
            "timestamp": datetime.now().isoformat()
        },
        "confidence": 0.95
    }
    
    response = requests.post(f"{API_BASE}/soldiers/S001/reports", json=report)
    print(f"✅ SITREP sent: {response.json()}")

def send_casevac():
    """Send a CASEVAC (Casualty Evacuation) Report"""
    report = {
        "report_type": "CASEVAC",
        "structured_json": {
            "casualties": 2,
            "location": "Grid 38.9072, 77.0369",
            "priority": "IMMEDIATE",
            "description": "2x gunshot wounds, stable condition",
            "evac_requested": True,
            "timestamp": datetime.now().isoformat()
        },
        "confidence": 0.98
    }
    
    response = requests.post(f"{API_BASE}/soldiers/S002/reports", json=report)
    print(f"🚑 CASEVAC sent: {response.json()}")

def send_eoincrep():
    """Send an Enemy Observation/Incident Report"""
    report = {
        "report_type": "EOINCREP",
        "structured_json": {
            "enemy_count": 6,
            "location": "Grid 38.8850, 77.0340",
            "direction": "North",
            "description": "Enemy patrol spotted, 6 personnel moving north",
            "equipment": ["Small arms"],
            "timestamp": datetime.now().isoformat()
        },
        "confidence": 0.92
    }
    
    response = requests.post(f"{API_BASE}/soldiers/S003/reports", json=report)
    print(f"⚠️  EOINCREP sent: {response.json()}")

if __name__ == "__main__":
    print("📡 Sending test reports to backend...\n")
    
    try:
        send_sitrep()
        send_casevac()
        send_eoincrep()
        
        print("\n✅ All reports sent successfully!")
        print("🔍 Check the dashboard at http://localhost:3000")
        print("📊 View all reports: https://military-hierarchy-backend.onrender.com//reports")
        
    except Exception as e:
        print(f"❌ Error sending reports: {e}")
        print("Make sure the backend is running at https://military-hierarchy-backend.onrender.com/")
