#!/usr/bin/env python3
"""
Test script for the streaming logs FastAPI server.
This script will start the server and provide instructions for testing.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install fastapi uvicorn")
        return False
    
    print("✅ All required packages are installed")
    return True

def test_server_connection():
    """Test if the server is responding"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding correctly")
            print(f"Health check response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to server: {e}")
        return False

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI streaming logs server...")
    print("Server will be available at: http://localhost:8000")
    print("Streaming endpoint: http://localhost:8000/agent/stream")
    print("Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Run the server using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.streaming_logs:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")

def main():
    """Main function to test the streaming logs setup"""
    print("🧪 Testing Streaming Logs Implementation")
    print("=" * 50)
    
    # Check if required packages are installed
    if not check_requirements():
        return
    
    # Check if the streaming_logs.py file exists
    streaming_logs_path = Path("api/streaming_logs.py")
    if not streaming_logs_path.exists():
        print(f"❌ Streaming logs file not found: {streaming_logs_path}")
        print("Make sure the file api/streaming_logs.py exists")
        return
    
    print("✅ Streaming logs file found")
    
    # Check if the HTML demo file exists
    demo_path = Path("frontend_example/streaming_logs_demo.html")
    if demo_path.exists():
        print("✅ Frontend demo file found")
        print(f"Demo available at: {demo_path.absolute()}")
    else:
        print("⚠️  Frontend demo file not found (optional)")
    
    print("\n📋 Testing Instructions:")
    print("1. The server will start on http://localhost:8000")
    print("2. Open the frontend demo in your browser:")
    print(f"   file://{demo_path.absolute()}")
    print("3. Click 'Start Agent' to see streaming logs")
    print("4. You can also test the API directly:")
    print("   curl http://localhost:8000/agent/stream")
    
    input("\nPress Enter to start the server...")
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main() 