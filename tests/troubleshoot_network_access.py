#!/usr/bin/env python3
"""
Network Access Troubleshooting Tool
This script helps diagnose why external devices can't access the services.
"""

import requests
import socket
import subprocess
import sys
import json
from datetime import datetime

# Your network IP
LOCAL_IP = "10.3.35.27"

def test_local_access():
    """Test if services are accessible locally."""
    print("=" * 60)
    print("TESTING LOCAL ACCESS")
    print("=" * 60)
    
    services = [
        (f"https://military-hierarchy-backend.onrender.com//", "Backend API (localhost)"),
        (f"http://localhost:3000/", "Main Dashboard (localhost)"),
        (f"http://localhost:3001/", "Reports UI (localhost)"),
        (f"http://{LOCAL_IP}:8000/", "Backend API (network IP)"),
        (f"http://{LOCAL_IP}:3000/", "Main Dashboard (network IP)"),
        (f"http://{LOCAL_IP}:3001/", "Reports UI (network IP)")
    ]
    
    results = {}
    for url, name in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"OK {name}: {url}")
                results[name] = True
            else:
                print(f"ERROR {name}: {url} - Status {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"ERROR {name}: {url} - {e}")
            results[name] = False
    
    return results

def test_network_connectivity():
    """Test basic network connectivity."""
    print("\n" + "=" * 60)
    print("TESTING NETWORK CONNECTIVITY")
    print("=" * 60)
    
    # Test if we can bind to the network interface
    try:
        # Test if we can create a socket on the network interface
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((LOCAL_IP, 8000))
        sock.close()
        
        if result == 0:
            print(f"OK Network connectivity to {LOCAL_IP}:8000")
        else:
            print(f"ERROR Cannot connect to {LOCAL_IP}:8000")
            return False
    except Exception as e:
        print(f"ERROR Network connectivity test failed: {e}")
        return False
    
    return True

def check_firewall_rules():
    """Check Windows Firewall rules."""
    print("\n" + "=" * 60)
    print("CHECKING WINDOWS FIREWALL")
    print("=" * 60)
    
    try:
        # Check firewall status
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                              capture_output=True, text=True, timeout=10)
        
        if "State                                 ON" in result.stdout:
            print("WARNING: Windows Firewall is ON")
            print("This might be blocking external connections.")
        else:
            print("OK: Windows Firewall appears to be OFF or configured")
        
        # Check for specific rules
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                              capture_output=True, text=True, timeout=10)
        
        if "8000" in result.stdout or "3000" in result.stdout or "3001" in result.stdout:
            print("OK: Found firewall rules for our ports")
        else:
            print("WARNING: No specific firewall rules found for our ports")
            
    except Exception as e:
        print(f"ERROR: Could not check firewall: {e}")

def get_network_info():
    """Get detailed network information."""
    print("\n" + "=" * 60)
    print("NETWORK INFORMATION")
    print("=" * 60)
    
    try:
        # Get IP configuration
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
        print("IP Configuration:")
        print(result.stdout)
        
        # Get network interfaces
        result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                              capture_output=True, text=True, timeout=10)
        print("\nNetwork Interfaces:")
        print(result.stdout)
        
    except Exception as e:
        print(f"ERROR: Could not get network info: {e}")

def test_port_accessibility():
    """Test if ports are accessible from network."""
    print("\n" + "=" * 60)
    print("TESTING PORT ACCESSIBILITY")
    print("=" * 60)
    
    ports = [8000, 3000, 3001]
    
    for port in ports:
        try:
            # Try to connect to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((LOCAL_IP, port))
            sock.close()
            
            if result == 0:
                print(f"OK Port {port} is accessible on {LOCAL_IP}")
            else:
                print(f"ERROR Port {port} is NOT accessible on {LOCAL_IP}")
                
        except Exception as e:
            print(f"ERROR Testing port {port}: {e}")

def create_troubleshooting_guide():
    """Create a troubleshooting guide for your friend."""
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING GUIDE FOR YOUR FRIEND")
    print("=" * 60)
    
    print("If your friend can't access the services, try these steps:")
    print()
    print("1. VERIFY NETWORK CONNECTION:")
    print("   - Make sure your friend is on the SAME WiFi network")
    print("   - Check WiFi name matches exactly")
    print("   - Try connecting to a different device first")
    print()
    print("2. TEST BASIC CONNECTIVITY:")
    print("   - Ask your friend to ping your computer:")
    print(f"     ping {LOCAL_IP}")
    print("   - If ping fails, they're not on the same network")
    print()
    print("3. CHECK FIREWALL SETTINGS:")
    print("   - Open Windows Defender Firewall")
    print("   - Click 'Allow an app or feature through Windows Defender Firewall'")
    print("   - Make sure Python and Node.js are allowed")
    print("   - Or temporarily disable firewall for testing")
    print()
    print("4. VERIFY SERVICES ARE RUNNING:")
    print("   - Check that all services are still running")
    print("   - Restart services if needed")
    print()
    print("5. TEST FROM YOUR COMPUTER:")
    print("   - Open browser on YOUR computer")
    print(f"   - Go to: http://{LOCAL_IP}:3000")
    print("   - If it works for you but not your friend, it's a network issue")
    print()
    print("6. ALTERNATIVE TESTING:")
    print("   - Ask your friend to try: http://10.3.35.27:8000/docs")
    print("   - This is the API documentation page")
    print("   - If this works, the network is fine")

def main():
    """Run comprehensive troubleshooting."""
    print("NETWORK ACCESS TROUBLESHOOTING TOOL")
    print("=" * 60)
    print(f"Testing IP: {LOCAL_IP}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    local_results = test_local_access()
    network_ok = test_network_connectivity()
    check_firewall_rules()
    get_network_info()
    test_port_accessibility()
    create_troubleshooting_guide()
    
    # Summary
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING SUMMARY")
    print("=" * 60)
    
    local_accessible = sum(local_results.values())
    total_local = len(local_results)
    
    print(f"Local Access: {local_accessible}/{total_local} services accessible")
    print(f"Network Connectivity: {'OK' if network_ok else 'FAILED'}")
    
    if local_accessible == total_local and network_ok:
        print("\nSERVICES APPEAR TO BE WORKING LOCALLY")
        print("The issue is likely:")
        print("1. Your friend is not on the same WiFi network")
        print("2. Windows Firewall is blocking external connections")
        print("3. Network configuration issue")
        print()
        print("SOLUTION: Follow the troubleshooting guide above")
    else:
        print("\nSERVICES HAVE ISSUES")
        print("Check the error messages above and fix the problems")

if __name__ == "__main__":
    main()
