# Military Hierarchy API Documentation

## Base URL

- **Local**: https://military-hierarchy-backend.onrender.com/
- **Network**: http://10.3.35.27:8000
- **Interactive Docs**: http://10.3.35.27:8000/docs (Swagger UI)

## Authentication

Currently no authentication is required. All endpoints are publicly accessible.

## Data Models

### Soldier

```json
{
  "soldier_id": "ALPHA_01",
  "name": "Lt. John Smith",
  "rank": "Lieutenant",
  "unit_id": "PLT_1",
  "device_id": "RADIO_001",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "last_seen": "2024-01-15T14:45:00Z"
}
```

### Unit

```json
{
  "unit_id": "PLT_1",
  "name": "1st Platoon",
  "parent_unit_id": "CO_A",
  "level": "Platoon",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Raw Input

```json
{
  "input_id": "uuid-here",
  "soldier_id": "ALPHA_01",
  "timestamp": "2024-01-15T14:45:00Z",
  "raw_text": "Enemy spotted at grid 123456",
  "raw_audio_ref": "audio_file_001.wav",
  "input_type": "voice",
  "confidence": 0.95,
  "location_ref": "GPS_123456"
}
```

### Report

```json
{
  "report_id": "uuid-here",
  "soldier_id": "ALPHA_01",
  "unit_id": "PLT_1",
  "timestamp": "2024-01-15T14:45:00Z",
  "report_type": "SITREP",
  "structured_json": {
    "enemy_contact": true,
    "location": "grid 123456",
    "threat_level": "medium"
  },
  "confidence": 0.85
}
```

## API Endpoints

### System Status

**GET** `/`
Get system status and health information.

**Response:**

```json
{
  "message": "Military Hierarchy Backend API",
  "status": "running",
  "mqtt_connected": true
}
```

### Units

#### Get All Units

**GET** `/units`
Retrieve all military units in the hierarchy.

**Response:**

```json
{
  "units": [
    {
      "unit_id": "BAT_1",
      "name": "1st Infantry Battalion",
      "parent_unit_id": null,
      "level": "Battalion"
    }
  ]
}
```

#### Get Soldiers by Unit

**GET** `/units/{unit_id}/soldiers`
Get all soldiers in a specific unit.

**Parameters:**

- `unit_id` (path): The unit identifier

**Response:**

```json
{
  "soldiers": [
    {
      "soldier_id": "ALPHA_01",
      "name": "Lt. John Smith",
      "rank": "Lieutenant",
      "unit_id": "PLT_1",
      "device_id": "RADIO_001",
      "unit_name": "1st Platoon"
    }
  ]
}
```

#### Create Unit

**POST** `/units`
Create a new military unit.

**Request Body:**

```json
{
  "unit_id": "PLT_2",
  "name": "2nd Platoon",
  "parent_unit_id": "CO_A",
  "level": "Platoon"
}
```

**Response:**

```json
{
  "message": "Unit created successfully",
  "unit_id": "PLT_2"
}
```

### Soldiers

#### Get All Soldiers

**GET** `/soldiers`
Retrieve all soldiers with their unit information.

**Response:**

```json
{
  "soldiers": [
    {
      "soldier_id": "ALPHA_01",
      "name": "Lt. John Smith",
      "rank": "Lieutenant",
      "unit_id": "PLT_1",
      "device_id": "RADIO_001",
      "unit_name": "1st Platoon",
      "unit_level": "Platoon"
    }
  ]
}
```

#### Create Soldier

**POST** `/soldiers`
Create a new soldier.

**Request Body:**

```json
{
  "soldier_id": "ALPHA_02",
  "name": "Sgt. Jane Doe",
  "rank": "Sergeant",
  "unit_id": "PLT_1",
  "device_id": "RADIO_002",
  "status": "active"
}
```

**Response:**

```json
{
  "message": "Soldier created successfully",
  "soldier_id": "ALPHA_02"
}
```

#### Update Soldier Status

**PUT** `/soldiers/{soldier_id}/status`
Update a soldier's status and last seen timestamp.

**Parameters:**

- `soldier_id` (path): The soldier identifier

**Request Body:**

```json
{
  "status": "injured"
}
```

**Response:**

```json
{
  "message": "Soldier status updated successfully",
  "soldier_id": "ALPHA_01",
  "last_seen": "2024-01-15T14:45:00Z"
}
```

### Raw Inputs

#### Get Soldier Raw Inputs

**GET** `/soldiers/{soldier_id}/raw_inputs?limit=50`
Get raw inputs from a specific soldier.

**Parameters:**

- `soldier_id` (path): The soldier identifier
- `limit` (query, optional): Maximum number of inputs to return (default: 50)

**Response:**

```json
{
  "soldier_id": "ALPHA_01",
  "raw_inputs": [
    {
      "input_id": "uuid-here",
      "soldier_id": "ALPHA_01",
      "timestamp": "2024-01-15T14:45:00Z",
      "raw_text": "Enemy spotted at grid 123456",
      "raw_audio_ref": "audio_file_001.wav"
    }
  ]
}
```

#### Create Raw Input

**POST** `/soldiers/{soldier_id}/raw_inputs`
Create a new raw input from a soldier.

**Parameters:**

- `soldier_id` (path): The soldier identifier

**Request Body:**

```json
{
  "raw_text": "Enemy spotted at grid 123456",
  "raw_audio_ref": "audio_file_001.wav",
  "input_type": "voice",
  "confidence": 0.95,
  "location_ref": "GPS_123456",
  "timestamp": "2024-01-15T14:45:00Z"
}
```

**Response:**

```json
{
  "message": "Raw input created successfully",
  "input_id": "uuid-here"
}
```

### Reports

#### Get All Reports

**GET** `/reports?limit=100`
Get all structured reports.

**Parameters:**

- `limit` (query, optional): Maximum number of reports to return (default: 100)

**Response:**

```json
{
  "reports": [
    {
      "report_id": "uuid-here",
      "soldier_id": "ALPHA_01",
      "unit_id": "PLT_1",
      "timestamp": "2024-01-15T14:45:00Z",
      "report_type": "SITREP",
      "structured_json": {
        "enemy_contact": true,
        "location": "grid 123456",
        "threat_level": "medium"
      },
      "confidence": 0.85,
      "soldier_name": "Lt. John Smith",
      "unit_name": "1st Platoon"
    }
  ]
}
```

#### Get Soldier Reports

**GET** `/soldiers/{soldier_id}/reports?limit=50`
Get structured reports from a specific soldier.

**Parameters:**

- `soldier_id` (path): The soldier identifier
- `limit` (query, optional): Maximum number of reports to return (default: 50)

**Response:**

```json
{
  "soldier_id": "ALPHA_01",
  "reports": [
    {
      "report_id": "uuid-here",
      "soldier_id": "ALPHA_01",
      "unit_id": "PLT_1",
      "timestamp": "2024-01-15T14:45:00Z",
      "report_type": "SITREP",
      "structured_json": {
        "enemy_contact": true,
        "location": "grid 123456",
        "threat_level": "medium"
      },
      "confidence": 0.85,
      "soldier_name": "Lt. John Smith",
      "unit_name": "1st Platoon"
    }
  ]
}
```

#### Create Report

**POST** `/soldiers/{soldier_id}/reports`
Create a new structured report.

**Parameters:**

- `soldier_id` (path): The soldier identifier

**Request Body:**

```json
{
  "report_type": "SITREP",
  "structured_json": {
    "enemy_contact": true,
    "location": "grid 123456",
    "threat_level": "medium",
    "casualties": 0,
    "ammunition_status": "adequate"
  },
  "confidence": 0.85
}
```

**Response:**

```json
{
  "message": "Report created successfully",
  "report_id": "uuid-here"
}
```

### Hierarchy

#### Get Military Hierarchy

**GET** `/hierarchy`
Get the complete military hierarchy structure with nested units and soldiers.

**Response:**

```json
{
  "hierarchy": [
    {
      "unit_id": "BAT_1",
      "name": "1st Infantry Battalion",
      "parent_unit_id": null,
      "level": "Battalion",
      "soldiers": [],
      "subunits": [
        {
          "unit_id": "CO_A",
          "name": "Alpha Company",
          "parent_unit_id": "BAT_1",
          "level": "Company",
          "soldiers": [],
          "subunits": [
            {
              "unit_id": "PLT_1",
              "name": "1st Platoon",
              "parent_unit_id": "CO_A",
              "level": "Platoon",
              "soldiers": [
                {
                  "soldier_id": "ALPHA_01",
                  "name": "Lt. John Smith",
                  "rank": "Lieutenant",
                  "unit_id": "PLT_1",
                  "device_id": "RADIO_001",
                  "unit_name": "1st Platoon",
                  "unit_level": "Platoon"
                }
              ],
              "subunits": []
            }
          ]
        }
      ]
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found

```json
{
  "detail": "Soldier not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Database connection failed"
}
```

## Usage Examples

### Python Example

```python
import requests
import json

API_BASE = "http://10.3.35.27:8000"

# Create a new soldier
soldier_data = {
    "soldier_id": "ALPHA_03",
    "name": "Cpl. Mike Johnson",
    "rank": "Corporal",
    "unit_id": "PLT_1",
    "device_id": "RADIO_003",
    "status": "active"
}

response = requests.post(f"{API_BASE}/soldiers", json=soldier_data)
print(response.json())

# Send raw input from soldier
input_data = {
    "raw_text": "Mission complete, returning to base",
    "input_type": "voice",
    "confidence": 0.92,
    "location_ref": "GPS_789012"
}

response = requests.post(f"{API_BASE}/soldiers/ALPHA_03/raw_inputs", json=input_data)
print(response.json())

# Create a structured report
report_data = {
    "report_type": "MISSION_COMPLETE",
    "structured_json": {
        "mission_status": "completed",
        "casualties": 0,
        "equipment_status": "all_operational",
        "next_objective": "return_to_base"
    },
    "confidence": 0.95
}

response = requests.post(f"{API_BASE}/soldiers/ALPHA_03/reports", json=report_data)
print(response.json())
```

### JavaScript Example

```javascript
const API_BASE = "http://10.3.35.27:8000";

// Create a new soldier
const soldierData = {
  soldier_id: "ALPHA_04",
  name: "Pvt. Sarah Wilson",
  rank: "Private",
  unit_id: "PLT_1",
  device_id: "RADIO_004",
  status: "active",
};

fetch(`${API_BASE}/soldiers`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(soldierData),
})
  .then((response) => response.json())
  .then((data) => console.log(data));

// Send raw input
const inputData = {
  raw_text: "Enemy movement detected",
  input_type: "voice",
  confidence: 0.88,
  location_ref: "GPS_345678",
};

fetch(`${API_BASE}/soldiers/ALPHA_04/raw_inputs`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(inputData),
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

### cURL Examples

```bash
# Create a soldier
curl -X POST "http://10.3.35.27:8000/soldiers" \
  -H "Content-Type: application/json" \
  -d '{
    "soldier_id": "ALPHA_05",
    "name": "Sgt. Tom Brown",
    "rank": "Sergeant",
    "unit_id": "PLT_1",
    "device_id": "RADIO_005",
    "status": "active"
  }'

# Send raw input
curl -X POST "http://10.3.35.27:8000/soldiers/ALPHA_05/raw_inputs" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Requesting medical evacuation",
    "input_type": "voice",
    "confidence": 0.95,
    "location_ref": "GPS_901234"
  }'

# Create a report
curl -X POST "http://10.3.35.27:8000/soldiers/ALPHA_05/reports" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "MEDEVAC_REQUEST",
    "structured_json": {
      "casualty_count": 1,
      "injury_type": "gunshot_wound",
      "urgency": "urgent",
      "location": "grid 901234"
    },
    "confidence": 0.95
  }'

# Update soldier status
curl -X PUT "http://10.3.35.27:8000/soldiers/ALPHA_05/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "injured"
  }'
```

## MQTT Integration

The system also supports MQTT for real-time communication:

- **Topic**: `soldiers/inputs` - For receiving raw inputs from soldier devices
- **Topic**: `soldiers/heartbeat` - For soldier device heartbeat messages

MQTT messages should be in JSON format matching the raw input structure.
