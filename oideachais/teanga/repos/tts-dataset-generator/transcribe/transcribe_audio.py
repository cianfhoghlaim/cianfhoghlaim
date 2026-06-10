import os
import sys
import time
import logging
import traceback
from natsort import natsorted
import whisper
import torch


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

if torch.cuda.is_available():
    GPU_AVAILABLE = True
else:
    GPU_AVAILABLE = False



def transcribe_audio_files(audio_dir,
                           output_csv_path="metadata.csv",
                           ljspeech=False,
                           model_name="large",
                           language_="en"):
    """
    Transcribes all .wav files in a directory using OpenAI's Whisper model
    and saves the results to a CSV file.

    Args:
        audio_dir (str): Path to the directory containing the .wav audio segments.
        output_csv_path (str): Path where the output metadata CSV file will be saved.
        model_name (str): Name of the Whisper model to use
                          (e.g., "tiny", "base", "small", "medium", "large").
                          Larger models are more accurate but slower and require more VRAM/RAM.
        language_ (str): Language code for transcription.
        
    Returns:
        bool: True if transcription was successful, False otherwise
    """
    logger.info(f"Looking for .wav files in: {audio_dir}")

    if not os.path.isdir(audio_dir):
        logger.error(f"Directory not found: {audio_dir}")
        return False

    # Find all .wav files and sort them naturally
    try:
        wav_files = natsorted([f for f in os.listdir(audio_dir) if f.lower().endswith('.wav')])
    except Exception as e:
        logger.error(f"Error accessing audio directory: {e}")
        logger.debug(traceback.format_exc())
        return False

    if not wav_files:
        logger.error(f"No .wav files found in {audio_dir}")
        return False

    logger.info(f"Found {len(wav_files)} .wav files to transcribe.")

    # --- Load Whisper Model ---
    logger.info(f"Loading Whisper model: '{model_name}'...")
    if GPU_AVAILABLE:
        logger.info("CUDA (GPU) available. Whisper will run on GPU.")
        device = "cuda"
    else:
        logger.info("CUDA (GPU) not available. Whisper will run on CPU (this might be slow).")
        device = "cpu"

    try:
        model = whisper.load_model(model_name, device=device)
        logger.info(f"Whisper model '{model_name}' loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Whisper model '{model_name}'.")
        logger.error(f"Ensure the model name is correct and you have enough memory/VRAM.")
        logger.error(f"Error details: {e}")
        logger.critical("")
        logger.critical("")
        logger.critical("")
        logger.critical(f"Try --model small or you can use colab for enough memory/VRAM.")
        logger.critical("")
        logger.debug(traceback.format_exc())
        return False

    # --- Transcription Process ---
    metadata_text = []
    metadata_audio_path = []
    total_files = len(wav_files)
    start_time_total = time.time()

    # Process each audio file
    for i, filename in enumerate(wav_files):
        file_path = os.path.join(audio_dir, filename)
        logger.info(f"Processing file {i+1}/{total_files}: {filename}...")
        start_time_file = time.time()

        text = ""  # Default to empty string in case of errors

        try:
            # Transcribe audio using Whisper
            result = model.transcribe(file_path, language=language_)
            text = result["text"].strip()  # Get the transcribed text and strip whitespace
            end_time_file = time.time()
            print(f"Done ({end_time_file - start_time_file:.2f}s). Transcription: '{text}'")

        except Exception as e:
            # Catch potential errors during transcription
            text = f"[WHISPER_ERROR]"
            end_time_file = time.time()
            logger.error(f"Error transcribing {filename} after {end_time_file - start_time_file:.2f}s. Details: {e}")
            logger.debug(traceback.format_exc())

        # Store the result (filename without path, transcription)
        metadata_text.append(text)
        metadata_audio_path.append(filename[:-4])

    end_time_total = time.time()
    logger.info(f"Finished processing all files in {end_time_total - start_time_total:.2f} seconds.")

    if ljspeech:
        # --- Write CSV Output ---
        logger.info(f"Writing ljspeech format transcriptions to: {output_csv_path}")
        try:
            with open(output_csv_path, 'w', encoding='utf-8') as f:
                for i in range(len(metadata_audio_path)):
                    f.writelines(f'{metadata_audio_path[i]}|{metadata_text[i]}|{metadata_text[i]}\n')

            logger.info("Metadata CSV file created successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to write CSV file: {e}")
            logger.debug(traceback.format_exc())
            return False

    else:
    
        # --- Write CSV Output ---
        logger.info(f"Writing transcriptions to: {output_csv_path}")
        try:
            with open(output_csv_path, 'w', encoding='utf-8') as f:
                for i in range(len(metadata_audio_path)):
                    f.writelines(f'waws/{metadata_audio_path[i]}.wav|{metadata_text[i]}\n')

            logger.info("Metadata CSV file created successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to write CSV file: {e}")
            logger.debug(traceback.format_exc())
            return False
