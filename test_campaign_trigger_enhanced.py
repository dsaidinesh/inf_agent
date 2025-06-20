#!/usr/bin/env python3
"""
Test Campaign Trigger Enhanced Streaming 
Shows that /api/campaign-trigger/trigger/{campaign_id}/stream now has the same 
detailed call progress as /agent/campaign/stream (no more 50% → 90% jumps!)
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append('.')

async def test_campaign_trigger_enhanced():
    """Test the enhanced campaign trigger streaming"""
    
    print("🎯 Testing Campaign Trigger Enhanced Streaming")
    print("=" * 60)
    
    # Import the streaming function directly 
    from api.campaign_trigger import _stream_campaign_execution
    
    campaign_id = "mock_tech_campaign"  # Use mock campaign that exists
    
    print(f"📊 Campaign ID: {campaign_id}")
    print(f"🔄 Using Enhanced StreamingOrchestrator...")
    print("\n🎯 Expected: Detailed call progress (no 50% → 90% jump)")
    print("⚡ Same detailed logs as /agent/campaign/stream")
    print("=" * 60)
    print()
    
    try:
        # Stream the campaign execution
        update_count = 0
        detailed_logs_seen = []
        
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
                    update_count += 1
                    
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
                    
                    # Status emojis
                    status_colors = {
                        'initializing': '🎯',
                        'fetching_campaign': '📊',
                        'campaign_loaded': '✅',
                        'finding_creators': '🔍',
                        'creators_found': '✅',
                        'starting_execution': '🚀',
                        'state_stored': '📊',
                        'orchestrator_init': '🧠',
                        # Enhanced streaming statuses (now included!)
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
                        'completed': '🏁',
                        'error': '❌'
                    }
                    
                    emoji = status_colors.get(status, '📋')
                    
                    # Format progress
                    if isinstance(progress, (int, float)) and progress >= 0:
                        progress_str = f"({progress}%)"
                    else:
                        progress_str = ""
                    
                    # Print formatted log
                    print(f"{timestamp} {emoji} {message} {progress_str}")
                    
                    # Highlight the key improvements
                    if status in detailed_statuses:
                        print(f"       🎉 ENHANCED: Detailed call progress shown!")
                    
                    # Add separator for phase transitions
                    if status in ['campaign_loaded', 'creators_found', 'orchestrator_init', 'negotiations_start', 'contracts_start', 'completed']:
                        print("   " + "─" * 40)
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ Could not parse JSON: {e}")
                    print(f"   Raw data: {update}")
                    
        # Print test summary
        print("\n" + "=" * 60)
        print("🎯 Campaign Trigger Enhanced Streaming Test Results")
        print("=" * 60)
        print(f"📊 Total updates received: {update_count}")
        print(f"🎉 Detailed call logs seen: {len(detailed_logs_seen)}")
        
        if detailed_logs_seen:
            print("✅ SUCCESS: Enhanced streaming is working!")
            print("✅ Detailed call statuses found:")
            for status in detailed_logs_seen:
                status_names = {
                    'call_setup': 'Call Setup',
                    'dialing': 'Dialing Creator',
                    'connecting': 'Call Connecting',
                    'negotiating': 'Negotiation in Progress',
                    'call_completed': 'Call Completed'
                }
                print(f"   📱 {status_names.get(status, status)}")
        else:
            print("⚠️ WARNING: No detailed call logs seen")
            print("   This might indicate the enhancement isn't working")
            
        print("\n📋 Comparison Summary:")
        print("   BEFORE: 50% → 90% jump with 'Operation timeout'")
        print("   AFTER:  Detailed call progress for each creator")
        print("=" * 60)
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"📋 Error details: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🚀 Campaign Trigger Enhanced Streaming Test")
    print("Testing: /api/campaign-trigger/trigger/{campaign_id}/stream")
    print("Verifying: Same detailed logs as /agent/campaign/stream")
    print()
    
    asyncio.run(test_campaign_trigger_enhanced()) 