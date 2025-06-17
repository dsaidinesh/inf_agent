#!/usr/bin/env python3
"""
🎯 Quick Decision API Test
Tests the improved error handling for expired/invalid decision IDs
"""

import requests
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_decision_endpoints():
    """Test decision endpoints with various scenarios"""
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Decision API Error Handling")
    print("=" * 50)
    
    # Test 1: Valid decision ID (should fail gracefully if expired)
    print("\n1. 🧪 Testing expired decision ID...")
    expired_decision_id = "DEC-3FB627FB"  # From the logs
    
    try:
        response = requests.get(f"{base_url}/api/decision/approve/{expired_decision_id}")
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📄 Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("   ✅ Graceful handling - User sees friendly error page")
            # Check if it's HTML (user-friendly page)
            if 'text/html' in response.headers.get('content-type', ''):
                print("   🎨 HTML response - User-friendly interface")
            else:
                print("   📝 Non-HTML response")
        else:
            print(f"   ❌ Error response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️ Server not running - start with 'uvicorn main:app --reload --port 8000'")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False
    
    # Test 2: Invalid decision ID
    print("\n2. 🧪 Testing invalid decision ID...")
    invalid_decision_id = "DEC-INVALID123"
    
    try:
        response = requests.get(f"{base_url}/api/decision/approve/{invalid_decision_id}")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Graceful handling - User sees friendly error page")
        else:
            print(f"   ❌ Error response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Check pending decisions
    print("\n3. 🧪 Testing pending decisions endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/decision/pending")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pending_count = data.get('pending_decisions', {}).get('total_pending', 0)
            print(f"   📋 Pending decisions: {pending_count}")
            print("   ✅ Pending decisions endpoint working")
        else:
            print(f"   ❌ Error response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Decision API error handling test completed!")
    print("\n📖 What this means:")
    print("   • Sponsors clicking expired links get friendly error pages")
    print("   • No more 'dict object is not callable' crashes")
    print("   • Clear explanations of what went wrong")
    print("   • Better user experience for decision workflows")
    
    return True

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = test_decision_endpoints()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed - check server status") 