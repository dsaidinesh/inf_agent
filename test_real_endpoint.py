#!/usr/bin/env python3
"""
Test the actual streaming endpoint with real campaign ID
"""

import requests
import json
from datetime import datetime

def test_streaming_endpoint():
    """Test the streaming endpoint"""
    
    campaign_id = "49baa7a8-99c4-4caf-b140-d905e2338432"
    url = f"http://localhost:8000/api/campaign-trigger/trigger/{campaign_id}/stream?max_creators=3"
    
    print("🎯 Testing Campaign Trigger Streaming Endpoint")
    print("=" * 60)
    print(f"📊 Campaign ID: {campaign_id}")
    print(f"🔗 URL: {url}")
    print("\n🎯 Expected: Detailed call progress (no 50% → 90% jump)")
    print("=" * 60)
    print()
    
    try:
        # Make streaming request
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return
        
        print("✅ Connected to streaming endpoint")
        print("📡 Streaming data...")
        print("=" * 60)
        
        update_count = 0
        detailed_logs_seen = []
        
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                try:
                    update_count += 1
                    data = json.loads(line[6:])  # Remove "data: " prefix
                    
                    # Format timestamp
                    timestamp = datetime.fromisoformat(data['timestamp']).strftime("%H:%M:%S")
                    
                    # Get info
                    status = data['status']
                    message = data['message']
                    progress = data.get('progress', 'N/A')
                    
                    # Track detailed logs that prove enhancement is working
                    detailed_statuses = ['call_setup', 'dialing', 'connecting', 'negotiating', 'call_completed']
                    if status in detailed_statuses:
                        detailed_logs_seen.append(status)
                    
                    # Format progress
                    if isinstance(progress, (int, float)) and progress >= 0:
                        progress_str = f"({progress}%)"
                    else:
                        progress_str = ""
                    
                    # Print formatted log
                    print(f"{timestamp} 📡 {message} {progress_str}")
                    
                    # Highlight the key improvements
                    if status in detailed_statuses:
                        print(f"       🎉 ENHANCED: Detailed call progress shown!")
                    
                    # Stop after completion or error
                    if status in ['completed', 'error']:
                        break
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse: {line}")
        
        # Print test summary
        print("\n" + "=" * 60)
        print("🎯 Campaign Trigger Streaming Test Results")
        print("=" * 60)
        print(f"📊 Total updates received: {update_count}")
        print(f"🎉 Detailed call logs seen: {len(detailed_logs_seen)}")
        
        if detailed_logs_seen:
            print("✅ SUCCESS: Enhanced streaming is working!")
            print("✅ Detailed call statuses found:")
            for status in detailed_logs_seen:
                print(f"   📱 {status}")
        else:
            print("⚠️ Note: Campaign may not have reached call phase")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_streaming_endpoint() 