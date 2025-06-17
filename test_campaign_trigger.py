# test_campaign_trigger.py
"""
🎯 Test Campaign Trigger Endpoints
This script demonstrates how to use the new campaign trigger endpoints
that fetch creator data from Supabase and trigger AI calls.
"""

import asyncio
import requests
import time
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CampaignTriggerTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    async def run_full_test(self):
        """Run a complete test of all campaign trigger endpoints"""
        print("🚀 Starting Campaign Trigger API Testing...")
        print("=" * 60)
        
        try:
            # 1. Test system health
            await self.test_system_health()
            
            # 2. List available campaigns
            campaigns = await self.test_list_campaigns()
            
            if not campaigns:
                print("❌ No campaigns found - run setup_sample_data.py first")
                return False
            
            # 3. Pick a campaign to test
            test_campaign_id = campaigns[0]["id"]
            print(f"\n🎯 Testing with campaign: {test_campaign_id}")
            
            # 4. Discover creators for the campaign
            await self.test_discover_creators(test_campaign_id)
            
            # 5. Trigger AI calls for the campaign
            task_id = await self.test_trigger_calls(test_campaign_id)
            
            if task_id:
                # 6. Monitor the campaign progress
                await self.test_monitor_progress(task_id)
            
            print("\n✅ Campaign trigger testing completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Campaign trigger testing failed: {str(e)}")
            return False
    
    async def test_system_health(self):
        """Test system health and readiness"""
        print("1. 🏥 Testing System Health...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ System Status: {health_data.get('status', 'unknown')}")
                
                services = health_data.get('services', {})
                for service_name, service_info in services.items():
                    status = service_info.get('status', 'unknown')
                    print(f"   📊 {service_name}: {status}")
                
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check error: {str(e)}")
            return False
    
    async def test_list_campaigns(self):
        """Test listing available campaigns"""
        print("\n2. 📋 Testing Campaign Listing...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/campaign-trigger/campaigns")
            
            if response.status_code == 200:
                data = response.json()
                campaigns = data.get("campaigns", [])
                
                print(f"   ✅ Found {len(campaigns)} campaigns")
                
                for campaign in campaigns[:3]:  # Show first 3
                    print(f"   📋 {campaign['id']}: {campaign['product_name']} ({campaign['brand_name']})")
                    print(f"       Niche: {campaign['product_niche']}, Budget: ${campaign['total_budget']:,.0f}")
                
                return campaigns
            else:
                print(f"   ❌ List campaigns failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ List campaigns error: {str(e)}")
            return []
    
    async def test_discover_creators(self, campaign_id: str):
        """Test discovering creators for a campaign"""
        print(f"\n3. 🔍 Testing Creator Discovery for {campaign_id}...")
        
        try:
            params = {
                "max_results": 5,
                "min_followers": 100000,
                "max_rate": 10000
            }
            
            response = self.session.get(
                f"{self.base_url}/api/campaign-trigger/discover/{campaign_id}",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                creators = data.get("creators", [])
                
                print(f"   ✅ Found {len(creators)} matching creators")
                print(f"   🎯 Campaign: {data.get('campaign_name', 'Unknown')}")
                print(f"   💰 Budget: ${data.get('total_budget', 0):,.0f}")
                print(f"   🎪 Niche: {data.get('product_niche', 'Unknown')}")
                
                for creator in creators[:3]:  # Show first 3
                    print(f"   👤 {creator['name']} ({creator['platform']})")
                    print(f"       Followers: {creator['followers']:,}, Rate: ${creator['typical_rate']:,}")
                    print(f"       Match Score: {creator['match_score']:.2f}, Niche: {creator['niche']}")
                
                return creators
            else:
                print(f"   ❌ Creator discovery failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Creator discovery error: {str(e)}")
            return []
    
    async def test_trigger_calls(self, campaign_id: str):
        """Test triggering AI calls for a campaign"""
        print(f"\n4. 📞 Testing AI Call Triggering for {campaign_id}...")
        
        try:
            params = {
                "max_creators": 3,  # Limit to 3 for testing
                "call_priority": "high_match",
                "force_refresh": False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/campaign-trigger/trigger/{campaign_id}",
                params=params
            )
            
            if response.status_code == 202:
                data = response.json()
                task_id = data.get("task_id")
                
                print(f"   ✅ AI calls triggered successfully!")
                print(f"   🎯 Task ID: {task_id}")
                print(f"   📞 Creators to call: {data.get('calls_initiated', 0)}")
                print(f"   ⏱️ Estimated duration: {data.get('estimated_duration_minutes', 0)} minutes")
                print(f"   🔗 Monitor URL: {data.get('monitor_url', 'N/A')}")
                
                # Show creator details
                creator_details = data.get("creator_details", [])
                for creator in creator_details:
                    print(f"   👤 Will call: {creator['name']} ({creator['phone']})")
                
                return task_id
            else:
                print(f"   ❌ Call triggering failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Call triggering error: {str(e)}")
            return None
    
    async def test_monitor_progress(self, task_id: str, max_wait_minutes: int = 5):
        """Test monitoring campaign progress"""
        print(f"\n5. 📊 Testing Progress Monitoring for {task_id}...")
        
        try:
            start_time = time.time()
            max_wait_seconds = max_wait_minutes * 60
            check_interval = 10  # Check every 10 seconds
            
            while time.time() - start_time < max_wait_seconds:
                response = self.session.get(f"{self.base_url}/api/campaign-trigger/monitor/{task_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    status = data.get("status", "unknown")
                    progress = data.get("progress_percentage", 0)
                    total_calls = data.get("total_calls", 0)
                    completed_calls = data.get("completed_calls", 0)
                    successful_negotiations = data.get("successful_negotiations", 0)
                    
                    print(f"   📊 Status: {status} | Progress: {progress:.1f}%")
                    print(f"   📞 Calls: {completed_calls}/{total_calls} | Successful: {successful_negotiations}")
                    
                    # Show individual call status
                    call_status = data.get("call_status", [])
                    for call in call_status[:3]:  # Show first 3
                        creator_name = call.get("creator_name", "Unknown")
                        call_status_text = call.get("call_status", "unknown")
                        final_rate = call.get("final_rate", 0)
                        
                        print(f"       👤 {creator_name}: {call_status_text}", end="")
                        if final_rate > 0:
                            print(f" (${final_rate:,.0f})")
                        else:
                            print()
                    
                    # Check if completed
                    if status in ["completed", "failed"] or progress >= 100:
                        print(f"   ✅ Campaign monitoring completed!")
                        print(f"   🎯 Final Status: {status}")
                        print(f"   📈 Success Rate: {(successful_negotiations/total_calls*100):.1f}%" if total_calls > 0 else "N/A")
                        return True
                    
                    # Wait before next check
                    print(f"   ⏳ Waiting {check_interval} seconds for next update...\n")
                    time.sleep(check_interval)
                    
                else:
                    print(f"   ❌ Monitor request failed: {response.status_code}")
                    return False
            
            print(f"   ⏰ Monitoring timeout after {max_wait_minutes} minutes")
            print(f"   💡 Campaign may still be running - check manually later")
            return False
            
        except Exception as e:
            print(f"   ❌ Progress monitoring error: {str(e)}")
            return False
    
    async def test_specific_campaign(self, campaign_id: str):
        """Test a specific campaign by ID"""
        print(f"🎯 Testing specific campaign: {campaign_id}")
        print("=" * 50)
        
        # 1. Discover creators
        creators = await self.test_discover_creators(campaign_id)
        
        if not creators:
            print("❌ No creators found for this campaign")
            return False
        
        # 2. Confirm before triggering
        print(f"\n🤔 Ready to trigger AI calls to {len(creators)} creators?")
        print("   This will make actual API calls to your AI agents.")
        
        # For automated testing, we'll proceed. In interactive mode, you'd ask for confirmation.
        proceed = True  # input("   Proceed? (y/n): ").lower().startswith('y')
        
        if proceed:
            # 3. Trigger calls
            task_id = await self.test_trigger_calls(campaign_id)
            
            if task_id:
                # 4. Monitor progress
                await self.test_monitor_progress(task_id)
            
            return True
        else:
            print("   ⏹️ Skipped call triggering")
            return False

def print_usage():
    """Print usage instructions"""
    print("\n📖 Campaign Trigger API Usage:")
    print("=" * 50)
    print("1. Setup sample data:")
    print("   python setup_sample_data.py")
    print()
    print("2. Start the server:")
    print("   python main.py")
    print()
    print("3. Run this test:")
    print("   python test_campaign_trigger.py")
    print()
    print("4. Manual API Testing:")
    print("   • GET /api/campaign-trigger/campaigns")
    print("   • GET /api/campaign-trigger/discover/{campaign_id}")
    print("   • POST /api/campaign-trigger/trigger/{campaign_id}")
    print("   • GET /api/campaign-trigger/monitor/{task_id}")
    print()
    print("🎯 Sample Campaign IDs:")
    print("   • tech_campaign_001 - TechPro Wireless Earbuds")
    print("   • fitness_campaign_002 - FitPro Protein Powder")
    print("   • beauty_campaign_003 - GlowUp Skincare Set")

async def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO)
    
    tester = CampaignTriggerTester()
    
    print("🎯 Campaign Trigger API Tester")
    print("=" * 40)
    
    # Run full test suite
    success = await tester.run_full_test()
    
    if success:
        print("\n🎉 All tests passed!")
        print_usage()
    else:
        print("\n💡 Some tests failed - check the setup and try again")
        print_usage()

if __name__ == "__main__":
    asyncio.run(main()) 