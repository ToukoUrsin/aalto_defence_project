#!/usr/bin/env python3
"""
Test script to verify soldier assistant integration with backend.
This script simulates soldier commands and tests MQTT communication.
"""

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
SOLDIER_ID = "soldier_001"
SOLDIER_NAME = "Test_Soldier"
UNIT_ID = "unit_001"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("soldiers/inputs")
        client.subscribe("soldiers/heartbeat")
    else:
        print(f"❌ Failed to connect to MQTT broker. Return code: {rc}")

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📨 Received on {msg.topic}:")
        print(f"   {json.dumps(payload, indent=2)}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def test_soldier_input():
    """Test sending soldier input to backend."""
    print("\n🧪 Testing soldier input...")
    
    # Create test payload
    test_payload = {
        "soldier_id": SOLDIER_ID,
        "soldier_name": SOLDIER_NAME,
        "unit_id": UNIT_ID,
        "timestamp": datetime.now().isoformat(),
        "raw_text": "This is a test OPORD command",
        "action": "OPORD",
        "audio_file_ref": None
    }
    
    # Publish to backend topic
    client.publish("soldiers/inputs", json.dumps(test_payload))
    print(f"📤 Sent soldier input: {json.dumps(test_payload, indent=2)}")

def test_heartbeat():
    """Test sending heartbeat to backend."""
    print("\n💓 Testing heartbeat...")
    
    # Create heartbeat payload
    heartbeat_payload = {
        "soldier_id": SOLDIER_ID,
        "soldier_name": SOLDIER_NAME,
        "unit_id": UNIT_ID,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Publish heartbeat
    client.publish("soldiers/heartbeat", json.dumps(heartbeat_payload))
    print(f"📤 Sent heartbeat: {json.dumps(heartbeat_payload, indent=2)}")

def test_voice_commands():
    """Test various voice commands."""
    print("\n🎤 Testing voice commands...")
    
    commands = [
        {"text": "Hey Assistant, give me the OPORD", "action": "OPORD"},
        {"text": "Hey Assistant, I need a FRAGO", "action": "FRAGO"},
        {"text": "Hey Assistant, what's the status", "action": "UNKNOWN"},
    ]
    
    for cmd in commands:
        # Create soldier input payload
        payload = {
            "soldier_id": SOLDIER_ID,
            "soldier_name": SOLDIER_NAME,
            "unit_id": UNIT_ID,
            "timestamp": datetime.now().isoformat(),
            "raw_text": cmd["text"],
            "action": cmd["action"],
            "audio_file_ref": None
        }
        
        client.publish("soldiers/inputs", json.dumps(payload))
        print(f"📤 Sent command: {cmd['text']} -> {cmd['action']}")
        time.sleep(1)

def main():
    """Main test function."""
    global client
    
    print("🚀 Starting Soldier Assistant Integration Test")
    print("=" * 50)
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to MQTT broker
        print(f"🔌 Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Run tests
        test_soldier_input()
        time.sleep(1)
        
        test_heartbeat()
        time.sleep(1)
        
        test_voice_commands()
        time.sleep(2)
        
        print("\n✅ Integration test completed!")
        print("\n📋 Check the backend logs to verify messages were received.")
        print("   - Backend should show soldier inputs in the database")
        print("   - Backend should show heartbeat messages")
        print("   - Check https://military-hierarchy-backend.onrender.com//reports for new data")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
