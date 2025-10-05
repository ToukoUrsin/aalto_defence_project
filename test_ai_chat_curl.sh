#!/bin/bash
# Corrected curl command for testing /ai/chat endpoint
# The structured_json field must be a JSON STRING, not a Python dict

curl -X 'POST' \
  'https://military-hierarchy-backend.onrender.com/ai/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "What is the current tactical situation for 1st Infantry Battalion?",
    "context": {
        "node": {
            "name": "1st Infantry Battalion",
            "unit_id": "unit-001",
            "level": 2
        },
        "reports": [
            {
                "report_type": "SITREP",
                "timestamp": "2025-10-04T22:47:17.499795",
                "soldier_name": "Cpl. Smith",
                "structured_json": "{\"status\": \"All units operational\", \"location\": \"Grid 123456\", \"engagement_status\": \"No contact\"}"
            },
            {
                "report_type": "CONTACT",
                "timestamp": "2025-10-04T22:45:00.000000",
                "soldier_name": "Sgt. Johnson",
                "structured_json": "{\"enemy_count\": 5, \"location\": \"Grid 124567\", \"enemy_type\": \"Infantry\", \"description\": \"Small patrol observed\"}"
            },
            {
                "report_type": "CASUALTY",
                "timestamp": "2025-10-04T22:30:00.000000",
                "soldier_name": "Pvt. Williams",
                "structured_json": "{\"casualty_count\": 1, \"severity\": \"minor\", \"location\": \"Grid 123450\", \"injuries\": \"Ankle sprain\"}"
            }
        ]
    }
}'
