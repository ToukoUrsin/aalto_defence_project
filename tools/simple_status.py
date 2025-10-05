#!/usr/bin/env python3
"""
Simple Status Check for Military Hierarchy System
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
            print(f"OK {name}: {url} - WORKING")
            return True
        else:
            print(f"ERROR {name}: {url} - Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"ERROR {name}: {url} - NOT RUNNING")
        return False
    except Exception as e:
        print(f"ERROR {name}: {url} - ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("Military Hierarchy System - Status Check")
    print("=" * 60)
    
    # Check ports
    print("\nChecking Ports:")
    ports = [8000, 3000]
    for port in ports:
        if check_port(port):
            print(f"OK Port {port}: LISTENING")
        else:
            print(f"ERROR Port {port}: NOT LISTENING")
    
    # Check services
    print("\nChecking Services:")
    services = [
        ("https://military-hierarchy-backend.onrender.com/", "Backend API"),
        ("http://localhost:3000/", "Unified Dashboard (includes Reports)")
    ]
    
    working_services = 0
    for url, name in services:
        if check_service(url, name):
            working_services += 1
    
    print(f"\nSummary: {working_services}/{len(services)} services working")
    
    if working_services == len(services):
        print("\nSUCCESS! All services are running!")
        print("\nYour Military Hierarchy System is ready!")
        print("Check the ngrok windows for your public URLs.")
    else:
        print("\nWARNING: Some services are not running.")
        print("Try starting them manually:")
        print("1. Backend API: python backend.py")
        print("2. Unified Dashboard: cd mil_dashboard && npm run dev")

if __name__ == "__main__":
    main()
