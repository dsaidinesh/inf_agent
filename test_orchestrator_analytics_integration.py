#!/usr/bin/env python3
"""
🧪 Test Orchestrator Analytics Integration
Verify that the orchestrator now sends analytics to sponsor for approval BEFORE contracts
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_orchestrator_analytics_integration():
    """
    🧪 Test that orchestrator uses new analytics workflow
    """
    print("🧪 TESTING ORCHESTRATOR → ANALYTICS INTEGRATION")
    print("="*60)
    
    # Import services
    from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
    from models.campaign import CampaignData, NegotiationState, Creator, Platform, Availability, CreatorTier
    from services.analytics_service import analytics_service
    
    # Create test campaign with sponsor email
    campaign_data = CampaignData(
        id="camp_test_123",
        product_name="Test Product",
        brand_name="Test Brand",
        product_description="A test product for integration testing",
        target_audience="Tech enthusiasts",
        campaign_goal="Product awareness",
        product_niche="tech",
        total_budget=10000.0,
        sponsor_email="sponsor@testbrand.com",  # 🚀 Include sponsor email
        sponsor_name="Test Sponsor"
    )
    
    # Create test creator
    test_creator = Creator(
        id="creator_test_456",
        name="TestCreator_Analytics",
        email="test.creator@example.com",
        platform=Platform.YOUTUBE,
        followers=250000,
        niche="tech",
        typical_rate=3000.0,
        engagement_rate=4.5,
        average_views=50000,
        last_campaign_date="2024-01-01",
        availability=Availability.EXCELLENT,
        location="US",
        phone_number="+1-555-123-4567",
        languages=["English"],
        specialties=["Tech reviews", "Unboxing"]
    )
    
    # Create mock negotiation result
    test_negotiation = NegotiationState(
        creator_id="creator_test_456",
        campaign_id="camp_test_123",
        conversation_id="conv_test_789",
        call_duration_seconds=420,
        final_rate=3500.0,
        negotiated_terms={
            "deliverables": ["YouTube review video", "Instagram post"],
            "timeline": "2 weeks",
            "initial_offer": 3000.0,
            "enthusiasm": 9,
            "special_terms": ["Creative control retained"]
        }
    )
    test_negotiation.status = "success"  # Set as successful
    
    # Create test contract
    test_contract = {
        "contract_id": "contract_test_abc",
        "campaign_id": "camp_test_123",
        "creator_id": "creator_test_456",
        "compensation": 3500.0,
        "terms": test_negotiation.negotiated_terms,
        "status": "draft",
        "created_at": datetime.now().isoformat()
    }
    
    print("📊 Test Setup:")
    print(f"   Campaign: {campaign_data.brand_name} - {campaign_data.product_name}")
    print(f"   Creator: {test_creator.name} ({test_creator.email})")
    print(f"   Final Rate: ${test_negotiation.final_rate:,.2f}")
    print(f"   Sponsor Email: {campaign_data.sponsor_email}")
    
    # Initialize orchestrator
    orchestrator = EnhancedCampaignOrchestrator()
    
    # Mock the current state with our test creator
    from models.campaign import CreatorMatch, CampaignOrchestrationState
    creator_match = CreatorMatch(
        creator=test_creator,
        similarity_score=0.95,
        estimated_rate=3500.0,
        match_reasons=["Tech niche match", "High engagement"]
    )
    
    mock_state = CampaignOrchestrationState(
        task_id="test_123",
        campaign_id="camp_test_123",  # Required field
        campaign_data=campaign_data,
        discovered_influencers=[creator_match]
    )
    orchestrator._current_state = mock_state
    
    print("\n🚀 Testing Analytics Workflow Integration...")
    
    # Test the new _send_contract_email method (which now sends analytics)
    await orchestrator._send_contract_email(
        negotiation=test_negotiation,
        campaign_data=campaign_data,
        contract=test_contract
    )
    
    print(f"\n📋 Contract Status After Test: {test_contract['status']}")
    
    if test_contract["status"] == "pending_sponsor_approval":
        decision_id = test_contract.get("decision_id")
        sponsor_email = test_contract.get("sponsor_email")
        
        print(f"✅ SUCCESS: Analytics workflow integrated!")
        print(f"🔑 Decision ID: {decision_id}")
        print(f"📧 Sponsor Email: {sponsor_email}")
        print(f"⏳ Contract is waiting for sponsor approval")
        
        # Check pending decisions
        pending = analytics_service.get_pending_decisions()
        print(f"\n📋 Pending Decisions: {pending['total_pending']}")
        
        if pending["total_pending"] > 0:
            for decision in pending["decisions"]:
                if decision["decision_id"] == decision_id:
                    print(f"✅ Found our decision in pending list:")
                    print(f"   Campaign: {decision['campaign_name']}")
                    print(f"   Creator: {decision['creator_email']}")
                    print(f"   Sponsor: {decision['sponsor_email']}")
                    break
        
        print(f"\n🔗 Decision URLs:")
        print(f"   Approve: http://localhost:8000/api/decision/approve/{decision_id}")
        print(f"   Reject:  http://localhost:8000/api/decision/reject/{decision_id}")
        
        return True
        
    elif test_contract["status"] in ["analytics_failed", "workflow_error"]:
        print(f"❌ FAILED: Analytics workflow had an error")
        print(f"   Status: {test_contract['status']}")
        return False
        
    else:
        print(f"❌ UNEXPECTED: Contract status is {test_contract['status']}")
        print(f"   Expected: pending_sponsor_approval")
        return False

async def test_missing_sponsor_email():
    """
    🧪 Test orchestrator with missing sponsor email (should use fallback)
    """
    print("\n" + "="*60)
    print("🧪 TESTING MISSING SPONSOR EMAIL FALLBACK")
    
    from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
    from models.campaign import CampaignData, NegotiationState, Creator, Platform, Availability
    
    # Create campaign WITHOUT sponsor email
    campaign_data = CampaignData(
        id="camp_no_email_456",
        product_name="Mystery Product",
        brand_name="Unknown Brand Co",  # Not in lookup table
        product_description="A mystery product",
        target_audience="General audience",
        campaign_goal="Awareness",
        product_niche="general",
        total_budget=5000.0
        # No sponsor_email provided
    )
    
    test_creator = Creator(
        id="creator_mystery_789",
        name="MysteryCreator",
        email="mystery.creator@example.com",
        platform=Platform.INSTAGRAM,
        followers=100000,
        niche="lifestyle",
        typical_rate=2000.0,
        engagement_rate=3.2,
        average_views=25000,
        last_campaign_date="2024-01-01",
        availability=Availability.GOOD,
        location="US",
        phone_number="+1-555-987-6543",
        languages=["English"],
        specialties=["Lifestyle content"]
    )
    
    test_negotiation = NegotiationState(
        creator_id="creator_mystery_789",
        campaign_id="camp_no_email_456",
        conversation_id="conv_mystery_012",
        call_duration_seconds=240,
        final_rate=2200.0,
        negotiated_terms={
            "deliverables": ["Instagram post"],
            "timeline": "1 week",
            "initial_offer": 2000.0,
            "enthusiasm": 7
        }
    )
    test_negotiation.status = "success"
    
    test_contract = {
        "contract_id": "contract_mystery_def",
        "campaign_id": "camp_no_email_456",
        "creator_id": "creator_mystery_789",
        "compensation": 2200.0,
        "status": "draft"
    }
    
    print(f"📊 Test Setup (No Sponsor Email):")
    print(f"   Campaign: {campaign_data.brand_name}")
    print(f"   Creator: {test_creator.name}")
    print(f"   Sponsor Email: None (should generate fallback)")
    
    orchestrator = EnhancedCampaignOrchestrator()
    
    # Mock state
    from models.campaign import CreatorMatch, CampaignOrchestrationState
    creator_match = CreatorMatch(
        creator=test_creator,
        similarity_score=0.8,
        estimated_rate=2200.0
    )
    
    mock_state = CampaignOrchestrationState(
        task_id="test_456",
        campaign_id="camp_no_email_456",  # Required field
        campaign_data=campaign_data,
        discovered_influencers=[creator_match]
    )
    orchestrator._current_state = mock_state
    
    print("\n🎭 Testing Fallback Email Generation...")
    
    await orchestrator._send_contract_email(
        negotiation=test_negotiation,
        campaign_data=campaign_data,
        contract=test_contract
    )
    
    print(f"\n📋 Contract Status: {test_contract['status']}")
    
    if test_contract["status"] == "pending_sponsor_approval":
        sponsor_email = test_contract.get("sponsor_email")
        print(f"✅ SUCCESS: Fallback email generated!")
        print(f"📧 Generated Sponsor Email: {sponsor_email}")
        print(f"💡 Should be something like: sponsor@unknownbrandco.com")
        return True
    else:
        print(f"❌ FAILED: Expected pending_sponsor_approval, got {test_contract['status']}")
        return False

def main():
    """
    🎯 Main test runner
    """
    print("🧪 ORCHESTRATOR ANALYTICS INTEGRATION TESTS")
    print("="*60)
    print("🎯 Verifying that orchestrator now uses analytics workflow")
    print("📧 Instead of sending contracts directly to influencers")
    print("✅ Sponsors must approve BEFORE contracts are sent")
    
    async def run_tests():
        test1_result = await test_orchestrator_analytics_integration()
        test2_result = await test_missing_sponsor_email()
        
        print("\n" + "="*60)
        print("🎉 TEST RESULTS SUMMARY")
        print(f"✅ Analytics Integration: {'PASS' if test1_result else 'FAIL'}")
        print(f"🎭 Fallback Email Generation: {'PASS' if test2_result else 'FAIL'}")
        
        if test1_result and test2_result:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Orchestrator now properly uses analytics workflow")
            print("📧 Sponsors receive analytics for approval BEFORE contracts")
            print("🔗 Decision URLs are generated for sponsor actions")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("🛠️ Check the orchestrator integration")
    
    asyncio.run(run_tests())

if __name__ == "__main__":
    main() 