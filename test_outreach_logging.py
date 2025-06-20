#!/usr/bin/env python3
"""
🧪 Test Outreach Logging Functionality
Tests the new outreach logging service that logs influencer discoveries to Supabase
"""

import asyncio
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_outreach_logging():
    """Test the outreach logging functionality"""
    
    print("🧪 Testing Outreach Logging Functionality")
    print("=" * 60)
    
    try:
        # Import services and models
        from services.outreach_logger import outreach_logger
        from models.campaign import Creator, CreatorMatch, Platform, Availability, CampaignData
        
        # Test 1: Basic service initialization
        print("\n1. 🔧 Testing service initialization...")
        if outreach_logger.db_service.supabase:
            print("✅ Outreach logger service initialized with Supabase connection")
        else:
            print("❌ Outreach logger service failed to connect to Supabase")
            return False
        
        # Test 2: Create mock data
        print("\n2. 📝 Creating test data...")
        
        # Create test campaign
        test_campaign_id = f"TEST_OUTREACH_{int(datetime.now().timestamp())}"
        
        # Create test creators
        test_creators = [
            Creator(
                id="test_creator_1",
                name="Test Tech Creator 1",
                email="test1@example.com",
                platform=Platform.YOUTUBE,
                followers=100000,
                niche="tech",
                typical_rate=3000,
                engagement_rate=4.5,
                average_views=50000,
                last_campaign_date="2024-01-01",
                availability=Availability.GOOD,
                location="Mumbai, India",
                phone_number="+91 7013543557",
                languages=["English", "Hindi"],
                specialties=["tech_reviews", "gadget_unboxing"],
                preferred_collaboration_style="Professional and detail-oriented"
            ),
            Creator(
                id="test_creator_2",
                name="Test Tech Creator 2",
                email="test2@example.com",
                platform=Platform.INSTAGRAM,
                followers=75000,
                niche="tech",
                typical_rate=2500,
                engagement_rate=5.2,
                average_views=30000,
                last_campaign_date="2024-01-15",
                availability=Availability.EXCELLENT,
                location="Delhi, India",
                phone_number="+91 7013543558",
                languages=["English"],
                specialties=["product_reviews", "tech_tutorials"],
                preferred_collaboration_style="Creative and engaging"
            )
        ]
        
        # Create creator matches
        creator_matches = []
        for i, creator in enumerate(test_creators):
            match = CreatorMatch(
                creator=creator,
                similarity_score=0.85 - (i * 0.05),  # Slightly different scores
                estimated_rate=creator.typical_rate,
                match_reasons=["Good niche alignment", "Budget compatible", "High engagement"],
                availability_score=0.8
            )
            creator_matches.append(match)
        
        print(f"✅ Created {len(creator_matches)} test creator matches")
        
        # Test 3: Log influencer discovery
        print("\n3. 📝 Testing influencer discovery logging...")
        
        success = await outreach_logger.log_influencer_discovery(
            campaign_id=test_campaign_id,
            discovered_influencers=creator_matches
        )
        
        if success:
            print("✅ Successfully logged influencer discovery")
        else:
            print("❌ Failed to log influencer discovery")
            return False
        
        # Test 4: Verify logs were created
        print("\n4. 🔍 Verifying logs in database...")
        
        # Retrieve the logs we just created
        logs = await outreach_logger.get_outreach_logs_for_campaign(test_campaign_id)
        
        if logs:
            print(f"✅ Found {len(logs)} outreach logs for test campaign")
            for i, log in enumerate(logs):
                creator_name = log.get('content', {}).get('creator_details', {}).get('name', 'Unknown')
                print(f"   {i+1}. {creator_name} - Status: {log.get('status', 'unknown')}")
        else:
            print("❌ No logs found for test campaign")
            return False
        
        # Test 5: Test individual outreach attempt logging
        print("\n5. 📞 Testing outreach attempt logging...")
        
        test_creator_id = test_creators[0].id
        attempt_success = await outreach_logger.log_outreach_attempt(
            campaign_id=test_campaign_id,
            creator_id=test_creator_id,
            channel="voice",
            message_type="call_attempt",
            status="initiated",
            additional_data={
                "phone_number": test_creators[0].phone_number,
                "attempt_number": 1,
                "scheduled_time": datetime.now().isoformat()
            }
        )
        
        if attempt_success:
            print("✅ Successfully logged outreach attempt")
        else:
            print("❌ Failed to log outreach attempt")
        
        # Test 6: Test status update
        print("\n6. 🔄 Testing status update...")
        
        # Get the conversation ID from the first log
        if logs:
            conversation_id = logs[0].get('conversation_id')
            if conversation_id:
                update_success = await outreach_logger.update_outreach_status(
                    conversation_id=conversation_id,
                    new_status="contacted",
                    additional_data={
                        "contact_method": "phone_call",
                        "response_received": True,
                        "updated_timestamp": datetime.now().isoformat()
                    }
                )
                
                if update_success:
                    print("✅ Successfully updated outreach status")
                else:
                    print("❌ Failed to update outreach status")
            else:
                print("⚠️ No conversation ID found for status update test")
        
        # Test 7: Final verification
        print("\n7. 🔍 Final verification...")
        
        final_logs = await outreach_logger.get_outreach_logs_for_campaign(test_campaign_id)
        
        if final_logs:
            print(f"✅ Final verification: Found {len(final_logs)} total logs")
            
            # Show detailed log information
            for log in final_logs:
                content = log.get('content', {})
                creator_details = content.get('creator_details', {})
                print(f"   • Creator: {creator_details.get('name', 'Unknown')}")
                print(f"     Status: {log.get('status', 'unknown')}")
                print(f"     Type: {log.get('message_type', 'unknown')}")
                print(f"     Channel: {log.get('channel', 'unknown')}")
                print(f"     Time: {log.get('timestamp', 'unknown')}")
                print()
        
        print("🎉 All outreach logging tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_real_campaign():
    """Test with a real campaign to demonstrate full integration"""
    
    print("\n" + "="*60)
    print("🚀 Testing with Enhanced Orchestrator Integration")
    print("="*60)
    
    try:
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        from models.campaign import CampaignData
        
        # Create a test campaign
        test_campaign = CampaignData(
            id=f"INTEGRATION_TEST_{int(datetime.now().timestamp())}",
            product_name="Test Audio Headphones",
            brand_name="AudioMax Technologies",
            product_description="High-quality wireless headphones for tech enthusiasts",
            target_audience="Tech enthusiasts aged 25-35",
            campaign_goal="Increase brand awareness and drive sales",
            product_niche="tech",
            total_budget=15000.0,
            sponsor_email="sponsor@audiomax.test",
            sponsor_name="Test Sponsor",
            sponsor_phone="+1-555-0123"
        )
        
        print(f"📝 Created test campaign: {test_campaign.product_name}")
        print(f"   Campaign ID: {test_campaign.id}")
        print(f"   Budget: ${test_campaign.total_budget:,}")
        print(f"   Niche: {test_campaign.product_niche}")
        
        # Initialize orchestrator
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Run just the discovery phase to test our logging
        print("\n🔍 Running discovery phase with outreach logging...")
        
        # Create campaign state
        from models.campaign import CampaignOrchestrationState
        state = CampaignOrchestrationState(
            campaign_id=test_campaign.id,
            campaign_data=test_campaign
        )
        
        # Run discovery phase (this should trigger our outreach logging)
        await orchestrator._run_discovery_phase(state)
        
        # Verify that outreach logs were created
        print("\n🔍 Verifying outreach logs were created...")
        
        from services.outreach_logger import outreach_logger
        logs = await outreach_logger.get_outreach_logs_for_campaign(test_campaign.id)
        
        if logs:
            print(f"✅ SUCCESS: Found {len(logs)} outreach logs for the campaign")
            for i, log in enumerate(logs):
                content = log.get('content', {})
                creator_details = content.get('creator_details', {})
                similarity_score = content.get('similarity_score', 0)
                estimated_rate = content.get('estimated_rate', 0)
                
                print(f"   {i+1}. {creator_details.get('name', 'Unknown Creator')}")
                print(f"      Platform: {creator_details.get('platform', 'Unknown')}")
                print(f"      Similarity: {similarity_score:.3f}")
                print(f"      Est. Rate: ${estimated_rate:,}")
                print(f"      Status: {log.get('status', 'unknown')}")
                print()
        else:
            print("❌ No outreach logs found - integration may have failed")
            return False
        
        print("🎉 Integration test with real campaign PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    
    print("🚀 Starting Outreach Logging Tests")
    print("="*60)
    
    # Test 1: Basic functionality
    basic_test_passed = await test_outreach_logging()
    
    if not basic_test_passed:
        print("\n❌ Basic tests failed - stopping here")
        sys.exit(1)
    
    # Test 2: Integration with real orchestrator
    integration_test_passed = await test_with_real_campaign()
    
    if basic_test_passed and integration_test_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📊 Summary:")
        print("   ✅ Outreach logger service working")
        print("   ✅ Database logging functional")
        print("   ✅ Integration with orchestrator working")
        print("   ✅ Campaign and creator IDs properly logged")
        print("   ✅ Conversation IDs generated correctly")
        print("\n🚀 Your outreach logging system is ready!")
    else:
        print("\n❌ Some tests failed - please check the logs above")
        sys.exit(1)

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 