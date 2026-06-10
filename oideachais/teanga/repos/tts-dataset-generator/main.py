import sys
import argparse
import logging
import traceback
from segments.segment_audio import segment_audio_flexible
from transcribe.transcribe_audio import transcribe_audio_files

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



def setup_argparse():
    """
    Set up command-line argument parsing.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Audio/Video Processor for TTS Dataset Creation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--file', '-f', type=str, required=True, 
                              help="Input audio or video file path")
    parser.add_argument("--min-duration", type=float, default=3.0,
                              help="Minimum segment duration in seconds")
    parser.add_argument("--max-duration", type=float, default=10.0,
                              help="Maximum segment duration in seconds")
    parser.add_argument("--silence-threshold", type=int, default=-40,
                              help="Audio level (dBFS) below which is considered silence")
    parser.add_argument("--min-silence-len", type=int, default=250,
                              help="Minimum silence duration (ms) to mark a split point")
    parser.add_argument("--keep-silence", type=int, default=150,
                              help="Padding silence (ms) to keep at segment boundaries")
    parser.add_argument("--model", '-m', type=str, default="large",
                              choices=["tiny", "base", "small", "medium", "large"],
                              help="Whisper model size (larger = more accurate but slower)")
    parser.add_argument("--language", "-l", type=str, default="en",
                              help="Language code for transcription and number conversion")
    parser.add_argument("--ljspeech", type=bool, default=True,
                              help="Dataset format for coqui-ai/TTS")
    parser.add_argument("--sample_rate", type=int, default=22050,
                              help="Must be the same as the sampling rate of the sounds in the dataset")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                              default="INFO", help="Set logging level")
    

    return parser.parse_args()



def main():
    
    """
    Main function that runs the audio segmentation and transcription process
    """
    
    args = setup_argparse()
    
    # Update logging level based on arguments
    if hasattr(args, 'log_level'):
        logger.setLevel(getattr(logging, args.log_level))
        
    # Display banner
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║        Audio/Video Segmentation & Transcription Tool       ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("Running in PROCESS")
    logger.info("Running with default configuration")
    logger.info(f"Input file: {args.file}")
    logger.info(f"Language: {args.language}")
    logger.info(f"Whisper model: {args.model}")
    
    # First segment
    result = segment_audio_flexible(
        input_path=args.file,
        output_dir="MyTTSDataset/wavs",
        sample_rate=args.sample_rate,
        min_duration_s=args.min_duration,
        max_duration_s=args.max_duration,
        silence_thresh_dbfs=args.silence_threshold,
        min_silence_len_ms=args.min_silence_len,
        keep_silence_ms=args.keep_silence
    )
    
    if not result:
        logger.error("Segmentation failed. Stopping process.")
        sys.exit(1)
            
        # Then transcribe
    result = transcribe_audio_files(
        audio_dir="MyTTSDataset/wavs",
        output_csv_path= "MyTTSDataset/metadata.csv",
        ljspeech=args.ljspeech
        model_name=args.model,
        language_=args.language
    )
    
    if not result:
        logger.error("Transcription failed.")
        sys.exit(1)
        
    # Print some help information
    logger.info("\n--- IMPORTANT NOTES ---")
    logger.info("- Review the generated CSV file for accuracy.")
    logger.info(f"- Larger Whisper models generally yield better results but are slower.")
    logger.info("- Transcription speed depends heavily on your hardware (GPU highly recommended).")
    logger.info("- Check audio_processor.log for detailed processing information.")
    
    logger.info("\nProcess completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
