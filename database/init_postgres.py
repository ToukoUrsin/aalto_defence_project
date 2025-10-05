#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script for Render Deployment
Converts SQLite schema to PostgreSQL and initializes the database.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL schema - adapted from SQLite schema
POSTGRES_SCHEMA = """
-- Military Hierarchy Database Schema (PostgreSQL)

-- UNITS TABLE - Hierarchical Military Organization
CREATE TABLE IF NOT EXISTS units (
    unit_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_unit_id TEXT,
    level TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_unit_id) REFERENCES units(unit_id)
);

-- SOLDIERS TABLE - Individual Personnel Records
CREATE TABLE IF NOT EXISTS soldiers (
    soldier_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    rank TEXT,
    unit_id TEXT NOT NULL,
    device_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- RAW INPUTS TABLE - Complete Voice/Text Input History
CREATE TABLE IF NOT EXISTS soldier_raw_inputs (
    input_id TEXT PRIMARY KEY,
    soldier_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    raw_text TEXT NOT NULL,
    raw_audio_ref TEXT,
    input_type TEXT DEFAULT 'voice',
    confidence REAL DEFAULT 0.0,
    location_ref TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id)
);

-- REPORTS TABLE - AI-Generated Structured Reports
CREATE TABLE IF NOT EXISTS reports (
    report_id TEXT PRIMARY KEY,
    soldier_id TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    report_type TEXT NOT NULL,
    structured_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id),
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- Add optional columns to reports table if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='reports' AND column_name='source_input_id') THEN
        ALTER TABLE reports ADD COLUMN source_input_id TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='reports' AND column_name='status') THEN
        ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'generated';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='reports' AND column_name='reviewed_by') THEN
        ALTER TABLE reports ADD COLUMN reviewed_by TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='reports' AND column_name='reviewed_at') THEN
        ALTER TABLE reports ADD COLUMN reviewed_at TIMESTAMP;
    END IF;
END $$;

-- DEVICE STATUS TABLE
CREATE TABLE IF NOT EXISTS device_status (
    device_id TEXT PRIMARY KEY,
    soldier_id TEXT,
    status TEXT DEFAULT 'active',
    last_heartbeat TIMESTAMP,
    battery_level INTEGER,
    signal_strength INTEGER,
    location_lat REAL,
    location_lon REAL,
    location_accuracy REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id)
);

-- COMMUNICATION LOG TABLE
CREATE TABLE IF NOT EXISTS comm_log (
    log_id TEXT PRIMARY KEY,
    device_id TEXT,
    soldier_id TEXT,
    topic TEXT NOT NULL,
    message_type TEXT NOT NULL,
    message_size INTEGER,
    timestamp TIMESTAMP NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id)
);

-- FRAGOS TABLE (Fragmentary Orders)
CREATE TABLE IF NOT EXISTS fragos (
    frago_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    task TEXT,
    assigned_by TEXT,
    assigned_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- Add missing columns to fragos table if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='fragos' AND column_name='frago_number') THEN
        ALTER TABLE fragos ADD COLUMN frago_number INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='fragos' AND column_name='suggested_fields') THEN
        ALTER TABLE fragos ADD COLUMN suggested_fields TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='fragos' AND column_name='final_fields') THEN
        ALTER TABLE fragos ADD COLUMN final_fields TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='fragos' AND column_name='formatted_document') THEN
        ALTER TABLE fragos ADD COLUMN formatted_document TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='fragos' AND column_name='source_reports') THEN
        ALTER TABLE fragos ADD COLUMN source_reports TEXT;
    END IF;
END $$;

-- FRAGO SEQUENCE TABLE (Legacy compatibility)
CREATE TABLE IF NOT EXISTS frago_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    next_number INTEGER NOT NULL DEFAULT 1
);

-- SUGGESTIONS TABLE (AI-Generated Smart Notifications)
-- Drop and recreate to ensure clean schema (fixes column order issues from old deployments)
DROP TABLE IF EXISTS suggestions CASCADE;
CREATE TABLE suggestions (
    suggestion_id TEXT PRIMARY KEY,
    suggestion_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    unit_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- Add missing columns to suggestions table if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='urgency') THEN
        ALTER TABLE suggestions ADD COLUMN urgency TEXT NOT NULL DEFAULT 'MEDIUM';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='reason') THEN
        ALTER TABLE suggestions ADD COLUMN reason TEXT NOT NULL DEFAULT 'Automated suggestion';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='confidence') THEN
        ALTER TABLE suggestions ADD COLUMN confidence REAL NOT NULL DEFAULT 0.8;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='source_reports') THEN
        ALTER TABLE suggestions ADD COLUMN source_reports TEXT NOT NULL DEFAULT '[]';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='reviewed_at') THEN
        ALTER TABLE suggestions ADD COLUMN reviewed_at TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='suggestions' AND column_name='reviewed_by') THEN
        ALTER TABLE suggestions ADD COLUMN reviewed_by TEXT;
    END IF;
END $$;

-- REPORT SEQUENCES TABLE (Auto-incrementing report numbers)
CREATE TABLE IF NOT EXISTS report_sequences (
    report_type TEXT PRIMARY KEY,
    next_number INTEGER NOT NULL DEFAULT 1
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_units_parent ON units(parent_unit_id);
CREATE INDEX IF NOT EXISTS idx_units_level ON units(level);
CREATE INDEX IF NOT EXISTS idx_soldiers_unit ON soldiers(unit_id);
CREATE INDEX IF NOT EXISTS idx_soldiers_device ON soldiers(device_id);
CREATE INDEX IF NOT EXISTS idx_soldiers_status ON soldiers(status);
CREATE INDEX IF NOT EXISTS idx_raw_inputs_soldier ON soldier_raw_inputs(soldier_id);
CREATE INDEX IF NOT EXISTS idx_raw_inputs_timestamp ON soldier_raw_inputs(timestamp);
CREATE INDEX IF NOT EXISTS idx_reports_soldier ON reports(soldier_id);
CREATE INDEX IF NOT EXISTS idx_reports_unit ON reports(unit_id);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON reports(timestamp);
CREATE INDEX IF NOT EXISTS idx_device_status_soldier ON device_status(soldier_id);
CREATE INDEX IF NOT EXISTS idx_comm_log_timestamp ON comm_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_fragos_unit ON fragos(unit_id);
CREATE INDEX IF NOT EXISTS idx_fragos_status ON fragos(status);
CREATE INDEX IF NOT EXISTS idx_fragos_number ON fragos(frago_number);
CREATE INDEX IF NOT EXISTS idx_suggestions_unit ON suggestions(unit_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_status ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_urgency ON suggestions(urgency);
CREATE INDEX IF NOT EXISTS idx_suggestions_type ON suggestions(suggestion_type);
"""

