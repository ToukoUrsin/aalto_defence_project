#!/usr/bin/env python3
"""
Simple test script to verify soldier assistant MQTT integration.
This simulates voice commands without needing audio hardware.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant.mqqtt_client import publish_command, publish_heartbeat
import time
import json

def test_voice_commands():
    """Test various voice commands by simulating the payload."""
    print("Testing voice commands...")
    print("=" * 50)
    
    # Test commands (simulating what the voice assistant would send)
    test_commands = [
        {
            "text": "Hey Assistant, give me the OPORD",
            "action": "OPORD"
        },
        {
            "text": "Hey Assistant, I need a FRAGO",
            "action": "FRAGO"
        },
        {
            "text": "Hey Assistant, what's the status",
            "action": "UNKNOWN"
        },
        {
            "text": "Hey Assistant, report enemy contact",
            "action": "UNKNOWN"
        }
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\nTest {i}: Sending command...")
        print(f"   Text: {cmd['text']}")
        print(f"   Action: {cmd['action']}")
        
        # Create payload (same format as main.py would create)
        payload = {
            "action": cmd["action"],
            "text": cmd["text"]
        }
        
        # Send command
        publish_command(json.dumps(payload))
        time.sleep(1)  # Wait between commands

def test_heartbeat():
    """Test heartbeat functionality."""
    print("\nTesting heartbeat...")
    print("=" * 30)
    
    for i in range(3):
        print(f"Heartbeat {i+1}/3...")
        publish_heartbeat()
        time.sleep(2)

def test_manual_commands():
    """Interactive test for manual command input."""
    print("\nInteractive Test Mode")
    print("=" * 30)
    print("Enter commands manually (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not user_input:
                continue
                
            # Create payload
            payload = {
                "action": "MANUAL_TEST",
                "text": user_input
            }
            
            print(f"Sending: {user_input}")
            publish_command(json.dumps(payload))
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting interactive mode...")

def main():
    """Main test function."""
    print("Soldier Assistant MQTT Test")
    print("=" * 50)
    print("This test simulates voice commands without audio hardware.")
    print("Make sure your backend is running and MQTT broker is available.")
    print()
    
    try:
        # Test 1: Voice commands
        test_voice_commands()
        
        # Test 2: Heartbeat
        test_heartbeat()
        
        # Test 3: Interactive mode
        test_manual_commands()
        
        print("\nAll tests completed!")
        print("\nCheck your backend logs to verify messages were received:")
        print("   - Backend should show soldier inputs in the database")
        print("   - Backend should show heartbeat messages")
        print("   - Check https://military-hierarchy-backend.onrender.com//reports for new data")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("\nTroubleshooting:")
        print("   1. Make sure MQTT broker is running: mosquitto -v")
        print("   2. Make sure backend is running: python backend.py")
        print("   3. Check network connection to localhost:1883")

if __name__ == "__main__":
    main()
