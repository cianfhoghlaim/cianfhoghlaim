import os
from PIL import Image
import sys

def convert_tif_to_png(directory):
    tif_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.tif', '.tiff')):
                tif_files.append(os.path.join(root, file))

    if not tif_files:
        print("No TIF files found.")
        return

    print(f"Found {len(tif_files)} TIF files.")
    
    total_original_size = 0
    total_new_size = 0

    for tif_path in tif_files:
        try:
            print(f"Processing: {tif_path}")
            original_size = os.path.getsize(tif_path)
            total_original_size += original_size
            
            # Open the TIF image
            with Image.open(tif_path) as img:
                # Construct the new filename
                base, _ = os.path.splitext(tif_path)
                png_path = base + ".png"
                
                # Convert and save as PNG
                # Convert to RGB if necessary (e.g. if it's CMYK or has alpha that acts weird)
                if img.mode in ('CMYK', 'P'):
                     img = img.convert('RGB')
                
                img.save(png_path, 'PNG', optimize=True)
                
                new_size = os.path.getsize(png_path)
                total_new_size += new_size
                
                print(f"  Converted to: {png_path}")
                print(f"  Original size: {original_size / 1024 / 1024:.2f} MB")
                print(f"  New size:      {new_size / 1024 / 1024:.2f} MB")
                
                # Optional: Delete the original file? 
                # For safety, I will NOT delete in this script, just report.
                # User can decide to delete later or we can add a flag.
                
        except Exception as e:
            print(f"  Error processing {tif_path}: {e}")

    print("-" * 30)
    print(f"Total Original Size: {total_original_size / 1024 / 1024:.2f} MB")
    print(f"Total New Size:      {total_new_size / 1024 / 1024:.2f} MB")
    print(f"Space Saved:         {(total_original_size - total_new_size) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    target_dir = "leabharlann"
    if not os.path.exists(target_dir):
        print(f"Directory '{target_dir}' not found.")
    else:
        convert_tif_to_png(target_dir)
