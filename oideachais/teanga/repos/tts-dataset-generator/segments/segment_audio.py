import os
import sys
import logging
from pydub import AudioSegment
from pydub.silence import split_on_silence
from moviepy import VideoFileClip, AudioFileClip
import torchaudio
import traceback
import ffmpeg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tts_dataset_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tts_dataset_generator")




def extract_audio_ffmpeg_py(video_path, audio_path, sample_rate = 22050):
    """
    Extracts audio from a video file and saves it as a mono, 16-bit PCM WAV
    at 22050 Hz using ffmpeg-python.

    Args:
        video_path (str): Path to the input video file.
        audio_path (str): Path to save the output WAV audio file.
    """
    print(f"Processing '{video_path}' with ffmpeg-python...")
    try:
        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at '{video_path}'")
            return

        print(f"Extracting audio to '{audio_path}'...")
        print("Parameters: Mono, 22050 Hz, 16-bit PCM (WAV)")

        # Ensure the output filename ends with .wav for clarity
        # Although ffmpeg usually infers format, being explicit is good.
        if not audio_path.lower().endswith('.wav'):
             print("Warning: Output file does not end with .wav. Forcing WAV format.")
             # audio_path += ".wav" # Or rely on format spec below

        # Build the ffmpeg command pipeline
        stream = ffmpeg.input(video_path)

        # Select only the audio stream and apply filters/encoding options
        stream = ffmpeg.output(
            stream.audio,             # Use only the audio part of the input
            audio_path,
            acodec='pcm_s16le',       # Audio codec: 16-bit signed little-endian PCM
            ac=1,                     # Audio channels: 1 (mono)
            ar=str(sample_rate),               # Audio sample rate: 22050 Hz
            format='wav'            # Explicitly set format (optional if extension is .wav)
        )

        # Run the command, overwriting output file if it exists (-y flag)
        # Capture stdout/stderr for potential debugging
        stdout, stderr = ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        print("-" * 20)
        print("Audio extraction successful!")
        print(f"Output saved to: {audio_path}")
        print("-" * 20)

    except ffmpeg.Error as e:
        print('FFmpeg execution failed!', file=sys.stderr)
        print('stdout:', stdout.decode('utf8', errors='ignore'), file=sys.stderr)
        print('stderr:', stderr.decode('utf8', errors='ignore'), file=sys.stderr)
        print(f"An ffmpeg error occurred: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)



def segment_audio_flexible(input_path, output_dir, sample_rate= 22050,
                           min_duration_s=3.0, max_duration_s=10.0,
                           silence_thresh_dbfs=-40, min_silence_len_ms=250,
                           keep_silence_ms=150,
                           temp_audio_filename="_temp_extracted_audio.wav"):
    """
    Segments an audio or video file into clips of flexible duration (min_duration_s to max_duration_s),
    prioritizing natural speech boundaries based on silence.

    If the input is a video, audio is extracted first.

    Args:
        input_path (str): Path to the input audio or video file.
        output_dir (str): Directory where the segmented WAV files will be saved.
        min_duration_s (float): Minimum desired length of a segment in seconds.
        max_duration_s (float): Maximum desired length of a segment in seconds.
        silence_thresh_dbfs (int): Audio level below which is considered silence (dBFS).
                                   Adjust based on your recording's noise floor.
        min_silence_len_ms (int): Minimum duration of silence (in ms) to mark a split point.
                                  Adjust based on pauses between sentences/phrases.
        keep_silence_ms (int): Amount of original silence (in ms) to keep at the
                               beginning/end of each chunk for natural padding.
        temp_audio_filename (str): Filename for temporarily storing extracted audio.
    """
    logger.info(f"Processing input file: {input_path}")

    # --- Input Validation and Audio Extraction ---
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return False

    audio_path_to_process = None
    is_temporary_audio = False

    # Determine file type and handle video
    file_extension = os.path.splitext(input_path)[1].lower()
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']  # Add more if needed

    if file_extension in video_extensions:
        logger.info("Input is a video file. Extracting audio...")
        try:
            video = VideoFileClip(input_path)
            # Use the provided temp filename in the same dir as the script for simplicity
            audio_path_to_process = temp_audio_filename
            video.audio.write_audiofile(
                audio_path_to_process,
                fps=sample_rate,          # Sample rate
                nbytes=2,           # Bytes per sample (2 for 16-bit)
                codec='pcm_s16le',  # PCM signed 16-bit little-endian codec
                ffmpeg_params=["-ac", "1"] # Force mono audio (1 channel)
            )
            video.close()  # Release video file handle
            is_temporary_audio = True
            logger.info(f"Audio extracted successfully to: {audio_path_to_process}")
        except Exception as e:
            logger.error(f"Failed to extract audio from video: {e}")
            logger.debug(traceback.format_exc())
            if os.path.exists(temp_audio_filename):  # Clean up partial file if it exists
                os.remove(temp_audio_filename)
            return False
    else:
        # Assume it's an audio file pydub can handle
        audio = AudioFileClip(input_path)
        audio_path_to_process = temp_audio_filename
        audio.write_audiofile(
            audio_path_to_process,
            fps=sample_rate,          # Sample rate
            nbytes=2,           # Bytes per sample (2 for 16-bit)
            codec='pcm_s16le',  # PCM signed 16-bit little-endian codec
            ffmpeg_params=["-ac", "1"] # Force mono audio (1 channel)
        )
        logger.info("Input is assumed to be an audio file.")

    metadata = torchaudio.info(audio_path_to_process)
    print("Audio information: ", metadata)

    # --- Audio Processing ---
    try:
        # Load the audio (either original or extracted)
        logger.info(f"Loading audio from: {audio_path_to_process}")
        try:
            # Attempt loading (pydub uses ffmpeg/libav)
            audio = AudioSegment.from_file(audio_path_to_process)
            logger.info(f"Audio loaded successfully. Duration: {len(audio) / 1000:.2f} seconds")
        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            logger.error("Ensure the file is a valid audio format supported by pydub/ffmpeg.")
            logger.error("Also ensure 'ffmpeg' or 'libav' is installed and accessible.")
            logger.debug(traceback.format_exc())
            return False

        # Create the output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        logger.info(f"Splitting audio based on silence...")
        logger.info(f"  Parameters:")
        logger.info(f"    Min Silence Duration: {min_silence_len_ms} ms")
        logger.info(f"    Silence Threshold: {silence_thresh_dbfs} dBFS")
        logger.info(f"    Padding Silence: {keep_silence_ms} ms")

        # Split audio based on silence
        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len_ms,
            silence_thresh=silence_thresh_dbfs,
            keep_silence=keep_silence_ms
        )

        if not chunks:
            logger.warning("No segments found based on silence detection.")
            logger.warning("Consider adjusting 'silence_thresh_dbfs' or 'min_silence_len_ms'.")
            return False

        logger.info(f"Found {len(chunks)} potential segments based on silence.")
        logger.info(f"Filtering segments by duration ({min_duration_s:.1f}s - {max_duration_s:.1f}s)...")

        saved_count = 0
        skipped_too_short = 0
        skipped_too_long = 0

        # Filter and save the chunks
        for i, chunk in enumerate(chunks):
            chunk_duration_s = len(chunk) / 1000.0

            # Check duration
            if chunk_duration_s < min_duration_s:
                skipped_too_short += 1
                continue
            if chunk_duration_s > max_duration_s:
                skipped_too_long += 1
                continue

            padding_needed = 250
            silence = AudioSegment.silent(duration=padding_needed)
            final_segment = chunk + silence

            # Save the valid segment
            saved_count += 1
            output_filename = f"segment_{saved_count}.wav"  # Use a different prefix
            output_path = os.path.join(output_dir, output_filename)
            logger.debug(f"  Segment {saved_count} added {padding_needed/1000:.2f}s silence")
            logger.info(f"  Saving segment {saved_count} ({chunk_duration_s + (padding_needed/1000):.2f}s): {output_path}")
            try:
                # Export chunk as WAV file (standard format for TTS)
                final_segment.export(output_path, format="wav")
            except Exception as e:
                logger.error(f"Failed to save segment ({output_path}): {e}")
                logger.debug(traceback.format_exc())

        logger.info("\nProcessing Complete!")
        logger.info(f"  Saved {saved_count} segments.")
        logger.info(f"  Skipped {skipped_too_short} segments (duration < {min_duration_s:.1f}s).")
        logger.info(f"  Skipped {skipped_too_long} segments (duration > {max_duration_s:.1f}s).")
        
        return saved_count > 0  # Return True if we saved any segments

    except Exception as e:
        logger.error(f"Error during audio segmentation: {e}")
        logger.debug(traceback.format_exc())
        return False
    finally:
        # --- Cleanup ---
        if is_temporary_audio and os.path.exists(audio_path_to_process):
            logger.info(f"Cleaning up temporary audio file: {audio_path_to_process}")
            try:
                os.remove(audio_path_to_process)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {audio_path_to_process}: {e}")

