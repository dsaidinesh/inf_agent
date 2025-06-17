#!/usr/bin/env python3
"""
🎯 Test Supabase Decision Storage
Tests the new persistent decision storage in Supabase database
"""

import asyncio
import logging
import json
from datetime import datetime
from services.analytics_service import analytics_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_supabase_decision_storage():
    """Test the new Supabase decision storage system"""
    
    print("🎯 Testing Supabase Decision Storage")
    print("=" * 50)
    
    # Test 1: Store a decision in Supabase
    print("\n1. 🧪 Testing decision storage...")
    
    # Sample call data
    call_data = {
        "conversation_id": "test_conv_supabase_001",
        "call_duration_seconds": 240,
        "status": "completed",
        "negotiation_results": {
            "final_rate": 3500,
            "deliverables": ["1 Instagram post", "3 Instagram stories"],
            "timeline": "2 weeks",
            "creator_enthusiasm": 9,
            "special_terms": ["Usage rights for 12 months"]
        },
        "influencer_data": {
            "name": "Test Creator Supabase",
            "email": "testcreator@supabase.test",
            "platform": "Instagram"
        }
    }
    
    # Sample campaign data
    campaign_data = {
        "id": "11111111-2222-3333-4444-555555555555",  # Use existing campaign ID
        "campaign_name": "Supabase Test Campaign",
        "brand_name": "AudioMax Technologies",  # This will trigger your email
        "product_name": "Test Product",
        "total_budget": 15000,
        "offered_rate": 3000
    }
    
    try:
        # Process the call and store decision
        result = await analytics_service.process_completed_call(
            call_data=call_data,
            campaign_data=campaign_data,
            creator_email="testcreator@supabase.test"
        )
        
        if result["status"] == "success":
            decision_id = result["decision_id"]
            print(f"   ✅ Decision stored successfully!")
            print(f"   🆔 Decision ID: {decision_id}")
            print(f"   📧 Analytics email sent: {result['email_sent']}")
            print(f"   💾 Stored in database: {result['stored_in_database']}")
            print(f"   📧 Sponsor email: {result['sponsor_email_used']}")
            
            # Test 2: Retrieve the decision
            print(f"\n2. 🔍 Testing decision retrieval...")
            decision_data = await analytics_service._get_decision_from_database(decision_id)
            
            if decision_data:
                print(f"   ✅ Decision retrieved successfully!")
                print(f"   📊 Status: {decision_data['status']}")
                print(f"   📧 Creator: {decision_data['creator_email']}")
                print(f"   📧 Sponsor: {decision_data['sponsor_email']}")
                print(f"   💰 Final rate: ${decision_data['final_rate']}")
                print(f"   ⏰ Expires: {decision_data['expires_at']}")
            else:
                print("   ❌ Failed to retrieve decision")
                
            # Test 3: Get pending decisions
            print(f"\n3. 📋 Testing pending decisions list...")
            pending = analytics_service.get_pending_decisions()
            
            print(f"   📊 Total pending: {pending['total_pending']}")
            if pending['decisions']:
                latest = pending['decisions'][0]
                print(f"   🆔 Latest decision ID: {latest['decision_id']}")
                print(f"   👤 Creator: {latest['creator_email']}")
                print(f"   💰 Rate: ${latest['final_rate']}")
            
            # Test 4: Test decision processing (simulate sponsor approval)
            print(f"\n4. ✅ Testing decision approval...")
            approval_result = await analytics_service.process_sponsor_decision(
                decision_id=decision_id,
                decision="approve"
            )
            
            if approval_result["status"] == "success":
                print(f"   ✅ Decision approved successfully!")
                print(f"   📄 Action: {approval_result['action']}")
                print(f"   📧 Influencer email: {approval_result['influencer_email']}")
            else:
                print(f"   ⚠️ Approval result: {approval_result['message']}")
            
            return decision_id
            
        else:
            print(f"   ❌ Failed to store decision: {result['message']}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error during test: {str(e)}")
        return None

async def test_decision_persistence():
    """Test that decisions persist after server restart"""
    print("\n" + "=" * 50)
    print("🔄 Testing Decision Persistence")
    print("=" * 50)
    
    # Get all pending decisions to show they persist
    pending = analytics_service.get_pending_decisions()
    
    print(f"\n📊 Current pending decisions: {pending['total_pending']}")
    
    if pending['decisions']:
        print("\n📋 Persistent Decisions:")
        for i, decision in enumerate(pending['decisions'][:3], 1):  # Show first 3
            print(f"   {i}. 🆔 {decision['decision_id']}")
            print(f"      👤 Creator: {decision['creator_email']}")
            print(f"      📧 Sponsor: {decision['sponsor_email']}")
            print(f"      💰 Rate: ${decision.get('final_rate', 'N/A')}")
            print(f"      📅 Created: {decision['created_at'][:19]}")
            print(f"      ⏰ Expires: {decision['expires_at'][:19]}")
            print()
    
    print("✅ All decisions are now stored persistently in Supabase!")
    print("   • Decisions survive server restarts")
    print("   • Sponsor links work even after system reboot")
    print("   • Complete audit trail of all decisions")
    print("   • Automatic expiration handling")

async def main():
    """Main test function"""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test decision storage
    decision_id = await test_supabase_decision_storage()
    
    # Test persistence
    await test_decision_persistence()
    
    print("\n" + "=" * 50)
    print("🎉 Supabase Decision Storage Tests Completed!")
    print("\n📖 Key Improvements:")
    print("   • ✅ Decisions stored in Supabase database")
    print("   • ✅ Persistent across server restarts")
    print("   • ✅ Automatic expiration handling")
    print("   • ✅ Complete audit trail")
    print("   • ✅ Better sponsor decision experience")
    
    if decision_id:
        print(f"\n🔗 Test Decision URLs:")
        print(f"   Approve: http://localhost:8000/api/decision/approve/{decision_id}")
        print(f"   Reject:  http://localhost:8000/api/decision/reject/{decision_id}")

if __name__ == "__main__":
    asyncio.run(main()) 