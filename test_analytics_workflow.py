#!/usr/bin/env python3
"""
🧪 ANALYTICS WORKFLOW TEST SCRIPT
Test the complete post-call analytics and sponsor decision workflow

This script demonstrates:
1. ✅ Call completion processing
2. 📊 Analytics generation and email to sponsor
3. 🤔 Sponsor decision workflow (approve/reject)
4. 📄 Contract sending or regret emails
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class AnalyticsWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    def run_complete_test(self):
        """🎯 Run the complete analytics workflow test"""
        
        print("=" * 70)
        print("🧪 ANALYTICS WORKFLOW COMPREHENSIVE TEST")
        print("=" * 70)
        print("Testing the complete post-call analytics and decision workflow")
        print()
        
        try:
            # Test 1: Test basic analytics service
            print("1. 🧪 Testing analytics service...")
            self.test_analytics_service()
            
            # Test 2: Test completed call processing
            print("\n2. 📊 Testing completed call processing...")
            decision_id = self.test_completed_call_processing()
            
            # Test 3: Test sponsor decision workflow
            if decision_id:
                print(f"\n3. 🤔 Testing sponsor decision workflow...")
                print(f"   Decision ID: {decision_id}")
                self.test_sponsor_decision_workflow(decision_id)
            
            # Test 4: Test pending decisions
            print("\n4. 📋 Testing pending decisions...")
            self.test_pending_decisions()
            
            # Test 5: Test full workflow with different scenarios
            print("\n5. 🎭 Testing different scenarios...")
            self.test_different_scenarios()
            
            print("\n" + "=" * 70)
            print("🏁 ANALYTICS WORKFLOW TEST COMPLETED!")
            print("=" * 70)
            
            self.print_test_summary()
            
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            return False
    
    def test_analytics_service(self):
        """Test basic analytics service functionality"""
        
        try:
            # Test the test endpoint
            response = requests.post(
                f"{self.base_url}/api/decision/test-analytics",
                json={
                    "influencer_name": "Test Analytics Influencer",
                    "influencer_email": "analytics@test.com",
                    "sponsor_email": "sponsor@testbrand.com",
                    "campaign_name": "Analytics Test Campaign",
                    "brand_name": "Analytics Test Brand",
                    "final_rate": 3000,
                    "original_rate": 2500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Analytics service test passed")
                print(f"   📊 Decision ID: {data.get('decision_id', 'N/A')}")
                print(f"   📧 Analytics sent: {data.get('analytics_sent', False)}")
                
                self.test_results['analytics_service'] = {
                    'status': 'passed',
                    'decision_id': data.get('decision_id')
                }
                
                return data.get('decision_id')
            else:
                print(f"   ❌ Analytics service test failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                self.test_results['analytics_service'] = {'status': 'failed', 'error': response.text}
                return None
                
        except Exception as e:
            print(f"   ❌ Analytics service test exception: {e}")
            self.test_results['analytics_service'] = {'status': 'failed', 'error': str(e)}
            return None
    
    def test_completed_call_processing(self) -> str:
        """Test processing a completed call"""
        
        try:
            # Simulate a completed call with rich data
            call_completion_data = {
                "call_data": {
                    "conversation_id": f"test_conv_{int(time.time())}",
                    "call_duration_seconds": 240,  # 4 minutes
                    "status": "completed",
                    "negotiation_results": {
                        "final_rate": 2800,
                        "deliverables": [
                            "1 Instagram post with product showcase",
                            "3 Instagram stories",
                            "1 TikTok video review"
                        ],
                        "timeline": "3 weeks",
                        "creator_enthusiasm": 9,
                        "special_terms": [
                            "Usage rights for 12 months",
                            "Exclusive product category for 30 days"
                        ],
                        "key_quotes": [
                            "I absolutely love this product!",
                            "My audience will definitely connect with this",
                            "The timing works perfectly with my content calendar"
                        ]
                    },
                    "influencer_data": {
                        "name": "Sarah Johnson",
                        "email": "sarah@influencertest.com",
                        "platform": "Instagram",
                        "followers": 125000
                    }
                },
                "campaign_data": {
                    "campaign_name": "TechPro Wireless Headphones Launch",
                    "brand_name": "TechPro Audio",
                    "product_name": "TechPro Wireless Pro",
                    "total_budget": 15000,
                    "offered_rate": 2200,
                    "target_audience": "Tech enthusiasts, fitness lovers"
                },
                "sponsor_email": "marketing@techproaudio.com"
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook/process-completed-call",
                json=call_completion_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Call processing successful")
                print(f"   📊 Decision ID: {data.get('decision_id', 'N/A')}")
                print(f"   📧 Analytics report generated: {bool(data.get('analytics_report'))}")
                print(f"   ⏰ Decision expires: {data.get('decision_expires_at', 'N/A')}")
                
                self.test_results['call_processing'] = {
                    'status': 'passed',
                    'decision_id': data.get('decision_id'),
                    'analytics_generated': bool(data.get('analytics_report'))
                }
                
                return data.get('decision_id')
            else:
                print(f"   ❌ Call processing failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                self.test_results['call_processing'] = {'status': 'failed', 'error': response.text}
                return None
                
        except Exception as e:
            print(f"   ❌ Call processing exception: {e}")
            self.test_results['call_processing'] = {'status': 'failed', 'error': str(e)}
            return None
    
    def test_sponsor_decision_workflow(self, decision_id: str):
        """Test the sponsor decision workflow"""
        
        print(f"   🔗 Decision URLs:")
        print(f"      Approve: {self.base_url}/api/decision/approve/{decision_id}")
        print(f"      Reject:  {self.base_url}/api/decision/reject/{decision_id}")
        
        # Test approval workflow
        print(f"   ✅ Testing approval workflow...")
        try:
            approve_response = requests.get(
                f"{self.base_url}/api/decision/approve/{decision_id}",
                timeout=30
            )
            
            if approve_response.status_code == 200:
                print(f"      ✅ Approval workflow accessible")
                self.test_results['approval_workflow'] = {'status': 'accessible'}
            else:
                print(f"      ❌ Approval workflow failed: {approve_response.status_code}")
                self.test_results['approval_workflow'] = {'status': 'failed'}
                
        except Exception as e:
            print(f"      ❌ Approval workflow exception: {e}")
            self.test_results['approval_workflow'] = {'status': 'failed', 'error': str(e)}
        
        # Test rejection form
        print(f"   ❌ Testing rejection form...")
        try:
            reject_response = requests.get(
                f"{self.base_url}/api/decision/reject/{decision_id}",
                timeout=30
            )
            
            if reject_response.status_code == 200:
                print(f"      ✅ Rejection form accessible")
                self.test_results['rejection_form'] = {'status': 'accessible'}
            else:
                print(f"      ❌ Rejection form failed: {reject_response.status_code}")
                self.test_results['rejection_form'] = {'status': 'failed'}
                
        except Exception as e:
            print(f"      ❌ Rejection form exception: {e}")
            self.test_results['rejection_form'] = {'status': 'failed', 'error': str(e)}
    
    def test_pending_decisions(self):
        """Test pending decisions endpoint"""
        
        try:
            response = requests.get(
                f"{self.base_url}/api/decision/pending",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                pending_count = data.get('pending_decisions', {}).get('total_pending', 0)
                print(f"   ✅ Pending decisions retrieved: {pending_count} pending")
                
                if pending_count > 0:
                    print(f"   📋 Recent decisions:")
                    for decision in data['pending_decisions']['decisions'][:3]:  # Show first 3
                        print(f"      • {decision.get('campaign_name', 'N/A')} - {decision.get('influencer_name', 'N/A')}")
                
                self.test_results['pending_decisions'] = {
                    'status': 'passed',
                    'total_pending': pending_count
                }
            else:
                print(f"   ❌ Pending decisions failed: {response.status_code}")
                self.test_results['pending_decisions'] = {'status': 'failed'}
                
        except Exception as e:
            print(f"   ❌ Pending decisions exception: {e}")
            self.test_results['pending_decisions'] = {'status': 'failed', 'error': str(e)}
    
    def test_different_scenarios(self):
        """Test different call outcome scenarios"""
        
        scenarios = [
            {
                "name": "High-value successful negotiation",
                "final_rate": 5000,
                "original_rate": 3500,
                "enthusiasm": 9,
                "deliverables": ["Premium video review", "Multiple posts", "Story series"]
            },
            {
                "name": "Budget-friendly collaboration",
                "final_rate": 800,
                "original_rate": 750,
                "enthusiasm": 7,
                "deliverables": ["Single Instagram post", "2 stories"]
            },
            {
                "name": "Complex negotiation with special terms",
                "final_rate": 3200,
                "original_rate": 2000,
                "enthusiasm": 6,
                "deliverables": ["Video review", "Instagram posts", "Blog mention"]
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"   🎭 Scenario {i}: {scenario['name']}")
            
            try:
                test_data = {
                    "influencer_name": f"Scenario{i} Influencer",
                    "influencer_email": f"scenario{i}@test.com",
                    "sponsor_email": f"sponsor{i}@testbrand.com",
                    "campaign_name": f"Scenario {i} Campaign",
                    "brand_name": f"Scenario {i} Brand",
                    "final_rate": scenario["final_rate"],
                    "original_rate": scenario["original_rate"]
                }
                
                response = requests.post(
                    f"{self.base_url}/api/decision/test-analytics",
                    json=test_data,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Scenario {i} processed successfully")
                    print(f"      📊 Decision ID: {data.get('decision_id', 'N/A')}")
                else:
                    print(f"      ❌ Scenario {i} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Scenario {i} exception: {e}")
                
            time.sleep(1)  # Brief pause between scenarios
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        
        print("\n📊 TEST SUMMARY:")
        print("-" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'passed' or r.get('status') == 'accessible'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = result.get('status', 'unknown')
            emoji = "✅" if status in ['passed', 'accessible'] else "❌"
            print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")
        
        print("\n🎯 WHAT THIS WORKFLOW DOES:")
        print("1. 📞 Processes completed calls with structured analytics")
        print("2. 📊 Generates professional analytics reports")
        print("3. 📧 Sends analytics to sponsors via email")
        print("4. 🤔 Provides approve/reject decision interface")
        print("5. 📄 Automatically sends contracts on approval")
        print("6. 😔 Sends polite regret emails on rejection")
        
        print("\n🚀 HOW TO USE IN PRODUCTION:")
        print("1. Call /api/webhook/process-completed-call after each call")
        print("2. Sponsor receives email with analytics and decision buttons")
        print("3. Sponsor clicks approve/reject links")
        print("4. System automatically handles contract/regret emails")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Your analytics workflow is ready!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Check the errors above.")

def main():
    """Main function to run the analytics workflow test"""
    
    print("🚀 Starting Analytics Workflow Test...")
    print("Make sure your server is running on http://localhost:8000")
    print()
    
    tester = AnalyticsWorkflowTester()
    tester.run_complete_test()

 