#!/usr/bin/env python3
"""
Startup script for the Military Hierarchy System
Initializes database and starts the backend server
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Starting Military Hierarchy System...")
    
    # Check if we're in the right directory
    if not Path("database_setup.py").exists():
        print("❌ Error: database_setup.py not found. Please run from project root.")
        sys.exit(1)
    
    # Initialize database
    print("📊 Initializing database...")
    if not run_command("python database_setup.py"):
        print("❌ Failed to initialize database")
        sys.exit(1)
    print("✅ Database initialized successfully")
    
    # Check if MQTT broker is available
    print("🔍 Checking MQTT broker...")
    try:
        import paho.mqtt.client as mqtt
        client = mqtt.Client()
        client.connect("localhost", 1883, 5)
        client.disconnect()
        print("✅ MQTT broker is available")
    except Exception as e:
        print("⚠️  Warning: MQTT broker not available on localhost:1883")
        print("   Install and start Mosquitto broker for full functionality")
        print("   On Windows: Download from https://mosquitto.org/download/")
        print("   On Linux: sudo apt install mosquitto mosquitto-clients")
    
    # Start backend server
    print("🌐 Starting FastAPI backend server...")
    print("   Backend will be available at: https://military-hierarchy-backend.onrender.com/")
    print("   API docs will be available at: https://military-hierarchy-backend.onrender.com/docs")
    print("")
    
    # Start the backend
    try:
        run_command("python backend.py")
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    
    print("👋 Military Hierarchy System shutdown complete")

if __name__ == "__main__":
    main()
