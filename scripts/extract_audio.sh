#!/bin/bash

# Script to separate/extract audio from a video file (e.g., QuickTime .mov) using FFmpeg

if [ -z "$1" ]; then
  echo "Usage: $0 <input_video_file> [output_audio_file]"
  echo "Example: $0 my_video.mov"
  echo "Example: $0 my_video.mov output_audio.mp3"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# If no output file is provided, use the input filename with a .mp3 extension
if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="${INPUT_FILE%.*}.mp3"
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed or not in PATH."
    echo "You can install it using: brew install ffmpeg"
    exit 1
fi

echo "Extracting audio from '$INPUT_FILE' to '$OUTPUT_FILE'..."

# -i: input file
# -vn: no video
# -q:a 0: variable bit rate audio (highest quality)
# -map a: map only audio streams
ffmpeg -i "$INPUT_FILE" -vn -q:a 0 -map a "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
  echo "Successfully extracted audio to $OUTPUT_FILE"
else
  echo "Error occurred during audio extraction."
  exit 1
fi
