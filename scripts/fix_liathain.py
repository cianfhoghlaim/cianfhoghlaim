import os

def fix_mac_liathain(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for filename in filenames:
            if "mac_liath_in" in filename:
                old_path = os.path.join(dirpath, filename)
                new_filename = filename.replace("mac_liath_in", "mac_liathain")
                new_path = os.path.join(dirpath, new_filename)
                print(f"Renaming '{old_path}' -> '{new_path}'")
                os.rename(old_path, new_path)

if __name__ == "__main__":
    target_dirs = [
        "bunchloch/mata/applied_statistics_1/applied_statistics_report"
    ]
    
    base_path = "/Users/cliste/dev/cianfhoghlaim"
    for d in target_dirs:
        full_path = os.path.join(base_path, d)
        if os.path.exists(full_path):
            fix_mac_liathain(full_path)
