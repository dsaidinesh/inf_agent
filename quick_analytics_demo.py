#!/usr/bin/env python3
"""
🚀 QUICK ANALYTICS DEMO
Simple demonstration of the post-call analytics workflow

This shows you exactly how to integrate the analytics workflow into your system.
"""

import requests
import json
from datetime import datetime
import asyncio
from services.analytics_service import analytics_service

async def demo_analytics_workflow():
    """
    🚀 Demo the complete analytics workflow with sponsor email auto-detection
    """
    print("🎯 SPONSOR EMAIL AUTO-DETECTION DEMO")
    print("="*60)
    
    # Test data with campaign that includes sponsor email
    call_completion_data = {
        "call_data": {
            "conversation_id": "conv_demo_12345",
            "call_duration_seconds": 180,
            "status": "completed",
            "influencer_data": {
                "name": "TechReviewer_Sarah",
                "platform": "YouTube"
            },
            "negotiation_results": {
                "final_rate": 2500,
                "deliverables": ["1 Instagram post", "3 Instagram stories"],
                "timeline": "2 weeks",
                "creator_enthusiasm": 8,
                "special_terms": ["Usage rights for 6 months"]
            }
        },
        "campaign_data": {
            "campaign_name": "TechCorp Product Launch",
            "brand_name": "TechCorp",  # This will be used for lookup
            "product_name": "Smartphone X1",
            "offered_rate": 2000,
            "total_budget": 10000,
            "sponsor_email": "sponsor@techcorp.com"  # Included in campaign data
        },
        # "sponsor_email": "sponsor@techcorp.com",  # ← NOT PROVIDED - will auto-detect
        "creator_email": "sarah.tech@example.com"
    }
    
    print("📊 Testing AUTO-DETECTION from campaign_data...")
    print(f"   Brand: {call_completion_data['campaign_data']['brand_name']}")
    print(f"   Sponsor email in campaign_data: {call_completion_data['campaign_data']['sponsor_email']}")
    print(f"   No sponsor_email provided separately - should auto-detect!")
    
    # Process the completed call
    result = await analytics_service.process_completed_call(
        call_data=call_completion_data["call_data"],
        campaign_data=call_completion_data["campaign_data"],
        # sponsor_email=None,  # Not provided - will auto-detect
        creator_email=call_completion_data["creator_email"]
    )
    
    print("\n📊 ANALYTICS PROCESSING RESULT:")
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        decision_id = result["decision_id"]
        sponsor_email_used = result.get("sponsor_email_used")
        
        print(f"\n✅ Analytics sent successfully!")
        print(f"🔑 Decision ID: {decision_id}")
        print(f"📧 Sponsor email auto-detected: {sponsor_email_used}")
        print(f"👤 Creator email verified: {call_completion_data['creator_email']}")
        
        # Show pending decisions
        pending = analytics_service.get_pending_decisions()
        print(f"\n📋 Pending Decisions: {pending['total_pending']}")
        
        for decision in pending["decisions"]:
            print(f"   • {decision['decision_id']}: {decision['campaign_name']}")
            print(f"     Creator: {decision['creator_email']}")
            print(f"     Sponsor: {decision['sponsor_email']}")
        
        print(f"\n🔗 Decision URLs:")
        print(f"   Approve: /api/decision/approve/{decision_id}")
        print(f"   Reject:  /api/decision/reject/{decision_id}")
        
        return decision_id
    else:
        print(f"❌ Analytics processing failed: {result['message']}")
        return None

async def demo_brand_lookup():
    """
    🔍 Demo sponsor email lookup by brand name
    """
    print("\n" + "="*60)
    print("🔍 Testing BRAND NAME LOOKUP...")
    
    call_completion_data = {
        "call_data": {
            "conversation_id": "conv_lookup_456",
            "call_duration_seconds": 240,
            "status": "completed",
            "influencer_data": {
                "name": "TechInfluencer",
                "platform": "TikTok"
            },
            "negotiation_results": {
                "final_rate": 3000,
                "deliverables": ["TikTok video"],
                "timeline": "1 week"
            }
        },
        "campaign_data": {
            "campaign_name": "Audio Equipment Campaign",
            "brand_name": "TechPro Audio",  # This should match our lookup table
            "product_name": "Wireless Headphones",
            "offered_rate": 2800,
            "total_budget": 15000
            # No sponsor_email in campaign_data
        },
        "creator_email": "sarah.tech@example.com"
    }
    
    print(f"📊 Testing LOOKUP for brand: {call_completion_data['campaign_data']['brand_name']}")
    print(f"   No sponsor_email anywhere - should lookup by brand name!")
    
    result = await analytics_service.process_completed_call(
        call_data=call_completion_data["call_data"],
        campaign_data=call_completion_data["campaign_data"],
        creator_email=call_completion_data["creator_email"]
    )
    
    print("\n📊 LOOKUP RESULT:")
    if result["status"] == "success":
        sponsor_email_used = result.get("sponsor_email_used")
        print(f"✅ Found sponsor email via lookup: {sponsor_email_used}")
        print(f"🔑 Decision ID: {result['decision_id']}")
    else:
        print(f"❌ Lookup failed: {result['message']}")

