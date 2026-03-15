import os
import re
import shutil
import logging
from pathlib import Path
from PIL import Image
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = 'leabharlann/bunchloch'
MODULES_FILE = os.path.join(BASE_DIR, 'University-of-Galway-Modules.md')

def parse_modules(file_path):
    """Parses the markdown file to extract module codes and names."""
    modules = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Matches: ### [CODE] - [NAME]
        pattern = re.compile(r'###\s+([A-Z0-9]+)\s+-\s+(.+)')
        
        for match in pattern.finditer(content):
            code = match.group(1).strip()
            name = match.group(2).strip()
            modules[code] = name
            
    except FileNotFoundError:
        logging.error(f"Modules file not found at {file_path}")
        return {}
    
    return modules

def to_snake_case(text):
    """Converts a string to snake_case, ensuring ASCII only."""
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-alphanumeric characters (except spaces/hyphens)
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and hyphens with underscores
    text = re.sub(r'[\s-]+', '_', text)
    # Convert to lowercase and strip leading/trailing underscores
    return text.lower().strip('_')

def convert_tif_to_png(file_path):
    """Converts a TIF file to PNG and deletes the original."""
    try:
        path_obj = Path(file_path)
        if path_obj.suffix.lower() not in ['.tif', '.tiff']:
            return False

        png_path = path_obj.with_suffix('.png')
        
        with Image.open(path_obj) as img:
            img.save(png_path, 'PNG', optimize=True)
            
        logging.info(f"Converted TIF to PNG: {png_path}")
        os.remove(file_path)
        return True
    except Exception as e:
        logging.error(f"Failed to convert {file_path}: {e}")
        return False

def rename_item(path, new_name):
    """Renames a file or directory."""
    directory = os.path.dirname(path)
    new_path = os.path.join(directory, new_name)
    
    if path != new_path:
        try:
            os.rename(path, new_path)
            logging.info(f"Renamed: {path} -> {new_path}")
            return new_path
        except OSError as e:
            logging.error(f"Error renaming {path} to {new_path}: {e}")
            return path
    return path

def process_directory_contents(directory):
    """Recursively renames files and subdirectories to snake_case and converts TIFs."""
    for root, dirs, files in os.walk(directory, topdown=False):
        # Rename files and convert TIFs
        for filename in files:
            if filename.startswith('.'):
                continue
                
            old_path = os.path.join(root, filename)
            
            # 1. Convert TIF if needed (before renaming to keep logic simple, or after?)
            # Let's do conversion first if it's a tif
            if filename.lower().endswith(('.tif', '.tiff')):
                if convert_tif_to_png(old_path):
                    # If converted, the old file is gone, and we have a new .png file
                    # We should process the new .png file for renaming in the next pass or manually now.
                    # Simplified: just update filename to match the new png
                    filename = Path(filename).with_suffix('.png').name
                    old_path = os.path.join(root, filename)

            # 2. Rename to snake_case
            name, ext = os.path.splitext(filename)
            new_filename = to_snake_case(name) + ext.lower()
            rename_item(old_path, new_filename)

        # Rename directories
        for dirname in dirs:
            old_path = os.path.join(root, dirname)
            new_dirname = to_snake_case(dirname)
            rename_item(old_path, new_dirname)

def reorganize_structure(modules):
    """Reorganizes the directory structure based on modules."""
    
    # Manual mapping for directories
    mapping = {
        'Applied Statistics 1': 'ST311',
        'Applied Statistics 2': 'ST312',
        'Modelling 2': 'MP307',
        'Non-Linear Systems': 'MP491',
        'Numerical Analysis 2': 'MA378',
        'Networks': 'CS4423',
    }

    if not os.path.exists(BASE_DIR):
        logging.error(f"Base directory {BASE_DIR} does not exist.")
        return

    # Iterate through top-level directories in BASE_DIR (categories)
    for category in os.listdir(BASE_DIR):
        category_path = os.path.join(BASE_DIR, category)
        if not os.path.isdir(category_path) or category.startswith('.'):
            continue
            
        logging.info(f"Processing category: {category}")
        
        # We need to list dir contents first
        items = [i for i in os.listdir(category_path) if not i.startswith('.')]
        
        for item in items:
            item_path = os.path.join(category_path, item)
            if not os.path.isdir(item_path):
                # If it's a file in the category root (like in oideachas/), just rename/convert it
                if item_path.lower().endswith(('.tif', '.tiff')):
                    convert_tif_to_png(item_path)
                    item = Path(item).with_suffix('.png').name
                    item_path = os.path.join(category_path, item)
                
                name, ext = os.path.splitext(item)
                new_filename = to_snake_case(name) + ext.lower()
                rename_item(item_path, new_filename)
                continue
                
            # It is a directory (potential module)
            module_code = None
            module_name = None
            
            # 1. Check explicit mapping
            if item in mapping:
                module_code = mapping[item]
                if module_code in modules:
                    module_name = modules[module_code]
            
            # 2. Check regex match for "CODE - Name" pattern or existing snake_case with code
            if not module_code:
                # Try "CT511 - Databases" format
                match = re.match(r'^([A-Z0-9]+)\s*-\s*(.+)', item)
                if match:
                    code_candidate = match.group(1)
                    if code_candidate in modules:
                        module_code = code_candidate
                        module_name = modules[module_code]
                    else:
                        module_code = code_candidate
                        module_name = match.group(2)
                
                # Try "ct511_databases" format (already processed?)
                # If it starts with a known module code
                else:
                    parts = item.split('_')
                    if parts[0].upper() in modules:
                        module_code = parts[0].upper()
                        module_name = modules[module_code]

            # Construct new directory name
            if module_code and module_name:
                new_dir_name = to_snake_case(f"{module_code}_{module_name}")
            else:
                new_dir_name = to_snake_case(item)
            
            new_dir_path = os.path.join(category_path, new_dir_name)
            
            # Move/Rename the module directory
            final_path = item_path
            if item_path != new_dir_path:
                logging.info(f"Renaming module directory: {item} -> {new_dir_name}")
                try:
                    os.rename(item_path, new_dir_path)
                    final_path = new_dir_path
                except Exception as e:
                    logging.error(f"Error renaming {item_path} to {new_dir_path}: {e}")
                    # If rename failed (e.g. target exists), maybe merge? 
                    # For now, just continue with original path if rename failed, or skip?
                    # If we can't rename, we should probably still process contents of the original path
                    pass
            
            # Recursively rename contents of the module directory
            process_directory_contents(final_path)

if __name__ == "__main__":
    logging.info("Starting reorganization and conversion...")
    modules_data = parse_modules(MODULES_FILE)
    logging.info(f"Loaded {len(modules_data)} modules from markdown.")
    reorganize_structure(modules_data)
    logging.info("Reorganization complete.")
