#!/usr/bin/env python3
"""
Test script for streaming endpoints using curl and HTTP requests.
This demonstrates how to test the streaming functionality from command line.
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def test_curl_streaming():
    """Test the streaming endpoint using curl"""
    print("🧪 Testing Streaming Endpoints with curl")
    print("=" * 50)
    
    # Test basic connectivity first
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"📊 Service: {data.get('service')}")
            print(f"🔖 Version: {data.get('version')}")
            
            # Show available endpoints
            if 'streaming_endpoints' in data:
                print("\n📡 Available Streaming Endpoints:")
                for name, endpoint in data['streaming_endpoints'].items():
                    print(f"   {name}: {endpoint}")
            
            # Show curl examples
            if 'curl_examples' in data:
                print("\n💻 Curl Examples:")
                for name, command in data['curl_examples'].items():
                    print(f"   {name}: {command}")
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to server: {e}")
        print("Make sure the server is running with: python main.py")
        return False
    
    print("\n" + "=" * 50)
    print("🚀 Testing Streaming with curl")
    print("=" * 50)
    
    # Test the demo streaming endpoint
    print("\n1️⃣ Testing Demo Stream (GET /agent/stream)")
    print("Command: curl http://localhost:8000/agent/stream")
    print("Expected: Server-Sent Events stream with demo agent logs")
    print("\nTo test manually, run:")
    print("curl http://localhost:8000/agent/stream")
    print("\nYou should see output like:")
    print("data: {\"message\": \"Demo agent starting...\", \"status\": \"starting\", ...}")
    
    # Test campaign streaming endpoint  
    print("\n2️⃣ Testing Campaign Stream (POST /agent/campaign/stream)")
    print("This endpoint requires POST data with campaign information")
    
    # Create sample campaign data
    sample_campaign = {
        "id": "test_campaign_123",
        "brand_name": "TechCorp",
        "product_name": "Smart Watch Pro",
        "product_description": "Advanced fitness tracking smartwatch",
        "product_niche": "tech",
        "target_audience": "tech enthusiasts",
        "total_budget": 5000
    }
    
    print("\nSample curl command for campaign streaming:")
    print("curl -X POST http://localhost:8000/agent/campaign/stream \\")
    print("  -H 'Content-Type: application/json' \\")
    print(f"  -d '{json.dumps(sample_campaign, indent=2)}'")
    
    # Test health check
    print("\n3️⃣ Testing Health Check")
    print("Command: curl http://localhost:8000/health")
    
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Health check successful")
            print(f"Status: {health_data.get('status')}")
            if 'services' in health_data:
                print("Services:")
                for service, status in health_data['services'].items():
                    print(f"  {service}: {status.get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Instructions for frontend testing
    print("\n" + "=" * 50)
    print("🌐 Frontend Testing")
    print("=" * 50)
    
    frontend_path = Path("frontend_example/streaming_logs_demo.html")
    if frontend_path.exists():
        print("✅ Frontend demo found")
        print(f"Open in browser: file://{frontend_path.absolute()}")
        print("Then click 'Start Agent' to see live streaming!")
    else:
        print("❌ Frontend demo not found")
    
    return True

def run_interactive_curl_test():
    """Run an interactive curl test"""
    print("\n🎮 Interactive curl Test")
    print("Would you like to run a live curl test? (y/n): ", end="")
    
    choice = input().lower().strip()
    if choice == 'y':
        print("\n🚀 Running curl test...")
        try:
            # Run curl command and stream output
            cmd = ["curl", "http://localhost:8000/agent/stream"]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("📡 Streaming data (Press Ctrl+C to stop):")
            print("-" * 40)
            
            try:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
            except KeyboardInterrupt:
                process.terminate()
                print("\n🛑 Stream stopped by user")
                
        except FileNotFoundError:
            print("❌ curl command not found. Please install curl or test in browser.")
        except Exception as e:
            print(f"❌ Error running curl: {e}")

def main():
    """Main function"""
    print("🔥 InfluencerFlow AI - Streaming Test Suite")
    print("=" * 60)
    
    if test_curl_streaming():
        run_interactive_curl_test()
    
    print("\n✅ Test completed!")
    print("\nNext steps:")
    print("1. Open the frontend demo in your browser")
    print("2. Test with curl commands shown above")
    print("3. Integrate streaming into your own frontend")

if __name__ == "__main__":
    main() 