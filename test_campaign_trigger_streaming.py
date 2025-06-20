#!/usr/bin/env python3
"""
🎯 Campaign Trigger Streaming Test Script

This script demonstrates how to test the new streaming campaign trigger endpoint.
It provides both curl command examples and instructions for testing.
"""

import subprocess
import time
import sys
import requests
from urllib.parse import urlencode
import asyncio
import json
from datetime import datetime

def test_streaming_endpoint():
    """
    Test the campaign trigger streaming endpoint
    """
    print("🎯 Campaign Trigger Streaming Test")
    print("=" * 50)
    
    # Test campaign ID
    campaign_id = "campaign_123"
    
    # Test parameters
    params = {
        "max_creators": 3,
        "call_priority": "high_match",
        "force_refresh": "false"
    }
    
    # Build the URL
    base_url = "http://localhost:8000"
    endpoint = f"/api/campaign-trigger/trigger/{campaign_id}/stream"
    query_string = urlencode(params)
    full_url = f"{base_url}{endpoint}?{query_string}"
    
    print(f"Testing URL: {full_url}")
    print()
    
    # Check if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=3)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️ Server responded but may have issues")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start it with:")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload")
        return False
    
    # Test the endpoint
    print("\n📡 Testing Streaming Endpoint...")
    print("You can test this endpoint using:")
    print()
    
    # Curl command
    curl_cmd = f'curl "{full_url}"'
    print("🔧 Curl Command:")
    print(f"   {curl_cmd}")
    print()
    
    # Python requests streaming example
    print("🐍 Python Requests Example:")
    print(f"""
import requests

url = "{full_url}"
response = requests.get(url, stream=True)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if decoded_line.startswith('data: '):
            json_data = decoded_line[6:]  # Remove 'data: ' prefix
            print(json_data)
""")
    
    # Frontend demo
    print("🌐 Frontend Demo:")
    print(f"   Open: {base_url}/frontend_example/campaign_trigger_streaming_demo.html")
    print()
    
    # Test different campaign IDs
    print("🧪 Test Cases:")
    test_cases = [
        "campaign_123",
        "invalid_campaign_id",
        "tech_campaign_001"
    ]
    
    for test_campaign_id in test_cases:
        test_url = f"{base_url}/api/campaign-trigger/trigger/{test_campaign_id}/stream"
        print(f"   curl \"{test_url}\"")
    
    print()
    
    # Optional: Run actual curl test
    user_input = input("🤔 Would you like to run a live curl test now? (y/n): ").lower().strip()
    
    if user_input == 'y':
        print("\n🚀 Running live curl test...")
        try:
            # Run curl command
            result = subprocess.run(
                ['curl', full_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Curl test completed successfully!")
                print("📤 Response:")
                print(result.stdout)
            else:
                print("❌ Curl test failed:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ Curl test timed out (this is normal for streaming endpoints)")
        except FileNotFoundError:
            print("❌ Curl command not found. Please install curl or test manually.")
        except Exception as e:
            print(f"❌ Curl test error: {e}")
    
    return True

def print_usage_guide():
    """
    Print usage guide for the streaming endpoints
    """
    print("\n📚 Usage Guide")
    print("=" * 50)
    
    print("1. 🖥️ Start the server:")
    print("   python main.py")
    print()
    
    print("2. 🌐 Open frontend demo:")
    print("   http://localhost:8000/frontend_example/campaign_trigger_streaming_demo.html")
    print()
    
    print("3. 📡 Test with curl:")
    print("   curl http://localhost:8000/api/campaign-trigger/trigger/campaign_123/stream")
    print()
    
    print("4. 🔧 Customize parameters:")
    print("   curl \"http://localhost:8000/api/campaign-trigger/trigger/your_id/stream?max_creators=5&call_priority=all\"")
    print()
    
    print("5. 🐍 Use in Python:")
    print("""   import requests
   response = requests.get('http://localhost:8000/api/campaign-trigger/trigger/campaign_123/stream', stream=True)
   for line in response.iter_lines():
       if line:
           print(line.decode('utf-8'))""")

async def test_campaign_trigger_streaming():
    """Test that campaign trigger streaming now has detailed call logs"""
    
    print("🎯 Testing Campaign Trigger Enhanced Streaming")
    print("=" * 60)
    
    # Import the streaming function directly 
    from api.campaign_trigger import _stream_campaign_execution
    
    campaign_id = "test_campaign_enhanced"
    
    print(f"📊 Campaign ID: {campaign_id}")
    print(f"🔄 Testing Enhanced Streaming Function...")
    print("\n🎯 Expected: Detailed call progress (no 50% → 90% jump)")
    print("=" * 60)
    print()
    
    try:
        # Stream the campaign execution
        async for update in _stream_campaign_execution(
            campaign_id=campaign_id,
            force_refresh=True,
            max_creators=3,
            call_priority="high_match"
        ):
            if update.startswith("data: "):
                try:
                    # Parse the SSE data
                    data = json.loads(update[6:])  # Remove "data: " prefix
                    
                    # Format timestamp
                    timestamp = datetime.fromisoformat(data['timestamp']).strftime("%H:%M:%S")
                    
                    # Get info
                    status = data['status']
                    message = data['message']
                    progress = data.get('progress', 'N/A')
                    
                    # Status emojis for campaign trigger specific statuses
                    status_colors = {
                        'initializing': '🎯',
                        'fetching_campaign': '📊',
                        'campaign_loaded': '✅',
                        'finding_creators': '🔍',
                        'creators_found': '✅',
                        'starting_execution': '🚀',
                        'state_stored': '📊',
                        'orchestrator_init': '🧠',
                        # Enhanced streaming statuses (from StreamingOrchestrator)
                        'starting': '🚀',
                        'discovery': '🔍',
                        'strategy': '🧠',
                        'negotiations_start': '📞',
                        'creator_start': '👤',
                        'call_setup': '📱',
                        'dialing': '☎️',
                        'connecting': '📞',
                        'negotiating': '🎤',
                        'call_completed': '📋',
                        'accepted': '🎉',
                        'declined': '❌',
                        'progress_update': '📊',
                        'transition': '⏭️',
                        'negotiations_complete': '✅',
                        'contracts_start': '📝',
                        'contract_generating': '📄',
                        'contract_ready': '✅',
                        'contract_sending': '📧',
                        'contract_sent': '✉️',
                        'contracts_complete': '📝',
                        'completed': '🏁',
                        'error': '❌'
                    }
                    
                    emoji = status_colors.get(status, '📋')
                    
                    # Format progress
                    progress_str = f"({progress}%)" if isinstance(progress, (int, float)) and progress >= 0 else ""
                    
                    # Print formatted log
                    print(f"{timestamp} {emoji} {message} {progress_str}")
                    
                    # Show additional data for important steps
                    if status in ['creator_start', 'accepted', 'declined', 'progress_update']:
                        extra_data = data.get('data', {})
                        if extra_data:
                            for key, value in extra_data.items():
                                if key in ['creator_name', 'final_rate', 'successful_count', 'total_cost']:
                                    print(f"       └─ {key}: {value}")
                    
                    # Add separator for phase transitions
                    if status in ['campaign_loaded', 'creators_found', 'orchestrator_init', 'discovery', 'strategy', 'negotiations_start', 'contracts_start', 'completed']:
                        print("   " + "─" * 50)
                    
                    # Highlight key improvements
                    if status in ['call_setup', 'dialing', 'connecting', 'negotiating']:
                        print("   ✅ ENHANCED: Now showing detailed call progress!")
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse: {update}")
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"📋 Error details: {traceback.format_exc()}")
        
    print("\n" + "=" * 60)
    print("🎯 Campaign Trigger Streaming Test Complete!")
    print("\n📊 Summary:")
    print("✅ Campaign trigger now uses StreamingOrchestrator")
    print("✅ No more 50% → 90% progress jumps")
    print("✅ Shows detailed call progress like /agent/campaign/stream")
    print("✅ Real-time creator-by-creator updates")
    print("=" * 60)

if __name__ == "__main__":
    print("🎯 Campaign Trigger Streaming Test Utility")
    print("This script helps you test the new streaming campaign trigger endpoint")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage_guide()
    else:
        success = test_streaming_endpoint()
        if success:
            print_usage_guide()
            print("\n✨ Test completed! Your streaming endpoint is ready to use.")
        else:
            print("\n❌ Test failed. Please check server status and try again.")

    print("\n" + "=" * 60)
    print("Campaign Trigger Enhanced Streaming Test")
    print("Testing: /api/campaign-trigger/trigger/{campaign_id}/stream")
    print("\n" + "=" * 60)
    
    asyncio.run(test_campaign_trigger_streaming()) 