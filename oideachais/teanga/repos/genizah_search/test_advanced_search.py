#!/usr/bin/env python3
"""
Test script for the new shelf mark search functionality
"""

import requests
import json
import sys

API_BASE_URL = "api.cairogenizah.ai"

def test_shelfmark_search():
    """Test the shelf mark search endpoint"""
    print("Testing shelf mark search functionality...")
    
    # Test data
    test_cases = [
        {
            "shelf_mark": "T-S 8J5.1",
            "exact_match": True,
            "description": "Exact match test"
        },
        {
            "shelf_mark": "T-S 8J5",
            "exact_match": False,
            "description": "Partial match test"
        },
        {
            "shelf_mark": "MS-TS-NS-144",
            "exact_match": False,
            "description": "MS-TS format test"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Searching for: {test_case['shelf_mark']}")
        print(f"   Exact match: {test_case['exact_match']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/search-shelfmark",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: Found {data['count']} results")
                print(f"   ⏱️  Processing time: {data['processing_time_ms']}ms")
                
                if data['results']:
                    first_result = data['results'][0]
                    print(f"   📄 First result: {first_result['doc_id']}")
                    if first_result['metadata']:
                        shelf_mark = first_result['metadata'].get('shelf_mark') or first_result['metadata'].get('shelfmark')
                        print(f"   🏷️  Shelf mark: {shelf_mark}")
                else:
                    print("   ℹ️  No results found")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error: Make sure the backend is running on localhost:8000")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    return True

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        return False

def test_endpoints_list():
    """Test if the new endpoint is listed in the API root"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            if 'search_shelfmark' in endpoints:
                print("✅ Shelf mark search endpoint is properly documented")
                return True
            else:
                print("❌ Shelf mark search endpoint not found in API documentation")
                return False
        else:
            print(f"❌ Failed to get API root: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking API root: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Cairo Genizah Advanced Search Implementation")
    print("=" * 60)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: API Health
    if test_api_health():
        tests_passed += 1
    
    # Test 2: Endpoint Documentation
    if test_endpoints_list():
        tests_passed += 1
    
    # Test 3: Shelf Mark Search
    if test_shelfmark_search():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The advanced search feature is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1)
