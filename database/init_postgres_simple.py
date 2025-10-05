"""
SIMPLE PostgreSQL initialization - no fancy migrations, just works.
This drops EVERYTHING and recreates from scratch.
"""
import os
import sys
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple schema - matches backend.py exactly
SCHEMA = """
-- NUCLEAR OPTION: Drop everything first
DROP TABLE IF EXISTS suggestions CASCADE;
DROP TABLE IF EXISTS fragos CASCADE;
DROP TABLE IF EXISTS frago_sequence CASCADE;
DROP TABLE IF EXISTS report_sequences CASCADE;
DROP TABLE IF EXISTS device_status CASCADE;
DROP TABLE IF EXISTS comm_log CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS soldier_raw_inputs CASCADE;
DROP TABLE IF EXISTS soldiers CASCADE;
DROP TABLE IF EXISTS units CASCADE;

-- UNITS
CREATE TABLE units (
    unit_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_unit_id TEXT,
    level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SOLDIERS
CREATE TABLE soldiers (
    soldier_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    rank TEXT,
    unit_id TEXT,
    device_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- SOLDIER RAW INPUTS
CREATE TABLE soldier_raw_inputs (
    input_id TEXT PRIMARY KEY,
    soldier_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text TEXT,
    raw_audio_ref TEXT,
    input_type TEXT DEFAULT 'voice',
    confidence REAL DEFAULT 0.0,
    location_ref TEXT,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id)
);

-- REPORTS
CREATE TABLE reports (
    report_id TEXT PRIMARY KEY,
    soldier_id TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_type TEXT NOT NULL,
    structured_json TEXT,
    confidence REAL DEFAULT 0.0,
    status TEXT DEFAULT 'active',
    priority TEXT,
    location TEXT,
    description TEXT,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id),
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- DEVICE STATUS
CREATE TABLE device_status (
    status_id TEXT PRIMARY KEY,
    soldier_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    battery_level INTEGER,
    signal_strength INTEGER,
    gps_status TEXT,
    location_lat REAL,
    location_lon REAL,
    FOREIGN KEY(soldier_id) REFERENCES soldiers(soldier_id)
);

-- COMM LOG
CREATE TABLE comm_log (
    log_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    from_soldier_id TEXT,
    to_soldier_id TEXT,
    message_type TEXT,
    message_content TEXT,
    status TEXT
);

-- FRAGOS
CREATE TABLE fragos (
    frago_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft',
    deadline TIMESTAMP,
    frago_number INTEGER,
    suggested_fields TEXT,
    final_fields TEXT,
    formatted_document TEXT,
    source_reports TEXT,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- FRAGO SEQUENCE
CREATE TABLE frago_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    next_number INTEGER NOT NULL DEFAULT 1
);

-- SUGGESTIONS (matches backend.py INSERT exactly)
CREATE TABLE suggestions (
    suggestion_id TEXT PRIMARY KEY,
    suggestion_type TEXT NOT NULL,
    urgency TEXT NOT NULL,
    reason TEXT NOT NULL,
    confidence REAL NOT NULL,
    source_reports TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    unit_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by TEXT,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- REPORT SEQUENCES
CREATE TABLE report_sequences (
    report_type TEXT PRIMARY KEY,
    next_number INTEGER NOT NULL DEFAULT 1
);

-- INDEXES
CREATE INDEX idx_soldiers_unit ON soldiers(unit_id);
CREATE INDEX idx_reports_unit ON reports(unit_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_suggestions_unit ON suggestions(unit_id);
CREATE INDEX idx_suggestions_status ON suggestions(status);
"""

SAMPLE_DATA = """
-- Sample Units
INSERT INTO units (unit_id, name, parent_unit_id, level) VALUES 
('BAT_1', '1st Infantry Battalion', NULL, 'Battalion'),
('CO_A', 'Alpha Company', 'BAT_1', 'Company'),
('PLT_1', '1st Platoon', 'CO_A', 'Platoon'),
('SQD_1', '1st Squad', 'PLT_1', 'Squad');

-- Sample Soldiers
INSERT INTO soldiers (soldier_id, name, rank, unit_id, device_id) VALUES 
('S001', 'John Smith', 'SGT', 'SQD_1', 'DEV001'),
('S002', 'Jane Doe', 'CPL', 'SQD_1', 'DEV002');

-- Sample Report
INSERT INTO reports (report_id, soldier_id, unit_id, timestamp, report_type, structured_json, confidence) VALUES 
('REPORT_001', 'S001', 'SQD_1', NOW(), 'CASUALTY', '{"casualties": 2, "severity": "critical", "location": "Grid 12345"}', 0.95);

-- Sample Suggestion (matches backend.py column order EXACTLY)
INSERT INTO suggestions (suggestion_id, suggestion_type, urgency, reason, confidence, source_reports, status, unit_id, created_at) VALUES 
('SUGG_001', 'CASEVAC', 'HIGH', 'Critical casualties detected', 0.95, '["REPORT_001"]', 'pending', 'PLT_1', NOW());

-- Init sequences
INSERT INTO frago_sequence (id, next_number) VALUES (1, 1);
INSERT INTO report_sequences (report_type, next_number) VALUES ('CASEVAC', 1), ('EOINCREP', 1);
"""

def main():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL not set!")
        sys.exit(1)
    
    try:
        logger.info("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logger.info("💣 Dropping all tables...")
        logger.info("📝 Creating schema...")
        cursor.execute(SCHEMA)
        
        logger.info("📦 Inserting sample data...")
        cursor.execute(SAMPLE_DATA)
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [t[0] for t in cursor.fetchall()]
        logger.info(f"✅ Created tables: {tables}")
        
        cursor.execute("SELECT COUNT(*) FROM suggestions")
        count = cursor.fetchone()[0]
        logger.info(f"✅ Suggestions: {count} rows")
        
        cursor.close()
        conn.close()
        
        logger.info("✅✅✅ Database initialized successfully! ✅✅✅")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
