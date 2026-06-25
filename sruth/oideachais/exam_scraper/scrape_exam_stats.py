import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
import json
from datetime import datetime

BASE_URL = "https://www.examinations.ie/statistics/"
DOWNLOAD_DIR = "downloaded_stats"
FAILED_LOG = "failed_downloads.json"
START_YEAR = 2011
END_YEAR = 2024
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds

# Create base download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def to_snake_case(text):
    """Converts a string to snake_case, suitable for filenames."""
    text = text.strip()
    text = re.sub(r'[\\/*?:"<>|\s]+', '_', text)
    text = re.sub(r'[^\w_]+', '', text)
    text = text.lower()
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    if not text:
        return f"file_{int(time.time())}"
    return text

def get_file_info(url, option_text):
    """Generate filename and path information for a download."""
    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)
    _, extension = os.path.splitext(original_filename)
    
    snake_case_name = to_snake_case(option_text)
    extension = extension.lower()
    if not extension.startswith('.'):
        extension = '.' + extension if extension else '.file'
    
    filename = f"{snake_case_name}{extension}"
    return filename, original_filename

def download_with_retry(url, file_path, original_filename, retries=0):
    """Attempt to download with exponential backoff retry logic."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True, None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429 and retries < MAX_RETRIES:
            wait_time = INITIAL_BACKOFF * (2 ** retries)
            print(f"    Rate limited. Waiting {wait_time} seconds before retry {retries + 1}/{MAX_RETRIES}")
            time.sleep(wait_time)
            return download_with_retry(url, file_path, original_filename, retries + 1)
        return False, str(e)
        
    except Exception as e:
        return False, str(e)

def log_failed_download(year, url, option_text, error):
    """Log failed downloads for later retry."""
    log_file = os.path.join(DOWNLOAD_DIR, FAILED_LOG)
    failed_downloads = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            try:
                failed_downloads = json.load(f)
            except json.JSONDecodeError:
                pass
    
    failed_downloads.append({
        'year': year,
        'url': url,
        'option_text': option_text,
        'error': error,
        'timestamp': datetime.now().isoformat()
    })
    
    with open(log_file, 'w') as f:
        json.dump(failed_downloads, f, indent=2)

def download_file(url, folder_path, option_text, year):
    """Downloads a file if it doesn't already exist."""
    filename, original_filename = get_file_info(url, option_text)
    file_path = os.path.join(folder_path, filename)
    
    # Skip if file already exists
    if os.path.exists(file_path):
        print(f"    Skipping existing file: {filename}")
        return True
    
    success, error = download_with_retry(url, file_path, original_filename)
    if success:
        print(f"    Downloaded: {filename} (from {original_filename})")
        return True
    else:
        print(f"    Failed to download {filename}: {error}")
        log_failed_download(year, url, option_text, error)
        return False

print(f"Starting download process for years {START_YEAR} to {END_YEAR}...")
print(f"Files will be saved in '{DOWNLOAD_DIR}' directory.")

for year in range(START_YEAR, END_YEAR + 1):
    year_short = str(year)[-2:]
    year_url = f"{BASE_URL}?l=en&mc=st&sc=ryr&yr=r{year_short}"
    print(f"\nProcessing year: {year} ({year_url})")

    year_dir = os.path.join(DOWNLOAD_DIR, str(year))
    os.makedirs(year_dir, exist_ok=True)

    try:
        page_response = requests.get(year_url, timeout=30)
        page_response.raise_for_status()
        soup = BeautifulSoup(page_response.content, 'html.parser')

        file_options = soup.find_all('option', value=lambda x: x and x.startswith('/misc-doc/'))

        if not file_options:
            print(f"  No file links found for {year}.")
            continue

        print(f"  Found {len(file_options)} potential file links.")

        download_count = 0
        skip_count = 0
        for option in file_options:
            relative_path = option.get('value')
            option_text = option.get_text(strip=True)

            if not relative_path or not option_text:
                print(f"    Skipping option with missing value or text: {option}")
                continue

            base_for_join = BASE_URL.split('/statistics/')[0] + '/'
            download_url = urljoin(base_for_join, relative_path.lstrip('/'))

            if download_file(download_url, year_dir, option_text, year):
                download_count += 1
            else:
                skip_count += 1

            # Reduced delay between files
            time.sleep(0.2)

        print(f"  Year {year} summary: {download_count} downloaded, {skip_count} skipped/failed")

    except requests.exceptions.RequestException as e:
        print(f"  Error fetching page for year {year}: {e}")
        log_failed_download(year, year_url, None, str(e))
    except Exception as e:
        print(f"  An unexpected error occurred processing year {year}: {e}")
        log_failed_download(year, year_url, None, str(e))

    # Slightly reduced delay between years
    time.sleep(0.5)

print("\nDownload process finished.")
print(f"Check {os.path.join(DOWNLOAD_DIR, FAILED_LOG)} for any failed downloads that need to be retried.")