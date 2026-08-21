#!/usr/bin/env python3
"""
SEC Exam Materials Scraper using Firecrawl API.

Direct API call without local browser requirements.
"""
import subprocess
import json
import sys

API_KEY = "fc-1bc5f738cecc4997939dd31d202e5fcb"
BASE_URL = "https://api.firecrawl.dev/v1"

def firecrawl_scrape(url, actions=None, extract_prompt=None):
    """Scrape URL with optional actions and extraction."""
    payload = {"url": url}

    if actions:
        payload["actions"] = actions

    if extract_prompt:
        payload["extract"] = {
            "schema": {
                "type": "object",
                "properties": {
                    "dropdowns": {
                        "type": "object",
                        "properties": {
                            "level_options": {"type": "array", "items": {"type": "string"}},
                            "subject_options": {"type": "array", "items": {"type": "string"}},
                            "year_options": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "pdf_links": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "year": {"type": "string"},
                                "subject": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "prompt": extract_prompt
        }

    cmd = [
        "curl", "-s", "-X", "POST", f"{BASE_URL}/scrape",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stdout, "stderr": result.stderr}

def main():
    print("\n" + "=" * 60)
    print("SEC Exam Materials Scraper - Firecrawl API")
    print("=" * 60)

    # Step 1: Load the page and accept terms
    print("\n[1/3] Loading page and accepting terms...")
    result1 = firecrawl_scrape(
        "https://www.examinations.ie/exammaterialarchive/",
        actions=[
            {"type": "wait", "milliseconds": 3000},
            {"type": "click", "selector": "input[type='checkbox']"},
            {"type": "wait", "milliseconds": 2000}
        ]
    )

    if result1.get("success"):
        print("  ✓ Page loaded, terms accepted")
    else:
        print(f"  ✗ Error: {result1.get('error', 'Unknown')}")
        return 1

    # Step 2: Extract dropdown options
    print("\n[2/3] Extracting dropdown options...")
    result2 = firecrawl_scrape(
        "https://www.examinations.ie/exammaterialarchive/",
        extract_prompt="Extract ALL dropdown options for Year (exam years), Level (Leaving Certificate/Junior Cycle), and Subject. List all available options."
    )

    if result2.get("success"):
        extract_data = result2.get("data", {})
        if "llm_extraction" in extract_data:
            extraction = extract_data["llm_extraction"]
            print(f"  ✓ Extraction result:")
            print(json.dumps(extraction, indent=4)[:1000])

    # Step 3: Try to get a sample search result
    print("\n[3/3] Searching for Mathematics 2024...")

    # Use Firecrawl's map/crawl to discover PDF URLs
    cmd = [
        "curl", "-s", "-X", "POST", f"{BASE_URL}/map",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "url": "https://www.examinations.ie/exammaterialarchive/",
            "search": "mathematics 2024 pdf filetype:pdf",
            "limit": 10
        })
    ]

    map_result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        map_data = json.loads(map_result.stdout)
        if map_data.get("success"):
            links = map_data.get("links", [])
            print(f"  ✓ Found {len(links)} potential links")
            for link in links[:5]:
                if ".pdf" in link.lower():
                    print(f"    - {link}")
    except:
        print(f"  Map result: {map_result.stdout[:500]}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
