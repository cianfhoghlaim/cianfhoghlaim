import os
import shutil
import hashlib
from pathlib import Path

# Paths
BASE_DIR = Path.cwd() / 'education' / 'research'

# We want to flatten the deeply nested subdirectories like 'old', 'taighde', 'bonneagar', 'meaisínfhoghlaim' 
# into standard top-level directories in 'education/research/'

CATEGORIES = [
    "infrastructure",
    "machine_learning",
    "data_engineering",
    "teanga",
    "education",
    "web",
    "crypto"
]

CATEGORY_MAP = {
    "bonneagar": "infrastructure",
    "infrastructure": "infrastructure",
    "devops": "infrastructure",
    
    "meaisínfhoghlaim": "machine_learning",
    "ml": "machine_learning",
    "ai": "machine_learning",
    
    "data": "data_engineering",
    "duckdb": "data_engineering",
    "dagster": "data_engineering",
    "dlt": "data_engineering",
    
    "teanga": "teanga",
    "linguistics": "teanga",
    "nlp": "teanga",
    "celtic": "teanga",
    
    "scoil": "education",
    "education": "education",
    "edtech": "education",
    
    "web": "web",
    "frontend": "web",
    "ui": "web",
    
    "crypteolas": "crypto",
    "tuath": "crypto",
    "crypto": "crypto",
    "web3": "crypto"
}

def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def determine_category(file_path):
    path_lower = str(file_path).lower()
    for kw, cat in CATEGORY_MAP.items():
        if kw in path_lower:
            return cat
    return "infrastructure" # default

def main():
    if not BASE_DIR.exists():
        print(f"Directory {BASE_DIR} does not exist.")
        return

    # Create top-level category directories if they don't exist
    for cat in CATEGORIES:
        (BASE_DIR / cat).mkdir(parents=True, exist_ok=True)

    seen_hashes = {}
    moved_count = 0
    skipped_count = 0

    # Phase 1: Hash all files already in the top-level target categories
    for cat in CATEGORIES:
        cat_dir = BASE_DIR / cat
        if cat_dir.exists():
            for root, _, files in os.walk(cat_dir):
                for file in files:
                    if file == ".DS_Store":
                        continue
                    file_path = Path(root) / file
                    file_hash = compute_md5(file_path)
                    if file_hash:
                        seen_hashes[file_hash] = file_path

    # Phase 2: Walk through specific deep directories to flatten them
    directories_to_flatten = ["old", "taighde", "bonneagar", "meaisínfhoghlaim", "skills", "project-context"]
    
    for dir_name in directories_to_flatten:
        target_dir = BASE_DIR / dir_name
        if not target_dir.exists():
            continue
            
        print(f"\nProcessing {dir_name}...")
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file == ".DS_Store":
                    continue
                    
                file_path = Path(root) / file
                file_hash = compute_md5(file_path)
                
                if file_hash in seen_hashes:
                    print(f"Skipping duplicate: {file_path.relative_to(BASE_DIR)} (matches {seen_hashes[file_hash].relative_to(BASE_DIR)})")
                    skipped_count += 1
                    os.remove(file_path) # remove the duplicate
                    continue
                    
                seen_hashes[file_hash] = file_path
                
                target_cat = determine_category(file_path)
                target_cat_dir = BASE_DIR / target_cat
                target_path = target_cat_dir / file
                
                # handle filename collisions (same name but diff content)
                counter = 1
                while target_path.exists():
                    name = target_path.stem
                    ext = target_path.suffix
                    target_path = target_cat_dir / f"{name}_{counter}{ext}"
                    counter += 1
                    
                print(f"Moving {file_path.relative_to(BASE_DIR)} -> {target_path.relative_to(BASE_DIR)}")
                shutil.move(str(file_path), str(target_path))
                moved_count += 1

        # Remove empty directories in the target dir
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for dir in dirs:
                dir_path = Path(root) / dir
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass # not empty
        
        # Try removing the main target dir itself
        try:
            os.rmdir(target_dir)
            print(f"Removed empty directory {dir_name}.")
        except OSError:
            print(f"Directory {dir_name} is not empty, leaving it.")

    print(f"\nMigration complete. Moved: {moved_count}, Skipped/Deleted (duplicates): {skipped_count}")

if __name__ == "__main__":
    main()
