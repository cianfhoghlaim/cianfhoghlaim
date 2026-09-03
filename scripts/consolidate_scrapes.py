import os
import json
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Config
SOURCE_DIR = "stedding/site_scrape_samples"
DEST_DIR = "stedding/site_scrape_samples_clean"
MAX_WORKERS = 10
LIMIT = None  # Process all files if possible, or limit for speed

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def consolidate_content(data):
    """
    Extracts the useful markdown content, applies heuristics to filter out
    purely administrative/cookie pages, and returns the cleaned markdown.
    """
    if not data or 'markdown' not in data or 'metadata' not in data:
        return None, "FILTERED_NO_DATA"
    
    markdown = data.get('markdown', '')
    if not markdown or len(markdown) < 150:
        return None, "FILTERED_TOO_SHORT"
        
    url = data['metadata'].get('url', '').lower()
    
    # Filter known irrelevant paths
    irrelevant_patterns = ['/contact/', '/news/', '/cookie-policy/', '/privacy-policy/', '/about/', '/contact-us/']
    for pattern in irrelevant_patterns:
        if pattern in url:
            return None, f"FILTERED_URL_PATTERN"
            
    # Calculate Nav to Content ratio (rough heuristic)
    if "Manage Cookie Consent" in markdown and len(markdown) < 4000:
        return None, "FILTERED_COOKIE_BANNER_ONLY"
        
    # Heuristic: Remove standard footer / nav elements if possible
    # We will just split by "Manage consent" or standard Oide/NCCA footer texts
    clean_lines = []
    for line in markdown.split('\n'):
        if "Manage Cookie Consent" in line or "Cookie Policy" in line or "Privacy" in line:
            continue
        clean_lines.append(line)
        
    cleaned_markdown = '\n'.join(clean_lines).strip()
    
    if len(cleaned_markdown) < 100:
        return None, "FILTERED_EMPTY_AFTER_CLEAN"
        
    return cleaned_markdown, "SUCCESS"

def process_file(filepath):
    try:
        data = load_json(filepath)
        cleaned_markdown, status = consolidate_content(data)
        
        if status != "SUCCESS":
            return filepath, status
            
        # Determine output path
        path_obj = Path(filepath)
        domain = path_obj.parent.name
        basename = path_obj.stem
        out_path = Path(DEST_DIR) / domain / f"{basename}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# Source: {data['metadata'].get('url', 'Unknown')}\n\n")
            f.write(cleaned_markdown)
            
        return filepath, "SUCCESS"
        
    except Exception as e:
        return filepath, f"ERROR: {str(e)}"

def main():
    print(f"Starting heuristic consolidation.")
    os.makedirs(DEST_DIR, exist_ok=True)
    
    all_files = glob.glob(f"{SOURCE_DIR}/**/*.json", recursive=True)
    if LIMIT:
        all_files = all_files[:LIMIT]
        
    print(f"Found {len(all_files)} files to process.")
    
    results = {"SUCCESS": 0, "FILTERED_TOO_SHORT": 0, "FILTERED_URL_PATTERN": 0, "FILTERED_COOKIE_BANNER_ONLY": 0, "FILTERED_EMPTY_AFTER_CLEAN": 0, "ERROR": 0}
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, fp): fp for fp in all_files}
        
        for i, future in enumerate(as_completed(futures), 1):
            filepath, status = future.result()
            
            if status in results:
                results[status] += 1
            else:
                # Catch-all
                for key in results:
                    if status.startswith(key):
                        results[key] += 1
                        break
                    
            if i % 1000 == 0:
                print(f"Processed {i}/{len(all_files)} files. Status: {results}")

    print("\n--- Final Summary ---")
    print(f"Total processed: {len(all_files)}")
    for k, v in results.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
