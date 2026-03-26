import os
import re

def to_snake_case(name):
    # Separate extension
    name_parts = name.rsplit('.', 1)
    base_name = name_parts[0]
    ext = '.' + name_parts[1] if len(name_parts) > 1 else ''

    # Remove invalid characters, replace with space
    base_name = re.sub(r'[^a-zA-Z0-9]', ' ', base_name)
    
    # Insert space before capital letters if not preceded by a space or another capital letter
    # and if followed by a lowercase letter
    base_name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', base_name)
    base_name = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', base_name)

    # Convert to lowercase and split by whitespace/underscores/hyphens
    words = re.split(r'\s+', base_name.strip().lower())
    
    # Filter out empty strings
    words = [w for w in words if w]
    
    snake_name = '_'.join(words) + ext
    return snake_name

if __name__ == "__main__":
    files_to_rename = [
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Sinn Féin History and Funding Inquiry.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Sinn Féin Data, Funding, and Foreign Influence.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Royal Family, Kneecap, and Irish Cities.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Kneecap_ Deep Dive Investigation.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Kneecap Band Business and Youth Concerns.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Fine Gael Coalition Strategy Analysis.pdf",
        "/Users/cliste/dev/cianfhoghlaim/gemini/instagram_output/Farrell, Sinn Féin, and United Ireland Rhetoric.pdf"
    ]
    
    for old_path in files_to_rename:
        if os.path.exists(old_path):
            dirpath = os.path.dirname(old_path)
            filename = os.path.basename(old_path)
            
            new_filename = to_snake_case(filename)
            new_path = os.path.join(dirpath, new_filename)
            
            if old_path != new_path:
                print(f"Renaming file: '{old_path}' -> '{new_path}'")
                os.rename(old_path, new_path)
        else:
            print(f"File not found: {old_path}")