async def demo_fallback_generation():
    """
    🎭 Demo fallback email generation
    """
    print("\n" + "="*60)
    print("🎭 Testing FALLBACK GENERATION...")
    
    call_completion_data = {
        "call_data": {
            "conversation_id": "conv_fallback_789",
            "call_duration_seconds": 300,
            "status": "completed",
            "influencer_data": {
                "name": "UnknownInfluencer",
                "platform": "Instagram"
            },
            "negotiation_results": {
                "final_rate": 1800,
                "deliverables": ["Instagram post"],
                "timeline": "5 days"
            }
        },
        "campaign_data": {
            "campaign_name": "Unknown Brand Campaign",
            "brand_name": "Mystery Brand Co",  # Not in lookup table
            "product_name": "Mystery Product",
            "offered_rate": 2000,
            "total_budget": 8000
            # No sponsor_email anywhere
        },
        "creator_email": "sarah.tech@example.com"
    }
    
    print(f"📊 Testing FALLBACK for brand: {call_completion_data['campaign_data']['brand_name']}")
    print(f"   Brand not in lookup table - should generate fallback email!")
    
    result = await analytics_service.process_completed_call(
        call_data=call_completion_data["call_data"],
        campaign_data=call_completion_data["campaign_data"],
        creator_email=call_completion_data["creator_email"]
    )
    
    print("\n📊 FALLBACK RESULT:")
    if result["status"] == "success":
        sponsor_email_used = result.get("sponsor_email_used")
        print(f"⚠️ Generated fallback email: {sponsor_email_used}")
        print(f"🔑 Decision ID: {result['decision_id']}")
        print(f"💡 TIP: Add this brand to the lookup table for better results!")
    else:
        print(f"❌ Fallback failed: {result['message']}")

async def demo_endpoint_usage():
    """
    📡 Show updated endpoint usage examples
    """
    print("\n" + "="*60)
    print("📡 UPDATED ENDPOINT USAGE EXAMPLES")
    
    examples = [
        {
            "name": "✅ Best Practice: Sponsor email in campaign_data",
            "data": {
                "call_data": {"conversation_id": "conv_123"},
                "campaign_data": {
                    "brand_name": "TechCorp",
                    "sponsor_email": "sponsor@techcorp.com"  # Best practice
                },
                "creator_email": "creator@verified.com"
                # No separate sponsor_email needed
            }
        },
        {
            "name": "🔍 Lookup: No sponsor email, brand in lookup table",
            "data": {
                "call_data": {"conversation_id": "conv_456"},
                "campaign_data": {
                    "brand_name": "TechPro Audio"  # Will be found in lookup
                },
                "creator_email": "creator@verified.com"
            }
        },
        {
            "name": "🎭 Fallback: Unknown brand, auto-generate email",
            "data": {
                "call_data": {"conversation_id": "conv_789"},
                "campaign_data": {
                    "brand_name": "New Startup Brand"  # Will generate fallback
                },
                "creator_email": "creator@verified.com"
            }
        },
        {
            "name": "🎯 Override: Explicit sponsor_email (legacy)",
            "data": {
                "call_data": {"conversation_id": "conv_999"},
                "campaign_data": {"brand_name": "Any Brand"},
                "sponsor_email": "explicit@sponsor.com",  # Explicit override
                "creator_email": "creator@verified.com"
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print("   Request:")
        print(f"   POST /api/webhook/process-completed-call")
        print(f"   {json.dumps(example['data'], indent=6)}")
    
    print(f"\n📝 KEY CHANGES:")
    print("✅ sponsor_email is now OPTIONAL")
    print("✅ Auto-detects from campaign_data['sponsor_email']")
    print("✅ Lookups by brand name from database")
    print("✅ Generates fallback emails as last resort")
    print("✅ Shows which email was used in response")

def main():
    """Main demo function"""
    
    print("🚀 Starting Quick Analytics Demo...")
    print("Make sure your server is running on http://localhost:8000\n")
    
    # Run the demo
    decision_id = demo_analytics_workflow()
    
    if decision_id:
        demo_sponsor_decision(decision_id)
    
    show_integration_guide()
    
    print(f"\n🎉 Demo completed!")
    print(f"📧 Check your email service logs to see the analytics email")
    print(f"🧪 Run the full test with: python test_analytics_workflow.py")

if __name__ == "__main__":
    print("🎯 ANALYTICS WORKFLOW DEMO - WITH CREATOR EMAIL VERIFICATION")
    print("="*70)
    
    # Run the demo
    asyncio.run(demo_analytics_workflow())
    asyncio.run(demo_brand_lookup())
    asyncio.run(demo_fallback_generation())
    asyncio.run(demo_endpoint_usage())
    
    print("\n✅ Demo completed!")
    print("📝 The endpoint now requires and verifies creator email addresses!")
    print("🔧 Next steps: Test the /api/webhook/process-completed-call endpoint") 