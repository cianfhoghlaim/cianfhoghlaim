import os
import shutil
import hashlib
from pathlib import Path

# Paths
BASE_DIR = Path('/Users/cliste/dev/cianfhoghlaim')
OLD_RESEARCH_DIR = BASE_DIR / 'research' / 'old'
NEW_RESEARCH_DIR = BASE_DIR / 'research'

CATEGORIES = [
    "01_infrastructure_and_devops",
    "02_machine_learning_ai",
    "03_data_engineering",
    "04_linguistics_and_celtic_nlp",
    "05_education_and_edtech",
    "06_web_and_frontend",
    "07_crypto_and_web3"
]

CATEGORY_MAP = {
    "bonneagar": "01_infrastructure_and_devops",
    "infrastructure": "01_infrastructure_and_devops",
    "devops": "01_infrastructure_and_devops",
    
    "meaisínfhoghlaim": "02_machine_learning_ai",
    "ml": "02_machine_learning_ai",
    "ai": "02_machine_learning_ai",
    
    "data": "03_data_engineering",
    "duckdb": "03_data_engineering",
    
    "teanga": "04_linguistics_and_celtic_nlp",
    "linguistics": "04_linguistics_and_celtic_nlp",
    "nlp": "04_linguistics_and_celtic_nlp",
    "celtic": "04_linguistics_and_celtic_nlp",
    
    "scoil": "05_education_and_edtech",
    "education": "05_education_and_edtech",
    "edtech": "05_education_and_edtech",
    
    "web": "06_web_and_frontend",
    "frontend": "06_web_and_frontend",
    "ui": "06_web_and_frontend",
    
    "crypteolas": "07_crypto_and_web3",
    "tuath": "07_crypto_and_web3",
    "crypto": "07_crypto_and_web3",
    "web3": "07_crypto_and_web3",
    "ethereum": "07_crypto_and_web3",
    "smart-contracts": "07_crypto_and_web3",
    "tokenomics": "07_crypto_and_web3",
    "x402": "07_crypto_and_web3"
}

def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def determine_category(file_path):
    path_lower = str(file_path).lower()
    for kw, cat in CATEGORY_MAP.items():
        if kw in path_lower:
            return cat
    return "01_infrastructure_and_devops" # default

def main():
    if not OLD_RESEARCH_DIR.exists():
        print(f"Directory {OLD_RESEARCH_DIR} does not exist.")
        return

    # Create category directories
    for cat in CATEGORIES:
        (NEW_RESEARCH_DIR / cat).mkdir(parents=True, exist_ok=True)

    seen_hashes = set()
    moved_count = 0
    skipped_count = 0

    # Walk through all files in OLD_RESEARCH_DIR
    for root, _, files in os.walk(OLD_RESEARCH_DIR):
        for file in files:
            if file == ".DS_Store":
                continue
                
            file_path = Path(root) / file
            file_hash = compute_md5(file_path)
            
            if file_hash in seen_hashes:
                print(f"Skipping duplicate: {file_path}")
                skipped_count += 1
                os.remove(file_path) # remove the duplicate
                continue
                
            seen_hashes.add(file_hash)
            
            target_cat = determine_category(file_path)
            target_dir = NEW_RESEARCH_DIR / target_cat
            target_path = target_dir / file
            
            # handle filename collisions (same name but diff content)
            counter = 1
            while target_path.exists():
                name = target_path.stem
                ext = target_path.suffix
                target_path = target_dir / f"{name}_{counter}{ext}"
                counter += 1
                
            print(f"Moving {file_path} -> {target_path}")
            shutil.move(str(file_path), str(target_path))
            moved_count += 1

    print(f"\nMigration complete. Moved: {moved_count}, Skipped/Deleted (duplicates): {skipped_count}")

    # Remove empty directories in OLD_RESEARCH_DIR
    for root, dirs, files in os.walk(OLD_RESEARCH_DIR, topdown=False):
        for dir in dirs:
            dir_path = Path(root) / dir
            try:
                os.rmdir(dir_path)
            except OSError:
                pass # not empty
    
    # Try removing old research dir
    try:
        os.rmdir(OLD_RESEARCH_DIR)
        print("Removed empty research/old directory.")
    except OSError:
        print("research/old directory is not empty, leaving it.")

if __name__ == "__main__":
    main()
