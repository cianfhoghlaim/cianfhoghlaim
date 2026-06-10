#!/usr/bin/env python3
"""
Test script for Cairo Genizah Search Service
"""

import requests
import json
import time
import os
from typing import Dict, Any

# Your search service URL (update this to your actual endpoint)
BASE_URL = "http://localhost:8000"  # Update this to your actual service URL


def test_health_check():
    """Test the health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_search(query: str, filters: Dict[str, Any] = None, num_results: int = 5):
    """Test a search query"""
    print(f"\n=== Testing Search: '{query}' ===")

    payload = {
        "query": query,
        "num_results": num_results
    }

    if filters:
        payload["filters"] = filters
        print(f"Filters: {filters}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        request_time = (time.time() - start_time) * 1000

        print(f"Status: {response.status_code}")
        print(f"Request time: {request_time:.2f}ms")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"Results found: {data['count']}")
            print(f"Processing time: {data['processing_time_ms']}ms")

            # Show first few results
            for i, result in enumerate(data['results'][:3], 1):
                print(f"\nResult {i}:")
                print(f"  Doc ID: {result['doc_id']}")
                print(f"  Similarity: {result['similarity_score']}")
                print(f"  Distance: {result['distance']}")
        else:
            print(f"❌ Search failed: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Search error: {e}")
        return False


def test_filter_options():
    """Test getting available filter options"""
    print("\n=== Testing Filter Options ===")
    try:
        response = requests.get(f"{BASE_URL}/filters")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Filter options retrieved")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Filter options failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Filter options error: {e}")
        return False


def run_all_tests():
    """Run comprehensive tests"""
    print("🧪 Starting Cairo Genizah Search Service Tests")
    print("=" * 50)

    # Test 1: Health check
    health_ok = test_health_check()
    if not health_ok:
        print("❌ Service not healthy, stopping tests")
        return

    # Test 2: Filter options
    test_filter_options()

    # Test 3: Basic search
    test_search("Hebrew marriage document")

    # Test 4: Search with language filter
    test_search(
        "legal document",
        filters={"language": "Hebrew"}
    )

    # Test 5: Search with multiple filters
    test_search(
        "marriage",
        filters={
            "language": "Hebrew",
            "document_type": "marriage",
            "institution": "cambridge"
        }
    )

    # Test 6: Search for Arabic documents
    test_search(
        "Arabic letter",
        filters={"language": "Judaeo-Arabic"}
    )

    # Test 7: Search with more results
    test_search("cambridge document", num_results=10)

    print("\n" + "=" * 50)
    print("🏁 Tests completed!")


# Direct API test functions for manual testing
def manual_curl_examples():
    """Generate curl commands for manual testing"""
    print("\n=== Manual CURL Test Commands ===")

    # Health check
    print("# Health Check:")
    print(f"curl -X GET {BASE_URL}/health")

    # Basic search
    print("\n# Basic Search:")
    print(f"""curl -X POST {BASE_URL}/search \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "Hebrew marriage document", "num_results": 5}}'""")

    # Search with filters
    print("\n# Search with Filters:")
    print(f"""curl -X POST {BASE_URL}/search \\
  -H "Content-Type: application/json" \\
  -d '{{
    "query": "legal document",
    "filters": {{"language": "Hebrew", "document_type": "marriage"}},
    "num_results": 3
  }}'""")

    # Filter options
    print("\n# Get Filter Options:")
    print(f"curl -X GET {BASE_URL}/filters")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "curl":
            manual_curl_examples()
        elif sys.argv[1] == "health":
            test_health_check()
        elif sys.argv[1] == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "Hebrew document"
            test_search(query)
        else:
            print("Usage: python test_search.py [curl|health|search 'query']")
    else:
        # Update BASE_URL if provided via environment
        if "SEARCH_SERVICE_URL" in os.environ:
            BASE_URL = os.environ["SEARCH_SERVICE_URL"]

        run_all_tests()