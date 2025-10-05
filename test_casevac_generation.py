"""
Test CASEVAC generation endpoint to verify the database fix.
"""

import requests
import json

BASE_URL = "https://military-hierarchy-backend.onrender.com/"

def test_casevac_generation():
    """Test CASEVAC generation with sample data."""
    
    print("🚑 Testing CASEVAC Generation...")
    print("-" * 50)
    
    # Sample CASEVAC fields
    casevac_fields = {
        "location": "NV123456 (Grid coordinates)",
        "callsign_frequency": "30.55 MHz / DUSTOFF 23",
        "precedence": "A",  # URGENT
        "special_equipment": "A",  # None
        "patients": "2L 1A",  # 2 litter, 1 ambulatory
        "security": "N",  # No enemy
        "marking_method": "C",  # Smoke
        "nationality": "A",  # US Military
        "nbc_contamination": "N"  # None
    }
    
    # Generate CASEVAC
    try:
        response = requests.post(
            f"{BASE_URL}/casevac/generate",
            json={
                "unit_id": "ALPHA",
                "unit_name": "Alpha Company",
                "casevac_fields": casevac_fields,
                "source_report_ids": ["test-report-1"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CASEVAC Generated Successfully!")
            print(f"\nCASEVAC ID: {data['casevac_id']}")
            print(f"CASEVAC Number: {data['casevac_number']:04d}")
            print(f"Timestamp: {data['timestamp']}")
            print("\n" + "=" * 50)
            print("FORMATTED DOCUMENT:")
            print("=" * 50)
            print(data['formatted_document'])
            print("=" * 50)
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def verify_in_database():
    """Verify CASEVAC was saved to database."""
    import sqlite3
    
    print("\n📊 Verifying Database...")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect("military_hierarchy.db")
        c = conn.cursor()
        
        # Check latest CASEVAC
        c.execute("""
            SELECT report_id, report_type, timestamp, structured_json 
            FROM reports 
            WHERE report_type = 'CASEVAC' 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        row = c.fetchone()
        if row:
            report_id, report_type, timestamp, structured_json = row
            data = json.loads(structured_json)
            
            print(f"✅ Found CASEVAC in database!")
            print(f"\nReport ID: {report_id}")
            print(f"Report Type: {report_type}")
            print(f"Timestamp: {timestamp}")
            print(f"CASEVAC Number: {data.get('casevac_number')}")
            print(f"\nFields stored: {list(data.get('fields', {}).keys())}")
            print(f"Has formatted document: {'formatted_document' in data}")
            
            conn.close()
            return True
        else:
            print("❌ No CASEVAC found in database")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CASEVAC GENERATION TEST")
    print("=" * 50 + "\n")
    
    # Test generation
    generation_success = test_casevac_generation()
    
    if generation_success:
        # Verify in database
        db_success = verify_in_database()
        
        if db_success:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n⚠️ Generation succeeded but database verification failed")
    else:
        print("\n❌ GENERATION FAILED - Check backend logs")
