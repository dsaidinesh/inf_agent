#!/usr/bin/env python3
"""
Enhanced Streaming Logs Test - Shows detailed call progress
This demonstrates the improved streaming that shows ALL the steps between 50% and 90%
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append('.')

from models.campaign import CampaignData
from api.streaming_logs import enhanced_campaign_with_streaming

async def test_enhanced_streaming():
    """Test the enhanced streaming with detailed call logs"""
    
    print("🚀 Testing Enhanced Streaming Logs")
    print("=" * 50)
    
    # Create test campaign data
    campaign_data = CampaignData(
        id="test_enhanced_streaming",
        brand_name="TechFlow",
        product_name="AI Productivity Suite",
        product_description="Revolutionary AI tools for content creators",
        target_audience="Tech-savvy content creators aged 25-40",
        campaign_goal="Increase brand awareness and drive product trials",
        total_budget=15000,
        product_niche="Technology/Productivity"
    )
    
    task_id = f"enhanced_test_{int(datetime.now().timestamp())}"
    
    print(f"📊 Campaign: {campaign_data.brand_name} - {campaign_data.product_name}")
    print(f"💰 Budget: ${campaign_data.total_budget:,}")
    print(f"🎯 Target: {campaign_data.target_audience}")
    print(f"📋 Task ID: {task_id}")
    print("\n🔄 Starting Enhanced Streaming...\n")
    
    try:
        # Stream the campaign execution
        async for update in enhanced_campaign_with_streaming(campaign_data, task_id):
            if update.startswith("data: "):
                try:
                    # Parse the SSE data
                    data = json.loads(update[6:])  # Remove "data: " prefix
                    
                    # Format timestamp
                    timestamp = datetime.fromisoformat(data['timestamp']).strftime("%H:%M:%S")
                    
                    # Color-code different statuses
                    status = data['status']
                    message = data['message']
                    progress = data.get('progress', 'N/A')
                    
                    # Status emojis and colors
                    status_colors = {
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
                        'call_delayed': '⏱️',
                        'call_failed': '❌',
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
                    if status in ['discovery', 'strategy', 'negotiations_start', 'contracts_start', 'completed']:
                        print("   " + "─" * 40)
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse: {update}")
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    print("\n🏁 Enhanced Streaming Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    print("Enhanced Streaming Logs Demo")
    print("This shows detailed call progress instead of jumping from 50% to 90%")
    print("\n" + "=" * 60)
    
    asyncio.run(test_enhanced_streaming()) 