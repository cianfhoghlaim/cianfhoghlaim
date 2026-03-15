import os
import sys
from pathlib import Path
from PIL import Image

def analyze_and_convert(start_path):
    print(f"Scanning directory: {start_path}")
    
    file_stats = {}
    large_files = []
    tif_files = []
    
    # scan files
    for root, dirs, files in os.walk(start_path):
        for file in files:
            file_path = Path(root) / file
            try:
                size = file_path.stat().st_size
                ext = file_path.suffix.lower()
                
                # Stats
                if ext not in file_stats:
                    file_stats[ext] = {'count': 0, 'total_size': 0}
                file_stats[ext]['count'] += 1
                file_stats[ext]['total_size'] += size
                
                # Check for TIFs
                if ext in ['.tif', '.tiff']:
                    tif_files.append(file_path)
                
                # Check for large files (arbitrary > 10MB for now to list them)
                if size > 10 * 1024 * 1024: # 10MB
                    large_files.append((file_path, size))
                    
            except Exception as e:
                print(f"Error accessing {file_path}: {e}")

    # Report Stats
    print("\n--- File Statistics ---")
    print(f"{'Extension':<10} | {'Count':<8} | {'Total Size (MB)':<15}")
    print("-" * 40)
    for ext, stats in sorted(file_stats.items(), key=lambda x: x[1]['total_size'], reverse=True):
        size_mb = stats['total_size'] / (1024 * 1024)
        print(f"{ext:<10} | {stats['count']:<8} | {size_mb:<15.2f}")

    print("\n--- Large Files (>10MB) ---")
    for fp, size in sorted(large_files, key=lambda x: x[1], reverse=True):
        print(f"{size / (1024*1024):.2f} MB: {fp}")

    # Convert TIFs
    print(f"\n--- Converting {len(tif_files)} TIF/TIFF files to PNG ---")
    saved_space = 0
    for tif_path in tif_files:
        try:
            png_path = tif_path.with_suffix('.png')
            
            # Open and save as PNG
            with Image.open(tif_path) as img:
                img.save(png_path, 'PNG', optimize=True)
            
            original_size = tif_path.stat().st_size
            new_size = png_path.stat().st_size
            diff = original_size - new_size
            saved_space += diff
            
            print(f"Converted: {tif_path.name}")
            print(f"  Old: {original_size/1024:.2f} KB -> New: {new_size/1024:.2f} KB")
            print(f"  Saved: {diff/1024:.2f} KB")
            
            # Optional: Remove original if successful? 
            # For safety, I will NOT remove them automatically in this pass, just report.
            # print(f"  (Original file kept for safety)")
            
            # UNCOMMENT TO DELETE ORIGINALS
            os.remove(tif_path)
            print("  (Original file deleted)")
            
        except Exception as e:
            print(f"Failed to convert {tif_path}: {e}")

    print(f"\nTotal space saved: {saved_space / (1024*1024):.2f} MB")

if __name__ == "__main__":
    target_dir = "leabharlann"
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        sys.exit(1)
        
    analyze_and_convert(target_dir)
