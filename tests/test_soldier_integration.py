#!/usr/bin/env python3
"""
Test script to verify soldier assistant integration with backend.
Run this from the main project directory.
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
        print("[OK] Connected to MQTT broker")
    else:
        print(f"[ERROR] Failed to connect to MQTT broker. Return code: {rc}")

def test_soldier_input():
    """Test sending soldier input to backend."""
    print("\n[TEST] Testing soldier input...")
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    
    # Wait for connection
    time.sleep(2)
    
    # Test commands
    test_commands = [
        "Hey Assistant, give me the OPORD",
        "Hey Assistant, I need a FRAGO", 
        "Hey Assistant, report enemy contact",
        "Hey Assistant, what's the status"
    ]
    
    for i, command_text in enumerate(test_commands, 1):
        print(f"\n[SEND] Test {i}: {command_text}")
        
        # Create payload (same format as soldier assistant)
        payload = {
            "soldier_id": SOLDIER_ID,
            "soldier_name": SOLDIER_NAME,
            "unit_id": UNIT_ID,
            "timestamp": datetime.now().isoformat(),
            "raw_text": command_text,
            "action": "OPORD" if "OPORD" in command_text else "FRAGO" if "FRAGO" in command_text else "UNKNOWN",
            "audio_file_ref": None
        }
        
        # Publish to backend topic
        client.publish("soldiers/inputs", json.dumps(payload))
        print(f"   [MQTT] Sent: {json.dumps(payload, indent=2)}")
        time.sleep(1)
    
    # Test heartbeat
    print(f"\n[HEARTBEAT] Testing heartbeat...")
    heartbeat_payload = {
        "soldier_id": SOLDIER_ID,
        "soldier_name": SOLDIER_NAME,
        "unit_id": UNIT_ID,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }
    
    client.publish("soldiers/heartbeat", json.dumps(heartbeat_payload))
    print(f"   [MQTT] Sent heartbeat: {json.dumps(heartbeat_payload, indent=2)}")
    
    client.loop_stop()
    client.disconnect()
    
    print("\n[SUCCESS] Test completed!")
    print("\n[INFO] Check your backend logs to verify messages were received:")
    print("   - Backend should show soldier inputs in the database")
    print("   - Backend should show heartbeat messages")
    print("   - Check https://military-hierarchy-backend.onrender.com//reports for new data")

def test_backend_connection():
    """Test if backend is running and accessible."""
    print("[CHECK] Testing backend connection...")
    
    try:
        import requests
        response = requests.get("https://military-hierarchy-backend.onrender.com//")
        if response.status_code == 200:
            print("[OK] Backend is running and accessible")
            return True
        else:
            print(f"[ERROR] Backend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend: {e}")
        print("   Make sure backend is running: python backend.py")
        return False

def test_mqtt_connection():
    """Test if MQTT broker is accessible."""
    print("[CHECK] Testing MQTT connection...")
    
    try:
        client = mqtt.Client()
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.disconnect()
        print("[OK] MQTT broker is accessible")
        return True
    except Exception as e:
        print(f"[ERROR] Cannot connect to MQTT broker: {e}")
        print("   Make sure MQTT broker is running: mosquitto -v")
        return False

def main():
    """Main test function."""
    print("Soldier Assistant Integration Test")
    print("=" * 50)
    
    # Test connections first
    backend_ok = test_backend_connection()
    mqtt_ok = test_mqtt_connection()
    
    if not backend_ok or not mqtt_ok:
        print("\n[ERROR] Prerequisites not met. Please fix the issues above and try again.")
        return
    
    print("\n[OK] All prerequisites met. Running integration test...")
    
    # Run the actual test
    test_soldier_input()
    
    print("\n[INFO] Next steps:")
    print("   1. Check backend logs for received messages")
    print("   2. Visit https://military-hierarchy-backend.onrender.com//reports to see new data")
    print("   3. Test with actual soldier assistant: cd soldier_assistant && python test_simple.py")

if __name__ == "__main__":
    main()
