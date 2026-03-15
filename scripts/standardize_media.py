import os
import subprocess
import sys
import json

# Configuration
TARGET_DIR = "leabharlann"
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg', '.wma'}

# Standard Formats
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_ONLY_CODEC = "libmp3lame"
VIDEO_CONTAINER = ".mp4"
AUDIO_CONTAINER = ".mp3"

def get_media_files(directory):
    media_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in VIDEO_EXTENSIONS or ext in AUDIO_EXTENSIONS:
                media_files.append(os.path.join(root, file))
    return media_files

def convert_media(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    is_video = ext in VIDEO_EXTENSIONS
    
    if is_video:
        output_ext = VIDEO_CONTAINER
        target_file = os.path.splitext(file_path)[0] + "_std" + output_ext
        
        print(f"Converting Video: {file_path} -> {target_file}")
        
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-c:v", VIDEO_CODEC,
            "-crf", "23",
            "-preset", "medium",
            "-c:a", AUDIO_CODEC,
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-y",
            target_file
        ]
    else:
        output_ext = AUDIO_CONTAINER
        target_file = os.path.splitext(file_path)[0] + "_std" + output_ext
        
        print(f"Converting Audio: {file_path} -> {target_file}")
        
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-c:a", AUDIO_ONLY_CODEC,
            "-q:a", "2",
            "-y",
            target_file
        ]
        
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        original_size = os.path.getsize(file_path)
        new_size = os.path.getsize(target_file)
        
        print(f"  Success!")
        print(f"  Original: {original_size / 1024 / 1024:.2f} MB")
        print(f"  New:      {new_size / 1024 / 1024:.2f} MB")
        
        if new_size < original_size:
            print(f"  Saved:    {(original_size - new_size) / 1024 / 1024:.2f} MB")
        else:
            print(f"  Note: New file is larger. This can happen with already compressed files.")

    except subprocess.CalledProcessError as e:
        print(f"  Error converting {file_path}: {e.stderr.decode()}")

def main():
    print(f"Scanning {TARGET_DIR} for media files...")
    files = get_media_files(TARGET_DIR)
    
    if not files:
        print("No media files found.")
        return

    print(f"Found {len(files)} media files.")
    
    for file in files:
        convert_media(file)

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        print(f"Directory '{TARGET_DIR}' not found.")
    else:
        main()
