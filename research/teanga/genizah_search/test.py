#!/usr/bin/env python3
"""
Proper Elasticsearch 8.x client configuration for HTTP connections
"""

from elasticsearch import Elasticsearch
import urllib3

# Disable SSL warnings for HTTP connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_elasticsearch_client(host="34.59.164.124", port=9200):
    """Create properly configured ES client for HTTP connections"""

    # Method 1: Basic HTTP configuration
    es = Elasticsearch(
        hosts=[{"host": host, "port": port, "scheme": "http"}],
        max_retries=3,
        retry_on_timeout=True,
        verify_certs=False,
        ssl_show_warn=False,
        sniff_on_start=False,
    )

    return es


def test_connection():
    """Test the connection"""
    es = create_elasticsearch_client()

    try:
        # Test ping
        if es.ping():
            print("✅ Ping successful")
        else:
            print("❌ Ping failed")
            return False

        # Test info
        info = es.info()
        print(f"✅ ES Version: {info['version']['number']}")
        print(f"✅ Cluster: {info['cluster_name']}")

        return True

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Elasticsearch connection...")
    success = test_connection()
    if success:
        print("🎉 Connection working!")
    else:
        print("💥 Connection failed")