# Sample data for testing
SAMPLE_DATA = """
-- Initialize FRAGO sequence
INSERT INTO frago_sequence (id, next_number) VALUES (1, 1)
ON CONFLICT (id) DO NOTHING;

-- Initialize report sequences
INSERT INTO report_sequences (report_type, next_number) VALUES 
    ('CASEVAC', 1),
    ('EOINCREP', 1),
    ('FRAGO', 1),
    ('OPORD', 1)
ON CONFLICT (report_type) DO NOTHING;

-- Sample Units
INSERT INTO units (unit_id, name, parent_unit_id, level) VALUES 
('BAT_1', '1st Infantry Battalion', NULL, 'Battalion'),
('CO_A', 'Alpha Company', 'BAT_1', 'Company'),
('CO_B', 'Bravo Company', 'BAT_1', 'Company'),
('PLT_1', '1st Platoon', 'CO_A', 'Platoon'),
('PLT_2', '2nd Platoon', 'CO_A', 'Platoon'),
('PLT_3', '3rd Platoon', 'CO_B', 'Platoon'),
('SQD_1', '1st Squad', 'PLT_1', 'Squad'),
('SQD_2', '2nd Squad', 'PLT_1', 'Squad'),
('SQD_3', '3rd Squad', 'PLT_2', 'Squad')
ON CONFLICT (unit_id) DO NOTHING;

-- Sample Soldiers
INSERT INTO soldiers (soldier_id, name, rank, unit_id, device_id, status, last_seen) VALUES 
('ALPHA_01', 'Lt. John Smith', 'Lieutenant', 'PLT_1', 'DEVICE_001', 'active', NOW() - INTERVAL '5 minutes'),
('ALPHA_02', 'Sgt. Mike Johnson', 'Sergeant', 'SQD_1', 'DEVICE_002', 'active', NOW() - INTERVAL '2 minutes'),
('ALPHA_03', 'Pvt. David Wilson', 'Private', 'SQD_1', 'DEVICE_003', 'active', NOW() - INTERVAL '1 minute'),
('ALPHA_04', 'Cpl. Sarah Brown', 'Corporal', 'SQD_2', 'DEVICE_004', 'active', NOW() - INTERVAL '3 minutes'),
('BRAVO_01', 'Capt. Tom Davis', 'Captain', 'CO_B', 'DEVICE_005', 'active', NOW() - INTERVAL '10 minutes')
ON CONFLICT (soldier_id) DO NOTHING;

-- Sample Raw Inputs
INSERT INTO soldier_raw_inputs (input_id, soldier_id, timestamp, raw_text, input_type, confidence) VALUES 
('INPUT_001', 'ALPHA_02', NOW() - INTERVAL '30 minutes', 'We have a soldier down with gunshot wound to the leg. Need immediate CASEVAC at grid 38SMB 123 456.', 'voice', 0.95),
('INPUT_002', 'ALPHA_04', NOW() - INTERVAL '45 minutes', 'Found suspicious device buried by roadside. Appears to be IED. Requesting EOD team.', 'voice', 0.92),
('INPUT_003', 'ALPHA_01', NOW() - INTERVAL '1 hour', 'Patrol complete. All personnel accounted for. Returning to base.', 'voice', 0.98),
('INPUT_004', 'BRAVO_01', NOW() - INTERVAL '2 hours', 'Enemy contact at grid 38SMB 789 012. 8-10 personnel with small arms. Engaging.', 'voice', 0.89),
('INPUT_005', 'ALPHA_03', NOW() - INTERVAL '15 minutes', 'Vehicle checkpoint established. Light civilian traffic observed.', 'voice', 0.94)
ON CONFLICT (input_id) DO NOTHING;

-- Sample Reports
INSERT INTO reports (report_id, soldier_id, unit_id, timestamp, report_type, structured_json, confidence, source_input_id, status) VALUES 
('REPORT_001', 'ALPHA_02', 'SQD_1', NOW() - INTERVAL '30 minutes', 'CASEVAC', 
'{"casualties": [{"name": "Pvt. Williams", "injury": "Gunshot wound to left leg", "severity": "URGENT", "status": "Stable"}], "location": "Grid 38SMB 123 456", "evacuation_point": "LZ Alpha", "urgency": "URGENT", "enemy_activity": "Sporadic small arms fire", "security": "Secured by squad element"}', 
0.95, 'INPUT_001', 'generated'),

('REPORT_002', 'ALPHA_04', 'SQD_2', NOW() - INTERVAL '45 minutes', 'EOINCREP',
'{"incident_type": "IED Discovery", "location": "Grid 38SMB 456 789", "description": "Suspected IED found buried at roadside, wires visible", "threat_level": "HIGH", "action_taken": "Area cordoned off, EOD team requested", "casualties": "None", "time_discovered": "14:30"}',
0.92, 'INPUT_002', 'generated'),

('REPORT_003', 'ALPHA_01', 'PLT_1', NOW() - INTERVAL '1 hour', 'SITREP',
'{"unit": "1st Platoon", "location": "Patrol Route Alpha", "situation": "Patrol completed successfully", "enemy_activity": "None observed", "friendly_forces": "All personnel accounted for", "logistics": "Supplies adequate", "next_action": "Return to base for debrief"}',
0.98, 'INPUT_003', 'generated'),

('REPORT_004', 'BRAVO_01', 'CO_B', NOW() - INTERVAL '2 hours', 'SPOTREP',
'{"what": "Enemy patrol, 8-10 personnel with small arms", "when": "14:45 local time", "where": "Grid 38SMB 789 012", "activity": "Moving north along ridgeline", "assessment": "Likely reconnaissance element", "action_taken": "Engaging enemy forces"}',
0.89, 'INPUT_004', 'generated'),

('REPORT_005', 'ALPHA_03', 'SQD_1', NOW() - INTERVAL '15 minutes', 'SITREP',
'{"unit": "1st Squad", "location": "Checkpoint Delta", "situation": "Maintaining checkpoint security", "enemy_activity": "None observed", "friendly_forces": "Full strength", "logistics": "Supplies adequate", "next_action": "Continue checkpoint operations"}',
0.94, 'INPUT_005', 'generated')
ON CONFLICT (report_id) DO NOTHING;

-- Sample Device Status
INSERT INTO device_status (device_id, soldier_id, status, last_heartbeat, battery_level, signal_strength, location_lat, location_lon) VALUES 
('DEVICE_001', 'ALPHA_01', 'active', NOW() - INTERVAL '5 minutes', 85, 75, 60.1699, 24.9384),
('DEVICE_002', 'ALPHA_02', 'active', NOW() - INTERVAL '2 minutes', 92, 82, 60.1705, 24.9390),
('DEVICE_003', 'ALPHA_03', 'active', NOW() - INTERVAL '1 minute', 78, 68, 60.1695, 24.9388),
('DEVICE_004', 'ALPHA_04', 'active', NOW() - INTERVAL '3 minutes', 88, 79, 60.1701, 24.9385),
('DEVICE_005', 'BRAVO_01', 'active', NOW() - INTERVAL '10 minutes', 65, 71, 60.1710, 24.9395)
ON CONFLICT (device_id) DO NOTHING;

-- Sample FRAGOs
INSERT INTO fragos (frago_id, unit_id, task, assigned_by, assigned_at, status, priority, deadline) VALUES 
('FRAGO_001', 'PLT_1', 'Establish checkpoint at Grid 38SMB 234 567 from 0600 to 1800', 'CO_A', NOW() - INTERVAL '6 hours', 'completed', 'high', NOW() + INTERVAL '12 hours'),
('FRAGO_002', 'SQD_1', 'Patrol Route Bravo and report any suspicious activity', 'PLT_1', NOW() - INTERVAL '3 hours', 'in_progress', 'medium', NOW() + INTERVAL '6 hours'),
('FRAGO_003', 'CO_B', 'Conduct area reconnaissance of sector 7', 'BAT_1', NOW() - INTERVAL '1 hour', 'pending', 'high', NOW() + INTERVAL '24 hours')
ON CONFLICT (frago_id) DO NOTHING;

-- Sample Suggestions (Smart Notifications)
-- Note: Using explicit column names to match the migrated schema
INSERT INTO suggestions (suggestion_id, suggestion_type, status, unit_id, created_at, urgency, reason, confidence, source_reports) VALUES 
('SUGG_001', 'CASEVAC', 'pending', 'PLT_1', NOW(), 'HIGH', 'Critical casualties detected requiring immediate evacuation', 0.95, '["REPORT_001"]'),
('SUGG_002', 'EOINCREP', 'pending', 'SQD_2', NOW(), 'HIGH', 'Explosive ordnance detected - EOD team required', 0.92, '["REPORT_002"]'),
('SUGG_003', 'EOINCREP', 'pending', 'CO_B', NOW(), 'MEDIUM', 'Enemy contact reported - tactical assessment needed', 0.89, '["REPORT_004"]')
ON CONFLICT (suggestion_id) DO NOTHING;
"""


def initialize_database():
    """Initialize PostgreSQL database with schema and sample data."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        sys.exit(1)
    
    try:
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logger.info("Creating database schema...")
        cursor.execute(POSTGRES_SCHEMA)
        
        logger.info("Inserting sample data...")
        cursor.execute(SAMPLE_DATA)
        
        conn.commit()
        logger.info("✅ Database initialized successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        logger.info(f"Created tables: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    initialize_database()
