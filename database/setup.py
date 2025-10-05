import sqlite3
import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from schema_definition import MilitaryHierarchySchema

def initialize_database():
    """Initialize the military hierarchy database with all required tables."""
    conn = sqlite3.connect("military_hierarchy.db")
    
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    
    c = conn.cursor()

    # Get the complete schema definition
    schema = MilitaryHierarchySchema()
    
    # Create all tables using the schema definition
    for table_name in schema.get_table_names():
        create_sql = schema.generate_create_table_sql(table_name)
        c.execute(create_sql)
        print(f"Created table: {table_name}")

    # Create indexes
    for table_name, table_schema in schema.tables.items():
        for index_name in table_schema.indexes:
            # Generate index creation SQL based on index name
            if 'parent' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON units(parent_unit_id);")
            elif 'level' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON units(level);")
            elif 'soldier' in index_name and 'unit' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldiers(unit_id);")
            elif 'soldier' in index_name and 'device' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldiers(device_id);")
            elif 'soldier' in index_name and 'status' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldiers(status);")
            elif 'raw_inputs' in index_name and 'soldier' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldier_raw_inputs(soldier_id);")
            elif 'raw_inputs' in index_name and 'timestamp' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldier_raw_inputs(timestamp);")
            elif 'raw_inputs' in index_name and 'type' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON soldier_raw_inputs(input_type);")
            elif 'reports' in index_name and 'soldier' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON reports(soldier_id);")
            elif 'reports' in index_name and 'unit' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON reports(unit_id);")
            elif 'reports' in index_name and 'type' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON reports(report_type);")
            elif 'reports' in index_name and 'timestamp' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON reports(timestamp);")
            elif 'reports' in index_name and 'status' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON reports(status);")
            elif 'device' in index_name and 'soldier' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON device_status(soldier_id);")
            elif 'device' in index_name and 'heartbeat' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON device_status(last_heartbeat);")
            elif 'comm_log' in index_name and 'device' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON comm_log(device_id);")
            elif 'comm_log' in index_name and 'soldier' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON comm_log(soldier_id);")
            elif 'comm_log' in index_name and 'timestamp' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON comm_log(timestamp);")
            elif 'comm_log' in index_name and 'topic' in index_name:
                c.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON comm_log(topic);")

    conn.commit()
    conn.close()
    print("Database initialized successfully with all tables and indexes.")

