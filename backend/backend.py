from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading
import logging
import google.generativeai as genai
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB2LVUXt2a9nMCpJwGJWen4_EECudv9u_c")
genai.configure(api_key=GEMINI_API_KEY)
# Use gemini-2.5-flash - fast model optimized for speed while maintaining quality
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="Military Hierarchy Backend", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration - auto-detect environment
DATABASE_URL = os.getenv("DATABASE_URL")  # Render/production provides this
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    # Production: Use PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info("Using PostgreSQL database")
else:
    # Local development: Use SQLite
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "military_hierarchy.db")
    logger.info(f"Using SQLite database at {DB_PATH}")

# Global MQTT client
mqtt_client = None

def get_db_connection():
    """Get a database connection (PostgreSQL or SQLite based on environment)."""
    if USE_POSTGRES:
        # PostgreSQL connection
        return psycopg2.connect(DATABASE_URL)
    else:
        # SQLite connection
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

def execute_query(query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False):
    """
    Execute a database query that works with both PostgreSQL and SQLite.
    Handles parameter placeholder differences (? for SQLite, %s for PostgreSQL).
    """
    conn = get_db_connection()
    try:
        # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s) if needed
        if USE_POSTGRES:
            query = query.replace("?", "%s")
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
            if USE_POSTGRES and result:
                result = dict(result)
            elif not USE_POSTGRES and result:
                result = dict(result)
            conn.close()
            return result
        elif fetch_all:
            results = cursor.fetchall()
            if USE_POSTGRES:
                results = [dict(row) for row in results]
            else:
                results = [dict(row) for row in results]
            conn.close()
            return results
        else:
            # For INSERT/UPDATE/DELETE
            conn.commit()
            conn.close()
            return None
    except Exception as e:
        conn.close()
        raise e

def generate_report_description(report_type: str, structured_json: Dict[str, Any]) -> str:
    """
    Generate a clean, human-readable description for a report based on its type and data.
    This makes frontend display clean and consistent.
    """
    try:
        if report_type == "CASUALTY" or report_type == "CASEVAC":
            casualties = structured_json.get("casualties", structured_json.get("casualty_count", "Unknown"))
            severity = structured_json.get("severity", "Unknown")
            location = structured_json.get("location", "Unknown location")
            injuries = structured_json.get("injuries", "")
            desc = f"{casualties} casualty(ies), {severity} severity at {location}"
            if injuries:
                desc += f" - {injuries}"
            return desc
            
        elif report_type == "CONTACT" or report_type == "EOINCREP":
            enemy_count = structured_json.get("enemy_count", "Unknown")
            location = structured_json.get("location", "Unknown location")
            enemy_type = structured_json.get("enemy_type", "enemy forces")
            activity = structured_json.get("activity", structured_json.get("description", ""))
            desc = f"{enemy_count} {enemy_type} at {location}"
            if activity:
                desc += f" - {activity}"
            return desc
            
        elif report_type == "SITREP":
            status = structured_json.get("status", structured_json.get("engagement_status", ""))
            location = structured_json.get("location", "")
            desc = status if status else "Situation report"
            if location:
                desc += f" at {location}"
            return desc
            
        elif report_type == "FRAGO":
            task = structured_json.get("task", structured_json.get("mission", ""))
            unit = structured_json.get("unit", "")
            desc = f"FRAGO: {task}" if task else "Fragmentary Order"
            if unit:
                desc += f" for {unit}"
            return desc
            
        elif report_type == "INTELLIGENCE" or report_type == "INTREP":
            observation = structured_json.get("observation", structured_json.get("description", ""))
            return observation if observation else "Intelligence report"
            
        elif report_type == "LOGSTAT":
            status = structured_json.get("status", structured_json.get("description", ""))
            return status if status else "Logistics status report"
            
        else:
            # Generic fallback
            if "description" in structured_json:
                return structured_json["description"]
            elif "observation" in structured_json:
                return structured_json["observation"]
            elif "status" in structured_json:
                return structured_json["status"]
            else:
                return f"{report_type} report"
                
    except Exception as e:
        logger.warning(f"Error generating description for {report_type}: {e}")
        return f"{report_type} report"

# ===== SMART NOTIFICATIONS SYSTEM - LEVEL 2 =====

def analyze_report_triggers(report_id: str, soldier_id: str, unit_id: str, 
                            report_type: str, structured_json: Dict[str, Any], 
                            text_content: str = ""):
    """
    Analyze newly created report for triggers that should generate suggestions.
    Level 2: Smart Notifications - suggests report creation to user.
    Level 3: Auto-Drafts - automatically generates draft reports (future).
    """
    triggers = []
    
    try:
        # Validate inputs
        if not structured_json:
            structured_json = {}
        
        # CASEVAC TRIGGERS - Detect casualty situations
        if report_type in ["CASUALTY", "CONTACT", "SITREP"]:
            try:
                casualties = structured_json.get("casualties", 0)
                severity = str(structured_json.get("severity", "")).lower()
                description = str(structured_json.get("description", "")).lower()
                text_lower = str(text_content).lower()
                
                # Check for casualties or injury keywords
                injury_keywords = ["wounded", "injured", "casualty", "casualties", "medevac", 
                                  "kia", "killed", "wia", "gunshot", "bleeding", "critical"]
                has_injury_keywords = any(keyword in text_lower or keyword in description 
                                         for keyword in injury_keywords)
                
                if casualties > 0 or has_injury_keywords:
                    # Determine urgency
                    urgency = "MEDIUM"
                    confidence = 0.75
                    reason = f"Potential casualties detected"
                    
                    # URGENT triggers
                    urgent_keywords = ["critical", "severe", "life-threatening", "kia", "killed"]
                    if any(kw in text_lower or kw in description for kw in urgent_keywords):
                        urgency = "URGENT"
                        confidence = 0.95
                        reason = f"URGENT: Critical casualties detected"
                    elif severity in ["critical", "severe"]:
                        urgency = "URGENT"
                        confidence = 0.95
                        reason = f"URGENT: {casualties} critical casualties"
                    elif casualties >= 1:
                        urgency = "HIGH"
                        confidence = 0.90
                        reason = f"{casualties} casualties reported"
                    
                    triggers.append({
                        "type": "CASEVAC",
                        "urgency": urgency,
                        "reason": reason,
                        "confidence": confidence,
                        "source_reports": [report_id]
                    })
            except Exception as e:
                logger.error(f"Error in CASEVAC trigger detection: {e}")
        
        # EOINCREP TRIGGERS - Detect enemy contact or explosive ordnance
        if report_type in ["CONTACT", "INTELLIGENCE", "SITREP"]:
            try:
                enemy_count = int(structured_json.get("enemy_count", 0))
                vehicle_count = int(structured_json.get("vehicle_count", 0))
                description = str(structured_json.get("description", "")).lower()
                text_lower = str(text_content).lower()
                
                # Enemy contact keywords
                enemy_keywords = ["enemy", "hostile", "contact", "engagement", "patrol", 
                                 "infantry", "armor", "artillery"]
                has_enemy_keywords = any(keyword in text_lower or keyword in description 
                                        for keyword in enemy_keywords)
                
                if enemy_count > 0 or has_enemy_keywords:
                    # Determine urgency based on enemy size
                    urgency = "MEDIUM"
                    confidence = 0.80
                    reason = "Enemy activity detected"
                    
                    if enemy_count > 10 or vehicle_count > 2:
                        urgency = "HIGH"
                        confidence = 0.90
                        reason = f"Significant enemy force: {enemy_count} personnel, {vehicle_count} vehicles"
                    elif enemy_count > 0:
                        urgency = "MEDIUM"
                        confidence = 0.85
                        reason = f"Enemy contact: {enemy_count} hostiles"
                    
                    triggers.append({
                        "type": "EOINCREP",
                        "urgency": urgency,
                        "reason": reason,
                        "confidence": confidence,
                        "source_reports": [report_id]
                    })
            except Exception as e:
                logger.error(f"Error in EOINCREP trigger detection: {e}")
        
        # EOD EOINCREP TRIGGERS - Detect explosive devices
        try:
            eod_keywords = ["ied", "mine", "unexploded", "booby trap", "explosive", 
                           "ordnance", "bomb", "explosive device"]
            description = str(structured_json.get("description", "")).lower()
            text_lower = str(text_content).lower()
            
            has_eod_keywords = any(keyword in text_lower or keyword in description 
                                   for keyword in eod_keywords)
            
            if has_eod_keywords:
                triggers.append({
                    "type": "EOINCREP_EOD",
                    "urgency": "HIGH",
                    "reason": "Explosive ordnance/device detected",
                    "confidence": 0.85,
                    "source_reports": [report_id]
                })
        except Exception as e:
            logger.error(f"Error in EOD trigger detection: {e}")
        
        # Save triggers to suggestions table
        if triggers:
            create_suggestions(triggers, unit_id)
            logger.info(f"Created {len(triggers)} suggestions for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error analyzing report triggers: {e}", exc_info=True)
    
    return triggers

