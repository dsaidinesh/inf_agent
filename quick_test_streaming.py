#!/usr/bin/env python3
"""
Quick test of the streaming campaign trigger endpoint
"""

import requests
import json
import time

def test_streaming_campaign():
    """Test the streaming campaign trigger"""
    # Use a real campaign ID that exists
    campaign_id = "11111111-2222-3333-4444-555555555555"
    url = f"http://localhost:8000/api/campaign-trigger/trigger/{campaign_id}/stream"
    
    print(f"🎯 Testing streaming campaign trigger")
    print(f"📡 URL: {url}")
    print(f"⏱️  Starting at: {time.strftime('%H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Make streaming request
        response = requests.get(url, stream=True, timeout=60)
        
        if response.status_code == 200:
            print("✅ Connected to stream")
            
            # Read streaming data
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # Parse SSE format
                    if line.startswith('data: '):
                        json_data = line[6:]
                        try:
                            data = json.loads(json_data)
                            timestamp = time.strftime('%H:%M:%S')
                            progress = data.get('progress', 'N/A')
                            message = data.get('message', 'No message')
                            status = data.get('status', 'unknown')
                            
                            print(f"[{timestamp}] ({progress}%) {status.upper()}: {message}")
                            
                            # Show additional data if available
                            if 'data' in data and data['data']:
                                extra_data = data['data']
                                if 'creator_name' in extra_data:
                                    print(f"    👤 Creator: {extra_data['creator_name']}")
                                if 'final_rate' in extra_data:
                                    print(f"    💰 Rate: ${extra_data['final_rate']:,}")
                                if 'influencer_count' in extra_data:
                                    print(f"    📊 Found: {extra_data['influencer_count']} influencers")
                            
                            # Exit on completion or error
                            if status in ['completed', 'error']:
                                print(f"\n🏁 Stream completed with status: {status}")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"Raw data: {line}")
                    else:
                        print(f"Non-data line: {line}")
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    
    print(f"\n✅ Test completed at: {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    test_streaming_campaign() 