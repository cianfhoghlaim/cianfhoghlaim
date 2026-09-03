import os
import shutil
import filecmp

def merge_directories(src_dir, dest_dir):
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isdir(src_path):
            if not os.path.exists(dest_path):
                print(f"Moving directory {src_path} -> {dest_path}")
                shutil.move(src_path, dest_path)
            else:
                print(f"Merging directory {src_path} into {dest_path}")
                merge_directories(src_path, dest_path)
        else:
            if not os.path.exists(dest_path):
                print(f"Moving file {src_path} -> {dest_path}")
                shutil.move(src_path, dest_path)
            else:
                if filecmp.cmp(src_path, dest_path, shallow=False):
                    print(f"Files are identical, removing source {src_path}")
                    os.remove(src_path)
                else:
                    print(f"CONFLICT: Files differ: {src_path} and {dest_path}")
                    # You might want to handle this manually, e.g., by renaming
                    # For now, let's keep both
                    base, ext = os.path.splitext(item)
                    new_dest_path = os.path.join(dest_dir, f"{base}_from_education{ext}")
                    print(f"Moving conflicting file {src_path} -> {new_dest_path}")
                    shutil.move(src_path, new_dest_path)

if __name__ == "__main__":
    src_dir = "education"
    dest_dir = "."
    merge_directories(src_dir, dest_dir)
