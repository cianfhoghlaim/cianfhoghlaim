import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

SAMPLES_DIR = Path("/Users/cianmacandeisigh/dev/kings_college_galway/stedding/site_scrape_samples")

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/")
    
    # Example logic: ncca.ie/en/about-ncca -> ncca.ie_en_about-ncca_.json
    if not path:
        return f"{domain}_.json"
        
    path_slug = path.replace("/", "_")
    return f"{domain}_{path_slug}_.json"

url = "https://ncca.ie/en/about-ncca/about-us/what-we-do"
domain = urlparse(url).netloc.replace("www.", "")
expected_file = SAMPLES_DIR / domain / url_to_filename(url)
print(f"URL: {url}")
print(f"Expected file: {expected_file}")
print(f"Exists: {expected_file.exists()}")

url2 = "https://ncca.ie/en/"
expected_file2 = SAMPLES_DIR / domain / url_to_filename(url2)
print(f"URL: {url2}")
print(f"Expected file: {expected_file2}")
print(f"Exists: {expected_file2.exists()}")
