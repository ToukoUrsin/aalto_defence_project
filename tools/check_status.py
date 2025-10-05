#!/usr/bin/env python3
"""
Status Check for Military Hierarchy System
"""

import requests
import subprocess
import sys

def check_port(port):
    """Check if a port is listening."""
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        return f":{port}" in result.stdout
    except:
        return False

def check_service(url, name):
    """Check if a service is responding."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: {url} - WORKING")
            return True
        else:
            print(f"❌ {name}: {url} - Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: {url} - NOT RUNNING")
        return False
    except Exception as e:
        print(f"❌ {name}: {url} - ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("Military Hierarchy System - Status Check")
    print("=" * 60)
    
    # Check ports
    print("\n🔍 Checking Ports:")
    ports = [8000, 3000, 3001]
    for port in ports:
        if check_port(port):
            print(f"✅ Port {port}: LISTENING")
        else:
            print(f"❌ Port {port}: NOT LISTENING")
    
    # Check services
    print("\n🌐 Checking Services:")
    services = [
        ("https://military-hierarchy-backend.onrender.com/", "Backend API"),
        ("http://localhost:3000/", "Main Dashboard"),
        ("http://localhost:3001/", "Reports UI")
    ]
    
    working_services = 0
    for url, name in services:
        if check_service(url, name):
            working_services += 1
    
    print(f"\n📊 Summary: {working_services}/{len(services)} services working")
    
    if working_services == len(services):
        print("\n🎉 All services are running!")
        print("\nYour Military Hierarchy System is ready!")
        print("Check the ngrok windows for your public URLs.")
    else:
        print("\n⚠️  Some services are not running.")
        print("Try starting them manually:")
        print("1. Backend API: python backend.py")
        print("2. Main Dashboard: cd mil_dashboard && npm run dev")
        print("3. Reports UI: cd ui-for-reports/frontend && npm run dev")

if __name__ == "__main__":
    main()
