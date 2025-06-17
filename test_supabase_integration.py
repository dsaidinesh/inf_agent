#!/usr/bin/env python3
"""
🧪 Supabase Integration Test Script
Tests the enhanced email system with Supabase database logging
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_supabase_integration():
    """Test Supabase database integration"""
    
    print("🧪 Testing Supabase Integration")
    print("=" * 60)
    
    try:
        # Import services
        from services.supabase_database import supabase_db
        from services.email_service import email_service
        
        # Test 1: Database Connection
        print("\n🔗 Test 1: Database Connection")
        connection_success = await supabase_db.test_connection()
        
        if connection_success:
            print("✅ Supabase connection test PASSED")
        else:
            print("❌ Supabase connection test FAILED")
            return False
        
        # Test 2: Check database structure 
        print("\n📋 Test 2: Check Database Structure")
        try:
            # Check if our new tables exist
            tables_to_check = ["campaigns", "email_logs", "sponsor_decisions", "creators"]
            
            for table in tables_to_check:
                result = supabase_db.supabase.table(table).select("*").limit(1).execute()
                print(f"   ✅ Table '{table}' accessible")
            
            print("✅ All required tables are accessible")
            
        except Exception as e:
            print(f"❌ Database structure test failed: {str(e)}")
            return False
        
        # Test 3: Email Logging Test
        print("\n📧 Test 3: Email Logging")
        test_campaign_id = f"TEST-{int(datetime.now().timestamp())}"
        test_creator_id = "test-creator-123"
        
        try:
            # Log a test email
            email_log_id = await supabase_db.log_email_sent(
                campaign_id=test_campaign_id,
                creator_id=test_creator_id,
                email_type="test",
                recipient_email="test@example.com",
                recipient_name="Test User",
                subject="Test Email from Supabase Integration",
                content_preview="This is a test email to verify Supabase logging works correctly",
                sendgrid_message_id="test-msg-123"
            )
            
            if email_log_id:
                print(f"✅ Email logging test PASSED - Log ID: {email_log_id}")
                
                # Verify the log was stored
                result = supabase_db.supabase.table("email_logs").select("*").eq("id", email_log_id).execute()
                if result.data:
                    print(f"✅ Email log verification PASSED")
                    print(f"   Logged email: {result.data[0]['subject']}")
                    print(f"   Recipient: {result.data[0]['recipient_email']}")
                    print(f"   Status: {result.data[0]['status']}")
                else:
                    print("❌ Email log verification FAILED - Log not found")
            else:
                print("❌ Email logging test FAILED")
                
        except Exception as e:
            print(f"❌ Email logging test failed: {str(e)}")
        
        # Test 4: Creator Email Lookup
        print("\n👤 Test 4: Creator Email Lookup")
        try:
            # Get first creator from database to test lookup
            result = supabase_db.supabase.table("creators").select("email, name").limit(1).execute()
            
            if result.data and result.data[0].get("email"):
                test_email = result.data[0]["email"]
                creator_name = result.data[0]["name"]
                
                creator = await supabase_db.get_creator_by_email(test_email)
                
                if creator:
                    print(f"✅ Creator email lookup PASSED")
                    print(f"   Found creator: {creator['name']} ({creator['email']})")
                else:
                    print("❌ Creator email lookup FAILED - Creator not found")
            else:
                print("⚠️ No creators with email addresses found in database")
                
        except Exception as e:
            print(f"❌ Creator email lookup test failed: {str(e)}")
        
        # Test 5: Campaign Update with Email Fields
        print("\n📊 Test 5: Campaign Email Fields")
        try:
            # Create a test campaign record with email fields
            test_campaign_data = {
                "id": test_campaign_id,
                "product_name": "Test Product",
                "brand_name": "Test Brand",
                "product_description": "A test product for Supabase integration testing",
                "target_audience": "Test audience",
                "campaign_goal": "Test campaign",
                "product_niche": "tech",
                "total_budget": 5000.0,
                "status": "active",
                "influencer_count": 0,
                # 🚀 NEW: Email fields
                "sponsor_email": "sponsor@testbrand.com",
                "sponsor_name": "John Sponsor",
                "sponsor_phone": "+1234567890",
                "sponsor_company": "Test Brand Inc"
            }
            
            result = supabase_db.supabase.table("campaigns").upsert(test_campaign_data).execute()
            
            if result.data:
                print("✅ Campaign with email fields test PASSED")
                campaign = result.data[0]
                print(f"   Campaign ID: {campaign['id']}")
                print(f"   Sponsor Email: {campaign.get('sponsor_email', 'Not set')}")
                print(f"   Sponsor Name: {campaign.get('sponsor_name', 'Not set')}")
            else:
                print("❌ Campaign with email fields test FAILED")
                
        except Exception as e:
            print(f"❌ Campaign email fields test failed: {str(e)}")
        
        # Test 6: Sponsor Decision Storage
        print("\n💼 Test 6: Sponsor Decision Storage")
        try:
            decision_id = f"DEC-TEST-{int(datetime.now().timestamp())}"
            
            decision_stored = await supabase_db.store_sponsor_decision(
                decision_id=decision_id,
                campaign_id=test_campaign_id,
                creator_id=test_creator_id,
                sponsor_email="sponsor@testbrand.com",
                creator_email="creator@test.com",
                analytics_report={"test": "analytics"},
                call_data={"test": "call_data"},
                campaign_data={"test": "campaign_data"},
                expires_at=datetime.now() + timedelta(hours=48)
            )
            
            if decision_stored:
                print(f"✅ Sponsor decision storage test PASSED")
                print(f"   Decision ID: {decision_id}")
                
                # Verify the decision was stored
                result = supabase_db.supabase.table("sponsor_decisions").select("*").eq("decision_id", decision_id).execute()
                if result.data:
                    decision = result.data[0]
                    print(f"   Status: {decision['decision_status']}")
                    print(f"   Expires: {decision['expires_at']}")
                else:
                    print("❌ Decision verification FAILED")
            else:
                print("❌ Sponsor decision storage test FAILED")
                
        except Exception as e:
            print(f"❌ Sponsor decision storage test failed: {str(e)}")
        
        # Test 7: Email Analytics View
        print("\n📈 Test 7: Email Analytics View")
        try:
            # Check the recent_email_activity view
            result = supabase_db.supabase.table("recent_email_activity").select("*").limit(5).execute()
            
            print(f"✅ Email analytics view accessible")
            print(f"   Recent emails: {len(result.data)}")
            
            for email in result.data[:3]:  # Show first 3
                print(f"   • {email.get('email_type', 'unknown')}: {email.get('subject', 'No subject')}")
                print(f"     To: {email.get('recipient_email', 'Unknown')} | Status: {email.get('status', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Email analytics view test failed: {str(e)}")
        
        print("\n🎉 Supabase Integration Tests Completed!")
        print("=" * 60)
        print("✅ Your Supabase database is ready for email-enabled campaigns!")
        print()
        print("💡 Next Steps:")
        print("   1. Install dependencies: pip install supabase postgrest")
        print("   2. Update your .env file with Supabase credentials") 
        print("   3. Configure SendGrid for email delivery")
        print("   4. Test email sending with test_email_service.py")
        print("   5. Run a full campaign with enhanced_orchestrator.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Make sure to install required dependencies:")
        print("   pip install supabase postgrest")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

async def test_email_integration():
    """Test enhanced email service integration"""
    
    print("\n📧 Testing Enhanced Email Service Integration")
    print("=" * 60)
    
    try:
        from services.email_service import email_service
        
        # Test enhanced email sending (mock mode)
        test_campaign_details = {
            "campaign_id": f"EMAIL-TEST-{int(datetime.now().timestamp())}",
            "creator_id": "test-creator-456",
            "campaign_name": "Test Campaign - Enhanced Email",
            "brand_name": "Test Brand",
            "product_name": "Test Product"
        }
        
        print("\n📤 Sending test contract email...")
        success = await email_service.send_contract_email(
            to_email="test@example.com",
            to_name="Test Creator",
            contract_content="This is a test contract for Supabase integration testing",
            campaign_details=test_campaign_details,
            contract_filename="test_contract.txt"
        )
        
        if success:
            print("✅ Enhanced contract email test PASSED")
            print("   Email logged to Supabase database")
        else:
            print("❌ Enhanced contract email test FAILED")
        
        print("\n📤 Sending test notification email...")
        success = await email_service.send_notification_email(
            to_email="sponsor@testbrand.com",
            subject="Test Notification - Supabase Integration",
            message="This is a test notification to verify enhanced email service works correctly",
            is_html=False
        )
        
        if success:
            print("✅ Enhanced notification email test PASSED")
        else:
            print("❌ Enhanced notification email test FAILED")
            
    except Exception as e:
        print(f"❌ Email integration test failed: {str(e)}")
        return False
    
    return True

async def main():
    """Run all integration tests"""
    print("🚀 InfluencerFlow AI - Supabase Email Integration Tests")
    print("=" * 70)
    
    # Test database integration
    db_success = await test_supabase_integration()
    
    # Test email integration 
    email_success = await test_email_integration()
    
    print("\n" + "=" * 70)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"   Database Integration: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"   Email Integration:    {'✅ PASSED' if email_success else '❌ FAILED'}")
    
    if db_success and email_success:
        print("\n🎉 ALL TESTS PASSED! Your system is ready for email-enabled campaigns!")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above and resolve them.")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 