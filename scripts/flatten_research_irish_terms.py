import os
import shutil
from pathlib import Path
import hashlib

def get_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def merge_directories(src_dir, dest_dir):
    """
    Recursively moves all files from src_dir to dest_dir.
    If a file exists and is identical (MD5 matches), it deletes the src file.
    If it's different, it renames it before moving.
    """
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    
    if not src_dir.exists():
        return
        
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for item in src_dir.iterdir():
        if item.name == ".DS_Store":
            item.unlink()
            continue
            
        target_path = dest_dir / item.name
        
        if item.is_dir():
            merge_directories(item, target_path)
            # Try to remove the directory if it's now empty
            try:
                item.rmdir()
            except OSError:
                pass
        else:
            if target_path.exists():
                src_hash = get_md5(item)
                dest_hash = get_md5(target_path)
                
                if src_hash == dest_hash and src_hash is not None:
                    print(f"Skipping duplicate: {item.relative_to(Path.cwd())}")
                    item.unlink()
                else:
                    # Resolve conflict
                    counter = 1
                    while target_path.exists():
                        target_path = dest_dir / f"{item.stem}_{counter}{item.suffix}"
                        counter += 1
                    print(f"Moving (renamed) {item.relative_to(Path.cwd())} -> {target_path.relative_to(Path.cwd())}")
                    shutil.move(str(item), str(target_path))
            else:
                print(f"Moving {item.relative_to(Path.cwd())} -> {target_path.relative_to(Path.cwd())}")
                shutil.move(str(item), str(target_path))

def main():
    base_research = Path("research")
    
    # Map of redundant (deeply nested / alias) folders to target parent folders
    # 'taighde' -> '' (root of research)
    # 'bonneagar' -> 'infrastructure'
    
    moves = [
        (base_research / "taighde", base_research),
        (base_research / "bonneagar", base_research / "infrastructure"),
    ]
    
    for src, dest in moves:
        if src.exists() and src.is_dir():
            print(f"Processing {src.relative_to(Path.cwd())}...")
            merge_directories(src, dest)
            try:
                src.rmdir()
                print(f"Removed now empty directory: {src}")
            except OSError:
                print(f"Could not remove directory (not empty): {src}")
                
if __name__ == "__main__":
    main()
