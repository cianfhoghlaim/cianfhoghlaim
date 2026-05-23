import json
import os
import time
from scrape_exam_stats import download_file, DOWNLOAD_DIR, FAILED_LOG

def retry_failed_downloads():
    """Retry downloading files that previously failed."""
    log_file = os.path.join(DOWNLOAD_DIR, FAILED_LOG)
    
    if not os.path.exists(log_file):
        print("No failed downloads log found.")
        return
    
    with open(log_file, 'r') as f:
        try:
            failed_downloads = json.load(f)
        except json.JSONDecodeError:
            print("Error reading failed downloads log.")
            return
    
    if not failed_downloads:
        print("No failed downloads to retry.")
        return
    
    print(f"Found {len(failed_downloads)} failed downloads to retry.")
    
    # Keep track of still-failing downloads
    new_failures = []
    success_count = 0
    
    for entry in failed_downloads:
        year = entry['year']
        url = entry['url']
        option_text = entry['option_text']
        
        if not option_text:  # Skip page fetching errors
            print(f"Skipping page error for year {year}")
            new_failures.append(entry)
            continue
            
        print(f"\nRetrying download from year {year}:")
        print(f"URL: {url}")
        print(f"File: {option_text}")
        
        year_dir = os.path.join(DOWNLOAD_DIR, str(year))
        os.makedirs(year_dir, exist_ok=True)
        
        if download_file(url, year_dir, option_text, year):
            success_count += 1
        else:
            new_failures.append(entry)
        
        # Add delay between retries
        time.sleep(1)
    
    # Update the failed downloads log with any remaining failures
    if new_failures:
        with open(log_file, 'w') as f:
            json.dump(new_failures, f, indent=2)
        print(f"\nRetry complete: {success_count} succeeded, {len(new_failures)} still failed")
    else:
        # All succeeded, remove the log file
        os.remove(log_file)
        print(f"\nAll {success_count} failed downloads successfully retrieved!")

if __name__ == '__main__':
    retry_failed_downloads()