def create_suggestions(triggers: List[Dict[str, Any]], unit_id: str):
    """Save triggered suggestions to database."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        for trigger in triggers:
            suggestion_id = str(uuid.uuid4())
            
            c.execute("""
                INSERT INTO suggestions 
                (suggestion_id, suggestion_type, urgency, reason, confidence, 
                 source_reports, status, unit_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """, (
                suggestion_id,
                trigger["type"],
                trigger["urgency"],
                trigger["reason"],
                trigger["confidence"],
                json.dumps(trigger["source_reports"]),
                unit_id,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(triggers)} suggestions to database")
        
    except Exception as e:
        logger.error(f"Error creating suggestions: {e}")

# ===== END SMART NOTIFICATIONS SYSTEM =====

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe("soldiers/inputs")
        client.subscribe("soldiers/heartbeat")
    else:
        logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages from soldier devices."""
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        
        if topic == "soldiers/inputs":
            handle_soldier_input(payload)
        elif topic == "soldiers/heartbeat":
            handle_soldier_heartbeat(payload)
            
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def handle_soldier_input(payload: Dict[str, Any]):
    """Save soldier input to database."""
    try:
        soldier_id = payload.get('soldier_id')
        timestamp = payload.get('timestamp', datetime.now().isoformat())
        raw_text = payload.get('raw_text', '')
        audio_ref = payload.get('audio_file_ref')

        if not soldier_id or not raw_text:
            logger.warning("Invalid soldier input: missing soldier_id or raw_text")
            return

        conn = get_db_connection()
        c = conn.cursor()
        input_id = str(uuid.uuid4())
        
        c.execute("""
            INSERT INTO soldier_raw_inputs (input_id, soldier_id, timestamp, raw_text, raw_audio_ref)
            VALUES (?, ?, ?, ?, ?)
        """, (input_id, soldier_id, timestamp, raw_text, audio_ref))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved input from soldier {soldier_id} at {timestamp}")
        
        # Optionally trigger AI processing here
        # process_with_ai(input_id, raw_text)
        
    except Exception as e:
        logger.error(f"Error saving soldier input: {e}")

def handle_soldier_heartbeat(payload: Dict[str, Any]):
    """Handle soldier device heartbeat."""
    soldier_id = payload.get('soldier_id')
    timestamp = payload.get('timestamp', datetime.now().isoformat())
    logger.info(f"Heartbeat from soldier {soldier_id} at {timestamp}")

def start_mqtt_client():
    """Start the MQTT client in a separate thread."""
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        logger.info("MQTT client started successfully")
    except Exception as e:
        logger.error(f"Failed to start MQTT client: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with system status."""
    return {
        "message": "Military Hierarchy Backend API",
        "status": "running",
        "mqtt_connected": mqtt_client.is_connected() if mqtt_client else False
    }

@app.get("/units")
async def get_units():
    """Get all military units."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM units ORDER BY level, name")
    rows = c.fetchall()
    conn.close()
    
    columns = ["unit_id", "name", "parent_unit_id", "level"]
    return {"units": [dict(zip(columns, row)) for row in rows]}

@app.get("/units/{unit_id}/soldiers")
async def get_soldiers_by_unit(unit_id: str):
    """Get all soldiers in a specific unit."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, u.name as unit_name 
        FROM soldiers s 
        JOIN units u ON s.unit_id = u.unit_id 
        WHERE s.unit_id = ?
        ORDER BY s.rank, s.name
    """, (unit_id,))
    rows = c.fetchall()
    conn.close()
    
    columns = ["soldier_id", "name", "rank", "unit_id", "device_id", "unit_name"]
    return {"soldiers": [dict(zip(columns, row)) for row in rows]}

@app.get("/soldiers")
async def get_all_soldiers():
    """Get all soldiers."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, u.name as unit_name, u.level as unit_level
        FROM soldiers s 
        JOIN units u ON s.unit_id = u.unit_id 
        ORDER BY u.level, s.rank, s.name
    """)
    rows = c.fetchall()
    conn.close()
    
    columns = ["soldier_id", "name", "rank", "unit_id", "device_id", "unit_name", "unit_level"]
    return {"soldiers": [dict(zip(columns, row)) for row in rows]}

@app.get("/hierarchy")
async def get_hierarchy():
    """Get the complete military hierarchy with nested structure."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all units with their hierarchy information
    c.execute("""
        SELECT u.unit_id, u.name, u.parent_unit_id, u.level, u.created_at
        FROM units u
        ORDER BY u.level, u.name
    """)
    units = c.fetchall()
    
    # Get all soldiers grouped by unit
    c.execute("""
        SELECT s.soldier_id, s.name, s.rank, s.unit_id, s.device_id, s.status, s.created_at, s.last_seen
        FROM soldiers s
        ORDER BY s.unit_id, s.name
    """)
    soldiers = c.fetchall()
    
    conn.close()
    
    # Group soldiers by unit
    soldiers_by_unit = {}
    for soldier in soldiers:
        unit_id = soldier[3]
        if unit_id not in soldiers_by_unit:
            soldiers_by_unit[unit_id] = []
        soldiers_by_unit[unit_id].append({
            "soldier_id": soldier[0],
            "name": soldier[1],
            "rank": soldier[2],
            "unit_id": soldier[3],
            "device_id": soldier[4],
            "status": soldier[5],
            "created_at": soldier[6],
            "last_seen": soldier[7]
        })
    
    # Build hierarchy structure
    hierarchy = []
    for unit in units:
        unit_data = {
            "unit_id": unit[0],
            "name": unit[1],
            "parent_unit_id": unit[2],
            "level": unit[3],
            "created_at": unit[4],
            "soldiers": soldiers_by_unit.get(unit[0], [])
        }
        hierarchy.append(unit_data)
    
    return {"hierarchy": hierarchy}

@app.get("/units/{unit_id}/soldiers")
async def get_unit_soldiers(unit_id: str):
    """Get all soldiers in a specific unit."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT s.soldier_id, s.name, s.rank, s.unit_id, s.device_id, s.status, s.created_at, s.last_seen
        FROM soldiers s
        WHERE s.unit_id = ?
        ORDER BY s.name
    """, (unit_id,))
    
    soldiers = c.fetchall()
    conn.close()
    
    return {
        "soldiers": [
            {
                "soldier_id": s[0],
                "name": s[1],
                "rank": s[2],
                "unit_id": s[3],
                "device_id": s[4],
                "status": s[5],
                "created_at": s[6],
                "last_seen": s[7]
            }
            for s in soldiers
        ]
    }

@app.get("/soldiers/{soldier_id}/raw_inputs")
async def get_soldier_raw_inputs(soldier_id: str, limit: int = 500):
    """Get raw inputs from a specific soldier."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM soldier_raw_inputs 
        WHERE soldier_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (soldier_id, limit))
    rows = c.fetchall()
    conn.close()
    
    columns = ["input_id", "soldier_id", "timestamp", "raw_text", "raw_audio_ref"]
    return {
        "soldier_id": soldier_id, 
        "raw_inputs": [dict(zip(columns, row)) for row in rows]
    }

@app.get("/soldiers/{soldier_id}/reports")
async def get_soldier_reports(soldier_id: str, limit: int = 500):
    """Get structured reports from a specific soldier."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, s.name as soldier_name, u.name as unit_name
        FROM reports r
        JOIN soldiers s ON r.soldier_id = s.soldier_id
        JOIN units u ON r.unit_id = u.unit_id
        WHERE r.soldier_id = ? 
        ORDER BY r.timestamp DESC 
        LIMIT ?
    """, (soldier_id, limit))
    rows = c.fetchall()
    conn.close()
    
    columns = ["report_id", "soldier_id", "unit_id", "timestamp", "report_type", 
               "structured_json", "confidence", "soldier_name", "unit_name"]
    return {
        "soldier_id": soldier_id, 
        "reports": [dict(zip(columns, row)) for row in rows]
    }

@app.get("/reports")
async def get_all_reports(limit: int = 1000):
    """Get all structured reports."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, s.name as soldier_name, u.name as unit_name
        FROM reports r
        JOIN soldiers s ON r.soldier_id = s.soldier_id
        JOIN units u ON r.unit_id = u.unit_id
        ORDER BY r.timestamp DESC 
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    
    columns = ["report_id", "soldier_id", "unit_id", "timestamp", "report_type", 
               "structured_json", "confidence", "soldier_name", "unit_name"]
    return {"reports": [dict(zip(columns, row)) for row in rows]}

@app.post("/soldiers/{soldier_id}/reports")
async def create_report(soldier_id: str, report_data: Dict[str, Any]):
    """Create a new structured report."""
    try:
        # Get soldier's unit_id using the helper function
        soldier_result = execute_query(
            "SELECT unit_id FROM soldiers WHERE soldier_id = ?", 
            (soldier_id,), 
            fetch_one=True
        )
        if not soldier_result:
            raise HTTPException(status_code=404, detail="Soldier not found")
        
        unit_id = soldier_result["unit_id"]
        report_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        report_type = report_data.get("report_type", "UNKNOWN")
        structured_json = report_data.get("structured_json", {})
        text_content = report_data.get("text_content", "")
        
        # Generate a clean description for the report
        if "description" not in structured_json:
            structured_json["description"] = generate_report_description(report_type, structured_json)
        
        execute_query("""
            INSERT INTO reports (report_id, soldier_id, unit_id, timestamp, report_type, structured_json, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id, soldier_id, unit_id, timestamp,
            report_type,
            json.dumps(structured_json),
            report_data.get("confidence", 0.0)
        ))
        
        # SMART NOTIFICATIONS: Analyze for triggers after saving report
        try:
            analyze_report_triggers(
                report_id=report_id,
                soldier_id=soldier_id,
                unit_id=unit_id,
                report_type=report_type,
                structured_json=structured_json,
                text_content=text_content
            )
        except Exception as e:
            # Log but don't crash if trigger analysis fails
            logger.error(f"Error in trigger analysis (non-fatal): {e}", exc_info=True)
        
        return {"message": "Report created successfully", "report_id": report_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/soldiers/{soldier_id}/raw_inputs")
async def create_raw_input(soldier_id: str, input_data: Dict[str, Any]):
    """Create a new raw input from a soldier."""
    try:
        # Verify soldier exists using helper function
        soldier_result = execute_query(
            "SELECT soldier_id FROM soldiers WHERE soldier_id = ?", 
            (soldier_id,), 
            fetch_one=True
        )
        if not soldier_result:
            raise HTTPException(status_code=404, detail="Soldier not found")
        
        input_id = str(uuid.uuid4())
        timestamp = input_data.get("timestamp", datetime.now().isoformat())
        
        execute_query("""
            INSERT INTO soldier_raw_inputs (input_id, soldier_id, timestamp, raw_text, raw_audio_ref, input_type, confidence, location_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            input_id, soldier_id, timestamp,
            input_data.get("raw_text", ""),
            input_data.get("raw_audio_ref"),
            input_data.get("input_type", "voice"),
            input_data.get("confidence", 0.0),
            input_data.get("location_ref")
        ))
        
        return {"message": "Raw input created successfully", "input_id": input_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/soldiers")
async def create_soldier(soldier_data: Dict[str, Any]):
    """Create a new soldier."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verify unit exists
        unit_id = soldier_data.get("unit_id")
        c.execute("SELECT unit_id FROM units WHERE unit_id = ?", (unit_id,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="Unit not found")
        
        soldier_id = soldier_data.get("soldier_id", str(uuid.uuid4()))
        timestamp = datetime.now().isoformat()
        
        c.execute("""
            INSERT INTO soldiers (soldier_id, name, rank, unit_id, device_id, status, created_at, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            soldier_id,
            soldier_data.get("name"),
            soldier_data.get("rank"),
            unit_id,
            soldier_data.get("device_id"),
            soldier_data.get("status", "active"),
            timestamp,
            timestamp
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Soldier created successfully", "soldier_id": soldier_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/units")
async def create_unit(unit_data: Dict[str, Any]):
    """Create a new military unit."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verify parent unit exists if specified
        parent_unit_id = unit_data.get("parent_unit_id")
        if parent_unit_id:
            c.execute("SELECT unit_id FROM units WHERE unit_id = ?", (parent_unit_id,))
            if not c.fetchone():
                raise HTTPException(status_code=404, detail="Parent unit not found")
        
        unit_id = unit_data.get("unit_id", str(uuid.uuid4()))
        timestamp = datetime.now().isoformat()
        
        c.execute("""
            INSERT INTO units (unit_id, name, parent_unit_id, level, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            unit_id,
            unit_data.get("name"),
            parent_unit_id,
            unit_data.get("level"),
            timestamp
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Unit created successfully", "unit_id": unit_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/soldiers/{soldier_id}/status")
async def update_soldier_status(soldier_id: str, status_data: Dict[str, Any]):
    """Update a soldier's status and last_seen timestamp."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verify soldier exists
        c.execute("SELECT soldier_id FROM soldiers WHERE soldier_id = ?", (soldier_id,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="Soldier not found")
        
        timestamp = datetime.now().isoformat()
        
        c.execute("""
            UPDATE soldiers 
            SET status = ?, last_seen = ?
            WHERE soldier_id = ?
        """, (status_data.get("status"), timestamp, soldier_id))
        
        conn.commit()
        conn.close()
        
        return {"message": "Soldier status updated successfully", "soldier_id": soldier_id, "last_seen": timestamp}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hierarchy")
async def get_military_hierarchy():
    """Get the complete military hierarchy structure."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all units - select specific columns to avoid unpacking issues
    c.execute("SELECT unit_id, name, parent_unit_id, level FROM units ORDER BY level, name")
    units = c.fetchall()
    
    # Get all soldiers
    c.execute("""
        SELECT s.soldier_id, s.name, s.rank, s.unit_id, s.device_id
        FROM soldiers s 
        ORDER BY s.rank, s.name
    """)
    soldiers = c.fetchall()
    
    conn.close()
    
    # Build hierarchy structure
    units_dict = {}
    for unit in units:
        unit_id, name, parent_id, level = unit
        units_dict[unit_id] = {
            "unit_id": unit_id,
            "name": name,
            "parent_unit_id": parent_id,
            "level": level,
            "soldiers": [],
            "subunits": []
        }
    
    # Add soldiers to units
    soldier_columns = ["soldier_id", "name", "rank", "unit_id", "device_id"]
    for soldier in soldiers:
        soldier_data = dict(zip(soldier_columns, soldier))
        unit_id = soldier_data["unit_id"]
        if unit_id in units_dict:
            units_dict[unit_id]["soldiers"].append(soldier_data)
    
    # Build parent-child relationships
    hierarchy = []
    for unit_id, unit_data in units_dict.items():
        if unit_data["parent_unit_id"] is None:  # Top-level unit
            hierarchy.append(unit_data)
        else:
            parent_id = unit_data["parent_unit_id"]
            if parent_id in units_dict:
                units_dict[parent_id]["subunits"].append(unit_data)
    
    return {"hierarchy": hierarchy}

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    context: Dict[str, Any]

class FRAGOSuggestRequest(BaseModel):
    unit_id: str
    unit_name: str
    soldier_ids: List[str]
    reports: List[Dict[str, Any]]

class FRAGOGenerateRequest(BaseModel):
    unit_id: str
    unit_name: str
    frago_fields: Dict[str, Any]
    source_report_ids: List[str]

@app.post("/ai/chat")
async def ai_chat(chat_request: ChatMessage):
    """
    AI chat endpoint that analyzes reports using Google Gemini AI.
    """
    try:
        message = chat_request.message
        context = chat_request.context
        
        # Extract node info and reports from context
        node = context.get("node", {})
        reports = context.get("reports", [])
        
        # Log what we received for debugging
        logger.info(f"AI Chat request - Node: {node.get('name')}, Reports count: {len(reports)}")
        if reports and len(reports) > 0:
            logger.info(f"First report sample: {reports[0]}")
        
        # Build a response based on the message and reports
        if not reports:
            response = f"I don't have any reports available for {node.get('name', 'this node')}. Once reports are generated, I can help analyze them."
        else:
            report_count = len(reports)
            
            # Build a comprehensive prompt with clear instructions
            prompt = f"""You are an experienced military intelligence analyst AI with expertise in battlefield analysis, threat assessment, and tactical recommendations. Your role is to provide actionable intelligence insights to military commanders and staff.

CONTEXT:
- Unit: {node.get('name', 'Unknown')}
- Current Analysis: {report_count} battlefield reports
- User Role: Military commander/staff officer

USER QUESTION: {message}

ANALYSIS INSTRUCTIONS:
1. Synthesize patterns across multiple reports
2. Identify key threats, opportunities, and tactical considerations
3. Provide specific, actionable recommendations
4. Use proper military terminology (METT-TC framework when applicable)
5. Highlight time-sensitive information requiring immediate action
6. Assess confidence levels in your analysis

BATTLEFIELD REPORTS ({report_count} total):
"""
            
            # Add all reports with full details (limit to 20 for faster response)
            for i, report in enumerate(reports[:20], 1):
                try:
                    # Handle both original backend format and transformed frontend format
                    report_type = report.get('report_type') or report.get('type', 'UNKNOWN')
                    soldier_name = report.get('soldier_name') or report.get('from', 'Unknown')
                    timestamp = report.get('timestamp') or report.get('time', 'unknown')
                    
                    # Get structured data - could be in 'structured_json' or 'data' field
                    if 'structured_json' in report:
                        structured = json.loads(report.get("structured_json", "{}")) if isinstance(report.get("structured_json"), str) else report.get("structured_json", {})
                    else:
                        structured = report.get('data', {})
                    
                    prompt += f"\n{i}. [{report_type}] from {soldier_name} at {timestamp}\n"
                    prompt += f"   Data: {json.dumps(structured)}\n"
                except Exception as e:
                    logger.error(f"Error parsing report {i}: {e}")
                    logger.error(f"Report structure: {report}")
                    continue
            
            if report_count > 20:
                prompt += f"\n... and {report_count - 20} more reports (showing first 20)\n"
            
            prompt += "\n\nRESPONSE FORMAT:\n"
            prompt += "- Lead with executive summary (2-3 sentences)\n"
            prompt += "- Provide detailed analysis with supporting evidence from reports\n"
            prompt += "- Include tactical recommendations with priority levels\n"
            prompt += "- Highlight any immediate actions required\n"
            prompt += "- Use military terminology and doctrine appropriately\n"
            prompt += "- Be concise but comprehensive - focus on actionable intelligence"
            
            try:
                # Call Gemini API with safety settings and timeout
                import google.generativeai as genai_timeout
                genai_timeout.configure(api_key=GEMINI_API_KEY)
                model_with_timeout = genai_timeout.GenerativeModel(
                    'gemini-2.5-flash',
                    generation_config={'response_mime_type': 'text/plain', 'max_output_tokens': 2048}
                )
                
                gemini_response = model_with_timeout.generate_content(
                    prompt,
                    safety_settings={
                        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                    },
                    request_options={'timeout': 25}  # 25 second timeout (under Render's 30s limit)
                )
                response = gemini_response.text
                logger.info(f"Gemini API success: Generated response for {report_count} reports")
            except TimeoutError as e:
                logger.error(f"Gemini API timeout: {e}")
                response = f"AI analysis in progress... {report_count} reports being analyzed for {node.get('name')}. The analysis is taking longer than expected. Key data points: Check reports panel for details."
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Simple fallback without confusing prompts
                response = f"Error: Unable to connect to AI service. {report_count} reports available from {node.get('name')}. Please try again or check reports panel."
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "reports_analyzed": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/frago/suggest")
async def suggest_frago(request: FRAGOSuggestRequest):
    """
    Analyze reports and suggest FRAGO fields using AI.
    """
    try:
        unit_name = request.unit_name
        reports = request.reports
        
        logger.info(f"FRAGO Suggest - Unit: {unit_name}, Reports: {len(reports)}")
        
        if not reports:
            raise HTTPException(status_code=400, detail="No reports available for analysis")
        
        # Build comprehensive prompt for FRAGO generation
        prompt = f"""You are a military operations officer AI. Analyze these battlefield reports and suggest a FRAGMENTARY ORDER (FRAGO) for {unit_name} and its subordinate units.

A FRAGO modifies an existing operation order. Use the 5-paragraph format:
1. SITUATION - Enemy forces, friendly forces, attachments/detachments
2. MISSION - Who, what, when, where, and why (task and purpose)
3. EXECUTION - Concept of operations, tasks to subordinate units, coordinating instructions
4. SERVICE SUPPORT - Logistics, medical, transportation
5. COMMAND AND SIGNAL - Command posts, succession of command, communications

REPORTS FROM {unit_name} ({len(reports)} total):
"""
        
        # Add all reports with full context
        for i, report in enumerate(reports[:100], 1):  # Limit to 100 for token management
            try:
                report_type = report.get('report_type') or report.get('type', 'UNKNOWN')
                soldier_name = report.get('soldier_name') or report.get('from', 'Unknown')
                timestamp = report.get('timestamp') or report.get('time', 'unknown')
                
                if 'structured_json' in report:
                    structured = json.loads(report.get("structured_json", "{}")) if isinstance(report.get("structured_json"), str) else report.get("structured_json", {})
                else:
                    structured = report.get('data', {})
                
                prompt += f"\n{i}. [{report_type}] from {soldier_name} at {timestamp}\n"
                prompt += f"   {json.dumps(structured)}\n"
            except Exception as e:
                logger.error(f"Error parsing report {i}: {e}")
                continue
        
        if len(reports) > 100:
            prompt += f"\n... and {len(reports) - 100} more reports\n"
        
        prompt += """\n\nBased on these reports, suggest a FRAGO with the following JSON structure:
{
  "situation": "Brief enemy and friendly situation update",
  "mission": "Clear mission statement with task and purpose",
  "execution": "Concept of operations and key tasks",
  "service_support": "Logistics and support requirements",
  "command_signal": "Command post locations and communication plan"
}

Provide ONLY the JSON object, no additional text."""
        
        try:
            # Call Gemini API
            gemini_response = gemini_model.generate_content(
                prompt,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            response_text = gemini_response.text.strip()
            
            # Try to extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            suggested_fields = json.loads(response_text)
            
            logger.info(f"FRAGO suggestion generated successfully for {unit_name}")
            
            return {
                "suggested_fields": suggested_fields,
                "reports_analyzed": len(reports),
                "timestamp": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            # Return a fallback structure
            return {
                "suggested_fields": {
                    "situation": f"Analysis of {len(reports)} reports from {unit_name}",
                    "mission": "Continue current operations with increased vigilance",
                    "execution": "Maintain current posture and report any changes",
                    "service_support": "Continue current logistics operations",
                    "command_signal": "No changes to command structure"
                },
                "reports_analyzed": len(reports),
                "timestamp": datetime.now().isoformat(),
                "warning": "AI response parsing failed, using fallback template"
            }
        
    except Exception as e:
        logger.error(f"Error in FRAGO suggest: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating FRAGO suggestion: {str(e)}")

@app.post("/frago/generate")
async def generate_frago(request: FRAGOGenerateRequest):
    """
    Generate and save a formatted FRAGO document.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get next FRAGO number
        c.execute("SELECT next_number FROM frago_sequence WHERE id = 1")
        frago_number = c.fetchone()[0]
        
        # Increment sequence
        c.execute("UPDATE frago_sequence SET next_number = next_number + 1 WHERE id = 1")
        
        # Format FRAGO document
        fields = request.frago_fields
        unit_name = request.unit_name
        timestamp = datetime.now()
        
        formatted_doc = f"""FRAGMENTARY ORDER {frago_number:04d}
{unit_name}
{timestamp.strftime('%d%H%M%S %b %Y').upper()}

1. SITUATION
{fields.get('situation', 'No change to current situation.')}

2. MISSION
{fields.get('mission', 'Continue current mission.')}

3. EXECUTION
{fields.get('execution', 'No change to current execution.')}

4. SERVICE SUPPORT
{fields.get('service_support', 'Continue current support operations.')}

5. COMMAND AND SIGNAL
{fields.get('command_signal', 'No change to command and signal.')}

ACKNOWLEDGE.
//END OF FRAGO//
"""
        
        # Save to database
        frago_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO fragos (
                frago_id, frago_number, unit_id, created_at, 
                suggested_fields, final_fields, formatted_document, source_reports
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            frago_id,
            frago_number,
            request.unit_id,
            timestamp.isoformat(),
            json.dumps(fields),  # For this version, suggested = final
            json.dumps(fields),
            formatted_doc,
            json.dumps(request.source_report_ids)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"FRAGO {frago_number:04d} generated for {unit_name}")
        
        return {
            "frago_id": frago_id,
            "frago_number": frago_number,
            "formatted_document": formatted_doc,
            "timestamp": timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating FRAGO: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating FRAGO: {str(e)}")

# ===== CASEVAC ENDPOINTS =====

@app.post("/casevac/suggest")
async def suggest_casevac(request: Request):
    """
    Generate AI suggestions for CASEVAC 9-line fields based on reports.
    """
    try:
        body = await request.json()
        unit_id = body.get("unit_id")
        unit_name = body.get("unit_name")
        soldier_ids = body.get("soldier_ids", [])
        reports = body.get("reports", [])
        suggestion_id = body.get("suggestion_id")
        
        logger.info(f"CASEVAC suggest - Received {len(reports)} reports for {unit_name}")
        
        # Ensure reports is a list
        if not isinstance(reports, list):
            logger.error(f"CASEVAC suggest - reports is not a list: {type(reports)}")
            reports = []
        
        # Filter for CASUALTY reports
        casualty_reports = []
        for r in reports:
            if not isinstance(r, dict):
                logger.warning(f"CASEVAC suggest - Skipping non-dict report: {type(r)}")
                continue
            if r.get("report_type") == "CASUALTY":
                casualty_reports.append(r)
        
        logger.info(f"CASEVAC suggest - Found {len(casualty_reports)} CASUALTY reports")
        
        if not casualty_reports:
            return {"suggested_fields": {
                "location": "",
                "callsign_frequency": "",
                "precedence": "C",
                "special_equipment": "A",
                "patients": "",
                "security": "N",
                "marking_method": "D",
                "nationality": "A",
                "nbc_contamination": "N"
            }}
        
        # Build context from reports
        context = f"Unit: {unit_name}\n"
        context += f"Soldier IDs involved: {', '.join(soldier_ids)}\n\n"
        context += "Recent CASUALTY Reports:\n"
        
        for i, report in enumerate(casualty_reports[:5], 1):  # Limit to 5 most recent
            structured = report.get("structured_json", {})
            logger.info(f"Report {i}: structured type before parsing: {type(structured)}, value preview: {str(structured)[:100]}")
            
            # Handle potential double-encoding
            while isinstance(structured, str):
                try:
                    parsed = json.loads(structured)
                    logger.info(f"Report {i}: Parsed JSON, type is now: {type(parsed)}")
                    structured = parsed
                    if isinstance(structured, dict):
                        break
                except Exception as e:
                    logger.warning(f"Failed to parse structured_json for report {i}: {e}")
                    structured = {}
                    break
            
            if not isinstance(structured, dict):
                logger.warning(f"structured_json is not a dict for report {i}: {type(structured)}")
                structured = {}
            
            logger.info(f"Report {i}: Final structured type: {type(structured)}")
            context += f"\n{i}. Report from {report.get('soldier_id', 'Unknown')} at {report.get('timestamp', 'Unknown')}:\n"
            context += f"   Location: {structured.get('location', 'Not specified')}\n"
            context += f"   Casualty Type: {structured.get('casualty_type', 'Not specified')}\n"
            context += f"   Number of Casualties: {structured.get('casualty_count', 'Not specified')}\n"
            context += f"   Severity: {structured.get('severity', 'Not specified')}\n"
            context += f"   Injuries: {structured.get('injuries', 'Not specified')}\n"
            context += f"   Immediate Care: {structured.get('immediate_care_given', 'Not specified')}\n"
            
        prompt = f"""You are a military medical evacuation coordinator assistant. Based on the casualty reports provided, generate appropriate values for a 9-line MEDEVAC request.

{context}

IMPORTANT: Respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "location": "Grid coordinates or location description",
  "callsign_frequency": "Radio frequency and callsign (e.g., '30.55 MHz / DUSTOFF 23')",
  "precedence": "A, B, C, D, or E (A=URGENT life-threatening, B=URGENT-SURGICAL, C=PRIORITY stable, D=ROUTINE minor, E=CONVENIENCE)",
  "special_equipment": "A, B, C, or D (A=None, B=Hoist, C=Extraction, D=Ventilator)",
  "patients": "Format as '#L #A' where L=litter (stretcher) and A=ambulatory (walking). Example: '2L 1A' for 2 litter, 1 ambulatory",
  "security": "N, P, E, or X (N=No enemy, P=Possible enemy, E=Enemy in area, X=Armed escort required)",
  "marking_method": "A, B, C, D, or E (A=Panels, B=Pyrotechnic, C=Smoke, D=None, E=Other)",
  "nationality": "A, B, C, D, or E (A=US Military, B=US Civilian, C=Non-US Military, D=Non-US Civilian, E=EPW)",
  "nbc_contamination": "N if no contamination, or specify: N (Nuclear), B (Biological), C (Chemical)"
}}

Guidelines:
- Set precedence to A (URGENT) for life-threatening injuries, B for surgical needs, C for stable but needs care
- Estimate litter vs ambulatory based on injury severity
- Consider security situation from reports
- Default to US Military nationality unless specified otherwise
- Default NBC to "N" unless reports mention chemical/biological/radiological hazards"""

        try:
            response = gemini_model.generate_content(
                prompt,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            response_text = response.text.strip()
            
            logger.info(f"CASEVAC suggest - Gemini response received, length: {len(response_text)}")
            
            # Clean up markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            suggested_fields = json.loads(response_text)
            
            logger.info(f"CASEVAC suggest - Successfully parsed AI suggestions")
            
            return {"suggested_fields": suggested_fields}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {response_text}")
            # Return default values if AI parsing fails
            # Safely parse structured_json from first report
            first_casualty_data = {}
            if casualty_reports:
                structured = casualty_reports[0].get("structured_json", {})
                if isinstance(structured, str):
                    try:
                        first_casualty_data = json.loads(structured)
                    except:
                        first_casualty_data = {}
                elif isinstance(structured, dict):
                    first_casualty_data = structured
            
            return {"suggested_fields": {
                "location": first_casualty_data.get("location", ""),
                "callsign_frequency": "FREQ TBD",
                "precedence": "C",
                "special_equipment": "A",
                "patients": "TBD",
                "security": "N",
                "marking_method": "D",
                "nationality": "A",
                "nbc_contamination": "N"
            }}
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            logger.error(f"Gemini API error details:", exc_info=True)
            raise
            
    except Exception as e:
        logger.error(f"Error in suggest_casevac: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/casevac/generate")
async def generate_casevac(request: Request):
    """
    Generate a formatted 9-line CASEVAC document and save to database.
    """
    conn = None
    try:
        body = await request.json()
        unit_id = body.get("unit_id")
        unit_name = body.get("unit_name")
        casevac_fields = body.get("casevac_fields", {})
        source_report_ids = body.get("source_report_ids", [])
        
        conn = get_db_connection()
        conn.execute("PRAGMA busy_timeout = 5000")  # Wait up to 5 seconds for locks
        c = conn.cursor()
        
        # Get next CASEVAC number
        c.execute("SELECT next_number FROM report_sequences WHERE report_type = 'CASEVAC'")
        row = c.fetchone()
        
        if row is None:
            # Initialize CASEVAC sequence if not exists
            c.execute("INSERT INTO report_sequences (report_type, next_number) VALUES ('CASEVAC', 1)")
            conn.commit()
            casevac_number = 1
        else:
            casevac_number = row[0]
        
        # Update sequence
        c.execute(
            "UPDATE report_sequences SET next_number = ? WHERE report_type = 'CASEVAC'",
            (casevac_number + 1,)
        )
        conn.commit()  # Commit sequence update immediately
        
        timestamp = datetime.now()
        dtg = timestamp.strftime("%d%H%M%SZ %b %Y").upper()
        
        # Format the 9-line CASEVAC document
        formatted_doc = f"""CASEVAC REQUEST {str(casevac_number).zfill(4)}
DTG: {dtg}
FROM: {unit_name}

9-LINE MEDEVAC REQUEST:

LINE 1 - LOCATION OF PICKUP SITE:
{casevac_fields.get('location', 'NOT SPECIFIED')}

LINE 2 - RADIO FREQUENCY, CALL SIGN, AND SUFFIX:
{casevac_fields.get('callsign_frequency', 'NOT SPECIFIED')}

LINE 3 - NUMBER OF PATIENTS BY PRECEDENCE:
{casevac_fields.get('precedence', 'C')} - {
    'URGENT (Life, limb, or eyesight threatening)' if casevac_fields.get('precedence') == 'A' else
    'URGENT-SURGICAL (Surgical intervention required within 2 hours)' if casevac_fields.get('precedence') == 'B' else
    'PRIORITY (Stable but requires medical attention)' if casevac_fields.get('precedence') == 'C' else
    'ROUTINE (Minor injuries, stable)' if casevac_fields.get('precedence') == 'D' else
    'CONVENIENCE (No medical condition)' if casevac_fields.get('precedence') == 'E' else
    'NOT SPECIFIED'
}

LINE 4 - SPECIAL EQUIPMENT REQUIRED:
{casevac_fields.get('special_equipment', 'A')} - {
    'None' if casevac_fields.get('special_equipment') == 'A' else
    'Hoist' if casevac_fields.get('special_equipment') == 'B' else
    'Extraction Equipment' if casevac_fields.get('special_equipment') == 'C' else
    'Ventilator' if casevac_fields.get('special_equipment') == 'D' else
    'NOT SPECIFIED'
}

LINE 5 - NUMBER OF PATIENTS BY TYPE:
{casevac_fields.get('patients', 'NOT SPECIFIED')}
(L = Litter/Stretcher, A = Ambulatory/Walking Wounded)

LINE 6 - SECURITY AT PICKUP SITE:
{casevac_fields.get('security', 'N')} - {
    'No enemy troops in area' if casevac_fields.get('security') == 'N' else
    'Possible enemy troops in area (approach with caution)' if casevac_fields.get('security') == 'P' else
    'Enemy troops in area (armed escort required)' if casevac_fields.get('security') == 'E' else
    'Enemy troops in area (armed escort required)' if casevac_fields.get('security') == 'X' else
    'NOT SPECIFIED'
}

LINE 7 - METHOD OF MARKING PICKUP SITE:
{casevac_fields.get('marking_method', 'D')} - {
    'Panels' if casevac_fields.get('marking_method') == 'A' else
    'Pyrotechnic signal' if casevac_fields.get('marking_method') == 'B' else
    'Smoke signal' if casevac_fields.get('marking_method') == 'C' else
    'None' if casevac_fields.get('marking_method') == 'D' else
    'Other (specify in remarks)' if casevac_fields.get('marking_method') == 'E' else
    'NOT SPECIFIED'
}

LINE 8 - PATIENT NATIONALITY AND STATUS:
{casevac_fields.get('nationality', 'A')} - {
    'US Military' if casevac_fields.get('nationality') == 'A' else
    'US Civilian' if casevac_fields.get('nationality') == 'B' else
    'Non-US Military' if casevac_fields.get('nationality') == 'C' else
    'Non-US Civilian' if casevac_fields.get('nationality') == 'D' else
    'Enemy Prisoner of War (EPW)' if casevac_fields.get('nationality') == 'E' else
    'NOT SPECIFIED'
}

LINE 9 - NBC CONTAMINATION:
{casevac_fields.get('nbc_contamination', 'N')}
(N=None, C=Chemical, B=Biological, R=Radiological)

---
SOURCE REPORTS: {', '.join(source_report_ids)}
GENERATED BY: AI-ASSISTED CASEVAC BUILDER
---
"""
        
        # Save to reports table with formatted document in structured_json
        report_id = f"CASEVAC_{casevac_number:04d}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Store both fields and formatted document in structured_json
        casevac_data = {
            "fields": casevac_fields,
            "formatted_document": formatted_doc,
            "casevac_number": casevac_number,
            "source_reports": source_report_ids
        }
        
        c.execute("""
            INSERT INTO reports 
            (report_id, soldier_id, unit_id, timestamp, report_type, structured_json, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            unit_id,  # Using unit_id as soldier_id for generated reports
            unit_id,
            timestamp.isoformat(),
            "CASEVAC",
            json.dumps(casevac_data),
            1.0,  # Full confidence for generated reports
            "generated"
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Generated CASEVAC {casevac_number} for unit {unit_name}")
        
        return {
            "casevac_id": report_id,
            "casevac_number": casevac_number,
            "formatted_document": formatted_doc,
            "timestamp": timestamp.isoformat()
        }
        
    except Exception as e:
        if conn:
            conn.close()
        logger.error(f"Error generating CASEVAC: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating CASEVAC: {str(e)}")

# ===== SUGGESTIONS API ENDPOINTS =====

@app.post("/eoincrep/suggest")
async def suggest_eoincrep(request: Request):
    """
    Generate AI suggestions for EOINCREP fields based on contact/intelligence reports.
    """
    try:
        body = await request.json()
        unit_id = body.get("unit_id")
        unit_name = body.get("unit_name")
        soldier_ids = body.get("soldier_ids", [])
        reports = body.get("reports", [])
        suggestion_id = body.get("suggestion_id")
        
        logger.info(f"EOINCREP suggest - Received {len(reports)} reports for {unit_name}")
        
        # Ensure reports is a list
        if not isinstance(reports, list):
            logger.error(f"EOINCREP suggest - reports is not a list: {type(reports)}")
            reports = []
        
        # Filter for CONTACT, INTELLIGENCE, and SITREP reports
        relevant_reports = []
        for r in reports:
            if not isinstance(r, dict):
                logger.warning(f"EOINCREP suggest - Skipping non-dict report: {type(r)}")
                continue
            if r.get("report_type") in ["CONTACT", "INTELLIGENCE", "SITREP"]:
                relevant_reports.append(r)
        
        logger.info(f"EOINCREP suggest - Found {len(relevant_reports)} relevant reports")
        
        if not relevant_reports:
            return {"suggested_fields": {
                "location": "",
                "observer_id": "",
                "enemy_type": "INFANTRY",
                "enemy_count": "",
                "vehicle_count": "0",
                "direction": "N",
                "equipment": "",
                "activity": "",
                "threat_level": "MEDIUM",
                "recommended_action": ""
            }}
        
        # Build context from reports
        context = f"Unit: {unit_name}\n"
        context += f"Soldier IDs involved: {', '.join(soldier_ids)}\n\n"
        context += "Recent Contact/Intelligence Reports:\n"
        
        for i, report in enumerate(relevant_reports[:5], 1):
            structured = report.get("structured_json", {})
            
            # Handle potential double-encoding
            while isinstance(structured, str):
                try:
                    parsed = json.loads(structured)
                    structured = parsed
                    if isinstance(structured, dict):
                        break
                except Exception as e:
                    logger.warning(f"Failed to parse structured_json for report {i}: {e}")
                    structured = {}
                    break
            
            if not isinstance(structured, dict):
                logger.warning(f"structured_json is not a dict for report {i}: {type(structured)}")
                structured = {}
            
            context += f"\n{i}. Report from {report.get('soldier_id', 'Unknown')} at {report.get('timestamp', 'Unknown')}:\n"
            context += f"   Type: {report.get('report_type', 'Unknown')}\n"
            context += f"   Location: {structured.get('location', 'Not specified')}\n"
            context += f"   Enemy Count: {structured.get('enemy_count', 'Not specified')}\n"
            context += f"   Vehicles: {structured.get('vehicle_count', 'Not specified')}\n"
            context += f"   Description: {structured.get('description', 'Not specified')}\n"
            
        prompt = f"""You are a military intelligence analyst assistant. Based on the contact and intelligence reports provided, generate appropriate values for an Enemy Observation/Incident Report (EOINCREP) using the SALUTE format.

{context}

IMPORTANT: Respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "location": "Grid coordinates or location description from reports",
  "observer_id": "Observer callsign or name if mentioned",
  "enemy_type": "INFANTRY, ARMOR, ARTILLERY, MIXED, or UNKNOWN (based on reports)",
  "enemy_count": "Number of enemy personnel observed (number only)",
  "vehicle_count": "Number of vehicles observed (number only, 0 if none)",
  "direction": "N, NE, E, SE, S, SW, W, NW, or STATIONARY (direction of enemy movement)",
  "equipment": "Detailed description of weapons, vehicles, and equipment observed",
  "activity": "What the enemy is doing: patrolling, digging in, moving, engaging, etc.",
  "threat_level": "LOW, MEDIUM, HIGH, or CRITICAL (assess based on enemy size and activity)",
  "recommended_action": "Suggest tactical response: monitor, engage, call for support, etc."
}}

Guidelines:
- Extract enemy_type from reports (infantry, armor, artillery mentions)
- Set threat_level to CRITICAL for large forces (>20 personnel or >3 vehicles)
- Set threat_level to HIGH for significant forces (10-20 personnel or 2-3 vehicles)
- Set threat_level to MEDIUM for small patrols (5-10 personnel or 1 vehicle)
- Set threat_level to LOW for minimal presence (<5 personnel)
- Recommend "Monitor and report" for LOW, "Prepare to engage" for MEDIUM, "Engage with support" for HIGH, "Immediate support required" for CRITICAL"""

        try:
            response = gemini_model.generate_content(
                prompt,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            response_text = response.text.strip()
            
            logger.info(f"EOINCREP suggest - Gemini response received, length: {len(response_text)}")
            
            # Clean up markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            suggested_fields = json.loads(response_text)
            
            logger.info(f"EOINCREP suggest - Successfully parsed AI suggestions")
            
            return {"suggested_fields": suggested_fields}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {response_text}")
            # Return default values if AI parsing fails
            # Safely parse structured_json from first report
            first_report_data = {}
            if relevant_reports:
                structured = relevant_reports[0].get("structured_json", {})
                if isinstance(structured, str):
                    try:
                        first_report_data = json.loads(structured)
                    except:
                        first_report_data = {}
                elif isinstance(structured, dict):
                    first_report_data = structured
            
            return {"suggested_fields": {
                "location": first_report_data.get("location", ""),
                "observer_id": "",
                "enemy_type": "UNKNOWN",
                "enemy_count": str(first_report_data.get("enemy_count", "")),
                "vehicle_count": "0",
                "direction": "N",
                "equipment": "TBD",
                "activity": "TBD",
                "threat_level": "MEDIUM",
                "recommended_action": "Monitor and report"
            }}
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            logger.error(f"Gemini API error details:", exc_info=True)
            raise
            
    except Exception as e:
        logger.error(f"Error in suggest_eoincrep: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/eoincrep/generate")
async def generate_eoincrep(request: Request):
    """
    Generate a formatted EOINCREP (Enemy Observation/Incident Report) document and save to database.
    """
    conn = None
    try:
        body = await request.json()
        unit_id = body.get("unit_id")
        unit_name = body.get("unit_name")
        eoincrep_fields = body.get("eoincrep_fields", {})
        source_report_ids = body.get("source_report_ids", [])
        
        conn = get_db_connection()
        conn.execute("PRAGMA busy_timeout = 5000")
        c = conn.cursor()
        
        # Get next EOINCREP number
        c.execute("SELECT next_number FROM report_sequences WHERE report_type = 'EOINCREP'")
        row = c.fetchone()
        
        if row is None:
            c.execute("INSERT INTO report_sequences (report_type, next_number) VALUES ('EOINCREP', 1)")
            conn.commit()
            eoincrep_number = 1
        else:
            eoincrep_number = row[0]
        
        # Update sequence
        c.execute(
            "UPDATE report_sequences SET next_number = ? WHERE report_type = 'EOINCREP'",
            (eoincrep_number + 1,)
        )
        conn.commit()
        
        timestamp = datetime.now()
        dtg = timestamp.strftime("%d%H%M%SZ %b %Y").upper()
        
        # Format the EOINCREP document using SALUTE format
        formatted_doc = f"""ENEMY OBSERVATION/INCIDENT REPORT {str(eoincrep_number).zfill(4)}
DTG: {dtg}
FROM: {unit_name}
OBSERVER: {eoincrep_fields.get('observer_id', 'NOT SPECIFIED')}

LOCATION: {eoincrep_fields.get('location', 'NOT SPECIFIED')}

=== SALUTE REPORT ===

S - SIZE:
Enemy Personnel: {eoincrep_fields.get('enemy_count', 'Unknown')}
Enemy Vehicles: {eoincrep_fields.get('vehicle_count', '0')}
Unit Type: {eoincrep_fields.get('enemy_type', 'UNKNOWN')}

A - ACTIVITY:
{eoincrep_fields.get('activity', 'NOT SPECIFIED')}

L - LOCATION:
{eoincrep_fields.get('location', 'NOT SPECIFIED')}

U - UNIT:
Type: {eoincrep_fields.get('enemy_type', 'UNKNOWN')}
Estimated Size: {
    'Fire Team (4-6)' if int(eoincrep_fields.get('enemy_count', '0') or '0') <= 6 else
    'Squad (8-12)' if int(eoincrep_fields.get('enemy_count', '0') or '0') <= 12 else
    'Platoon (20-40)' if int(eoincrep_fields.get('enemy_count', '0') or '0') <= 40 else
    'Company (80-150)' if int(eoincrep_fields.get('enemy_count', '0') or '0') <= 150 else
    'Battalion (300+)'
}

T - TIME:
{dtg}

E - EQUIPMENT:
{eoincrep_fields.get('equipment', 'NOT SPECIFIED')}

=== ADDITIONAL INFORMATION ===

DIRECTION OF MOVEMENT: {eoincrep_fields.get('direction', 'NOT SPECIFIED')}

THREAT ASSESSMENT: {eoincrep_fields.get('threat_level', 'MEDIUM')}

RECOMMENDED ACTION:
{eoincrep_fields.get('recommended_action', 'Monitor and report any changes')}

---
SOURCE REPORTS: {', '.join(source_report_ids)}
GENERATED BY: AI-ASSISTED EOINCREP BUILDER
---
"""
        
        # Save to reports table
        report_id = f"EOINCREP_{eoincrep_number:04d}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        eoincrep_data = {
            "fields": eoincrep_fields,
            "formatted_document": formatted_doc,
            "eoincrep_number": eoincrep_number,
            "source_reports": source_report_ids
        }
        
        c.execute("""
            INSERT INTO reports 
            (report_id, soldier_id, unit_id, timestamp, report_type, structured_json, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            unit_id,
            unit_id,
            timestamp.isoformat(),
            "EOINCREP",
            json.dumps(eoincrep_data),
            1.0,
            "generated"
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Generated EOINCREP {eoincrep_number} for unit {unit_name}")
        
        return {
            "eoincrep_id": report_id,
            "eoincrep_number": eoincrep_number,
            "formatted_document": formatted_doc,
            "timestamp": timestamp.isoformat()
        }
        
    except Exception as e:
        if conn:
            conn.close()
        logger.error(f"Error generating EOINCREP: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating EOINCREP: {str(e)}")

# ===== SUGGESTIONS API ENDPOINTS =====

@app.post("/api/suggestions/reanalyze")
async def reanalyze_all_reports():
    """
    Reanalyze all recent reports (last 50) to generate suggestions.
    This is useful for retroactively creating suggestions from existing reports.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get recent reports (last 50)
        c.execute("""
            SELECT report_id, soldier_id, unit_id, report_type, structured_json, timestamp
            FROM reports
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        
        rows = c.fetchall()
        total_reports = len(rows)
        suggestions_created = 0
        
        logger.info(f"Reanalyzing {total_reports} recent reports...")
        
        for row in rows:
            report_id, soldier_id, unit_id, report_type, structured_json_str, timestamp = row
            
            try:
                # Parse the structured JSON
                structured_json = json.loads(structured_json_str) if structured_json_str else {}
                
                # Get text content if available
                text_content = structured_json.get("description", "")
                
                # Analyze for triggers
                triggers = analyze_report_triggers(
                    report_id=report_id,
                    soldier_id=soldier_id,
                    unit_id=unit_id,
                    report_type=report_type,
                    structured_json=structured_json,
                    text_content=text_content
                )
                
                if triggers:
                    suggestions_created += len(triggers)
                    
            except Exception as e:
                logger.warning(f"Error analyzing report {report_id}: {e}")
                continue
        
        conn.close()
        
        logger.info(f"Reanalysis complete: created {suggestions_created} suggestions from {total_reports} reports")
        
        return {
            "message": "Reanalysis complete",
            "reports_analyzed": total_reports,
            "suggestions_created": suggestions_created
        }
        
    except Exception as e:
        logger.error(f"Error reanalyzing reports: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suggestions")
async def get_suggestions(status: str = "pending", unit_id: Optional[str] = None):
    """
    Get all suggestions, optionally filtered by status and unit_id.
    Status options: 'pending', 'draft_created', 'approved', 'dismissed'
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        query = "SELECT * FROM suggestions WHERE status = ?"
        params = [status]
        
        if unit_id:
            query += " AND unit_id = ?"
            params.append(unit_id)
        
        query += " ORDER BY created_at DESC LIMIT 50"
        
        c.execute(query, params)
        rows = c.fetchall()
        
        # Get column names
        columns = [description[0] for description in c.description]
        
        # Convert to list of dicts
        suggestions = []
        for row in rows:
            suggestion = dict(zip(columns, row))
            # Parse JSON fields
            suggestion['source_reports'] = json.loads(suggestion['source_reports'])
            if suggestion.get('suggested_fields'):
                suggestion['suggested_fields'] = json.loads(suggestion['suggested_fields'])
            suggestions.append(suggestion)
        
        conn.close()
        
        return {"suggestions": suggestions, "count": len(suggestions)}
        
    except Exception as e:
        logger.error(f"Error fetching suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/suggestions/{suggestion_id}")
async def dismiss_suggestion(suggestion_id: str, dismissed_by: str = "user"):
    """
    Dismiss a suggestion (mark as dismissed).
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("""
            UPDATE suggestions 
            SET status = 'dismissed', 
                dismissed_at = ?,
                dismissed_by = ?
            WHERE suggestion_id = ?
        """, (datetime.now().isoformat(), dismissed_by, suggestion_id))
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Suggestion dismissed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dismissing suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggestions/{suggestion_id}/create-draft")
async def create_suggestion_draft(suggestion_id: str):
    """
    Create a draft report from a suggestion (Level 3 - Auto-Drafts).
    This endpoint will be used when user clicks "Create Draft" on a suggestion.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get the suggestion
        c.execute("SELECT * FROM suggestions WHERE suggestion_id = ?", (suggestion_id,))
        row = c.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        columns = [description[0] for description in c.description]
        suggestion = dict(zip(columns, row))
        
        # Update suggestion status
        c.execute("""
            UPDATE suggestions 
            SET status = 'draft_created'
            WHERE suggestion_id = ?
        """, (suggestion_id,))
        
        conn.commit()
        conn.close()
        
        # Return the suggestion data for the builder to use
        return {
            "message": "Ready to create draft",
            "suggestion": {
                "suggestion_id": suggestion_id,
                "type": suggestion["suggestion_type"],
                "source_reports": json.loads(suggestion["source_reports"]),
                "urgency": suggestion["urgency"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating draft from suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== END SUGGESTIONS API ENDPOINTS =====

@app.on_event("startup")
async def startup_event():
    """Initialize MQTT client on startup."""
    mqtt_thread = threading.Thread(target=start_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up MQTT client on shutdown."""
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