def add_sample_data():
    """Add sample military hierarchy data for demonstration."""
    import uuid
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect("military_hierarchy.db")
    c = conn.cursor()

    # Clear existing data
    c.execute("DELETE FROM reports")
    c.execute("DELETE FROM soldier_raw_inputs")
    c.execute("DELETE FROM soldiers")
    c.execute("DELETE FROM units")

    # Add sample units (Battalion -> Company -> Platoon -> Squad)
    units_data = [
        ("BAT_1", "1st Infantry Battalion", None, "Battalion", datetime.now().isoformat()),
        ("CO_A", "Alpha Company", "BAT_1", "Company", datetime.now().isoformat()),
        ("CO_B", "Bravo Company", "BAT_1", "Company", datetime.now().isoformat()),
        ("PLT_1", "1st Platoon", "CO_A", "Platoon", datetime.now().isoformat()),
        ("PLT_2", "2nd Platoon", "CO_A", "Platoon", datetime.now().isoformat()),
        ("SQD_1", "1st Squad", "PLT_1", "Squad", datetime.now().isoformat()),
        ("SQD_2", "2nd Squad", "PLT_1", "Squad", datetime.now().isoformat()),
        ("SQD_3", "3rd Squad", "PLT_2", "Squad", datetime.now().isoformat()),
    ]

    for unit_data in units_data:
        c.execute("INSERT INTO units VALUES (?, ?, ?, ?, ?)", unit_data)

    # Add sample soldiers (with new columns)
    soldiers_data = [
        ("ALPHA_01", "Lt. John Smith", "Lieutenant", "PLT_1", "DEVICE_001", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=5)).isoformat()),
        ("ALPHA_02", "Sgt. Mike Johnson", "Sergeant", "SQD_1", "DEVICE_002", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=3)).isoformat()),
        ("ALPHA_03", "Pvt. David Wilson", "Private", "SQD_1", "DEVICE_003", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=2)).isoformat()),
        ("ALPHA_04", "Cpl. Sarah Brown", "Corporal", "SQD_2", "DEVICE_004", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=1)).isoformat()),
        ("BRAVO_01", "Capt. Tom Davis", "Captain", "CO_B", "DEVICE_005", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=4)).isoformat()),
        ("BRAVO_02", "Sgt. Lisa Garcia", "Sergeant", "PLT_2", "DEVICE_006", "active", datetime.now().isoformat(), (datetime.now() - timedelta(minutes=6)).isoformat()),
    ]

    for soldier_data in soldiers_data:
        c.execute("INSERT INTO soldiers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", soldier_data)

    # Add sample raw inputs (with new columns)

    raw_inputs_data = [
        (str(uuid.uuid4()), "ALPHA_01", (datetime.now() - timedelta(minutes=30)).isoformat(), 
         "Enemy vehicle spotted north of the road, looks like a T-72 tank", "audio_001.wav", "voice", 0.95, "Grid 123-456", datetime.now().isoformat()),
        (str(uuid.uuid4()), "ALPHA_02", (datetime.now() - timedelta(minutes=25)).isoformat(), 
         "Squad is in position, no contact yet", "audio_002.wav", "voice", 0.88, "Grid 123-457", datetime.now().isoformat()),
        (str(uuid.uuid4()), "ALPHA_03", (datetime.now() - timedelta(minutes=20)).isoformat(), 
         "Need medical evacuation, one casualty at grid 123-456", "audio_003.wav", "voice", 0.92, "Grid 123-456", datetime.now().isoformat()),
        (str(uuid.uuid4()), "ALPHA_04", (datetime.now() - timedelta(minutes=15)).isoformat(), 
         "Moving to secondary position, will report when in place", "audio_004.wav", "voice", 0.85, "Grid 123-458", datetime.now().isoformat()),
        (str(uuid.uuid4()), "BRAVO_01", (datetime.now() - timedelta(minutes=10)).isoformat(), 
         "Company is advancing on objective, all platoons moving", "audio_005.wav", "voice", 0.90, "Grid 124-456", datetime.now().isoformat()),
    ]

    for input_data in raw_inputs_data:
        c.execute("INSERT INTO soldier_raw_inputs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", input_data)

    # Add sample structured reports (with new columns)
    sample_reports = [
        (str(uuid.uuid4()), "ALPHA_01", "PLT_1", (datetime.now() - timedelta(minutes=28)).isoformat(),
         "EOINCREP", '{"unit": "Alpha-1", "location": "Grid 123-456", "threat_type": "T-72 Tank", "direction": "North", "confidence": 0.85}', 0.85, raw_inputs_data[0][0], "generated", None, None, datetime.now().isoformat()),
        (str(uuid.uuid4()), "ALPHA_03", "SQD_1", (datetime.now() - timedelta(minutes=18)).isoformat(),
         "CASEVAC", '{"unit": "Alpha-3", "location": "Grid 123-456", "casualty_count": 1, "urgency": "High", "status": "Requested", "confidence": 0.90}', 0.90, raw_inputs_data[2][0], "generated", None, None, datetime.now().isoformat()),
        (str(uuid.uuid4()), "BRAVO_01", "CO_B", (datetime.now() - timedelta(minutes=8)).isoformat(),
         "SITREP", '{"unit": "Bravo Company", "status": "Advancing", "objective": "Primary target", "all_units": "Moving", "confidence": 0.75}', 0.75, raw_inputs_data[4][0], "generated", None, None, datetime.now().isoformat()),
    ]

    for report_data in sample_reports:
        c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", report_data)

    conn.commit()
    conn.close()
    print("Sample data added successfully.")

if __name__ == "__main__":
    initialize_database()
    add_sample_data()
