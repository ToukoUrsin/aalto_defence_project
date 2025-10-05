-- Migration: Add missing tables for smart notifications and report sequences
-- Date: 2025-10-05
-- Description: Adds suggestions, report_sequences, and updates fragos table schema

-- =====================================================
-- SUGGESTIONS TABLE - AI-Generated Smart Notifications
-- =====================================================
CREATE TABLE IF NOT EXISTS suggestions (
    suggestion_id TEXT PRIMARY KEY,
    suggestion_type TEXT NOT NULL,              -- CASEVAC, EOINCREP, etc.
    urgency TEXT NOT NULL,                      -- URGENT, HIGH, MEDIUM, LOW
    reason TEXT NOT NULL,                       -- Human-readable reason
    confidence REAL NOT NULL,                   -- AI confidence (0.0-1.0)
    source_reports TEXT NOT NULL,               -- JSON array of report IDs
    status TEXT DEFAULT 'pending',              -- pending, accepted, rejected
    unit_id TEXT,                               -- Target unit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by TEXT,
    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
);

-- =====================================================
-- REPORT SEQUENCES TABLE - Auto-incrementing report numbers
-- =====================================================
CREATE TABLE IF NOT EXISTS report_sequences (
    report_type TEXT PRIMARY KEY,               -- CASEVAC, EOINCREP, FRAGO, etc.
    next_number INTEGER NOT NULL DEFAULT 1      -- Next available number
);

-- Initialize common report sequence types
INSERT INTO report_sequences (report_type, next_number) VALUES 
    ('CASEVAC', 1),
    ('EOINCREP', 1),
    ('FRAGO', 1),
    ('OPORD', 1)
ON CONFLICT (report_type) DO NOTHING;

-- =====================================================
-- FRAGO SEQUENCE TABLE - Legacy compatibility
-- =====================================================
CREATE TABLE IF NOT EXISTS frago_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    next_number INTEGER NOT NULL DEFAULT 1
);

-- Initialize FRAGO sequence
INSERT INTO frago_sequence (id, next_number) VALUES (1, 1)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- UPDATE FRAGOS TABLE - Add missing fields
-- =====================================================
-- Note: IF NOT EXISTS doesn't work for columns, so we use a safer approach

DO $$ 
BEGIN
    -- Add suggested_fields column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fragos' AND column_name = 'suggested_fields'
    ) THEN
        ALTER TABLE fragos ADD COLUMN suggested_fields TEXT;
    END IF;

    -- Add final_fields column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fragos' AND column_name = 'final_fields'
    ) THEN
        ALTER TABLE fragos ADD COLUMN final_fields TEXT;
    END IF;

    -- Add formatted_document column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fragos' AND column_name = 'formatted_document'
    ) THEN
        ALTER TABLE fragos ADD COLUMN formatted_document TEXT;
    END IF;

    -- Add source_reports column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fragos' AND column_name = 'source_reports'
    ) THEN
        ALTER TABLE fragos ADD COLUMN source_reports TEXT;
    END IF;

    -- Add frago_number column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fragos' AND column_name = 'frago_number'
    ) THEN
        ALTER TABLE fragos ADD COLUMN frago_number INTEGER;
    END IF;
END $$;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_suggestions_unit ON suggestions(unit_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_status ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_urgency ON suggestions(urgency);
CREATE INDEX IF NOT EXISTS idx_suggestions_type ON suggestions(suggestion_type);
CREATE INDEX IF NOT EXISTS idx_fragos_number ON fragos(frago_number);

-- =====================================================
-- VERIFICATION
-- =====================================================
-- Check that all tables exist
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('suggestions', 'report_sequences', 'frago_sequence');
    
    RAISE NOTICE 'Migration complete: % new tables created', table_count;
END $$;
