# TTS Dataset Generator

A powerful tool for generating high-quality text-to-speech (TTS) datasets from audio or video files. This utility automates the process of segmenting media files into optimal chunks and transcribing them accurately, saving hours of manual work.

## 🔍 Overview

This tool helps you:

1. **Segment** audio or video files into optimal chunks for TTS training
2. **Transcribe** those segments automatically using OpenAI's Whisper model
3. **Generate** a properly formatted dataset ready for TTS model training

Perfect for creating custom voice datasets, podcast transcription, lecture processing, and more.

## ✨ Features

- **Flexible audio segmentation** based on natural speech boundaries
- **High-quality transcription** using OpenAI's Whisper models
- **Handles both video and audio** files as input
- **Configurable parameters** for optimal segmentation
- **GPU acceleration** support for faster processing
- **Multi-language support** for transcription

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- ffmpeg (required for audio processing)

### Installation Steps

Requires the command-line tool ffmpeg to be installed on your system, which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

```bash
# Clone this repository
git clone https://github.com/gokhaneraslan/tts-dataset-generator.git
cd tts-dataset-generator

# Install dependencies
pip install -r requirements.txt
```

The main dependencies include:
- pydub (for audio processing)
- openai-whisper (for transcription)
- torch (for GPU acceleration, optional)
- moviepy (for video handling)
- natsort (for natural sorting, optional)

To choose the best model for your system, please visit for available models and required VRAM information.        
[OpenAI Whisper](https://github.com/openai/whisper)

## 📋 Usage

If you do not have enough equipment to choose the "large" whisper model, we recommend you to use google colab.

### Basic Usage

```bash
python main.py --file your_audio_or_video_file.mp4 --model large --language tr

# Or
python main.py --f your_audio_or_video_file.mp4 -m small -l tr
```

This will:
1. Process your file and segment it into chunks
2. Save the audio segments to `MyTTSDataset/wavs/`
3. Transcribe each segment
4. Generate a metadata file at `MyTTSDataset/metadata.csv`

### Advanced Options

```bash
python main.py \
  --file your_file.mp4 \
  --min-duration 3.0 \
  --max-duration 8.0 \
  --silence-threshold -35 \
  --min-silence-len 500 \
  --keep-silence 100 \
  --model medium \
  --language tr \
  --ljspeech True \
  --sample_rate 22050
```

### All Available Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--file` or `-f` | Input audio or video file path | (Required) |
| `--min-duration` | Minimum segment duration in seconds | 3.0 |
| `--max-duration` | Maximum segment duration in seconds | 10.0 |
| `--silence-threshold` | Audio level (dBFS) below which is considered silence | -40 |
| `--min-silence-len` | Minimum silence duration (ms) to mark a split point | 250 |
| `--keep-silence` | Padding silence (ms) to keep at segment boundaries | 150 |
| `--model` or `-m` | Whisper model size (tiny/base/small/medium/large) | large |
| `--language` or `-l` | Language code for transcription and number conversion | en |
| `--ljspeech` | Dataset format for coqui-ai/TTS formatter ljspeech | True |
| `--sample_rate` | Must be the same as the sampling rate of the sounds in the dataset | 22050 |
| `--log-level` | Set logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) | INFO |

## 🌐 Language Support

The tool supports multiple languages through the Whisper model. Some commonly used language codes:

- `tr` - Turkish
- `en` - English
- `fr` - French
- `de` - German
- `es` - Spanish
- `it` - Italian
- `ja` - Japanese
- `zh` - Chinese
- `ru` - Russian
- `pt` - Portuguese

Run the tool to see a complete list of supported language codes.

## 🔬 Technical Details

### Audio Segmentation Algorithm

The tool uses a sophisticated audio segmentation approach optimized for TTS dataset creation:

1. **Silence Detection**: 
   - Uses pydub's `split_on_silence` function which analyzes the audio waveform to identify natural pauses in speech
   - The `silence_thresh_dbfs` parameter (-40 dBFS by default) determines what volume level is considered silence
   - The `min_silence_len_ms` parameter (250ms by default) sets how long a silence must be to trigger a split

2. **Duration Constraints**:
   - Filters segments to ensure they're between `min_duration_s` and `max_duration_s` seconds
   - This is crucial for TTS training as too-short segments lack context, while too-long segments can cause training instability

3. **Natural Boundaries**:
   - Preserves a small amount of silence (`keep_silence_ms`) at the beginning/end of each segment
   - This creates natural-sounding pauses that improve TTS model prosody

4. **Padding**:
   - Adds consistent silence padding (250ms) to the end of each segment
   - This gives TTS models consistent end-of-utterance patterns to learn from

For optimal results:
- For clean studio recordings, use higher `silence_thresh_dbfs` values (-45 to -50)
- For recordings with background noise, use lower values (-30 to -35)
- For fast speech, reduce `min_silence_len_ms` to catch shorter pauses
- For slow, deliberate speech, increase `min_silence_len_ms`

### Transcription Engine

The transcription uses OpenAI's Whisper, a state-of-the-art speech recognition model:

- Supports multiple languages and accents
- Performs well even with background noise and varying audio quality
- Different model sizes balance accuracy vs. speed/resource requirements
- Automatically handles punctuation and capitalization

## 🔄 Integration with TTS Training Pipelines

This tool generates datasets compatible with most modern TTS frameworks. Here's how it fits into typical TTS training workflows:

### 1. Dataset Creation (This Tool)
- **Input**: Raw audio/video recordings of a voice talent
- **Process**: Segmentation → Transcription → Formatting
- **Output**: Segmented audio files + aligned transcripts

### 2. Dataset Preprocessing
- Load the generated dataset into your TTS system
- Most systems require:
  - Text normalization (lowercase, num2words, basic cleaning)
  - Audio feature extraction (mel spectrograms, etc.)
  - Text tokenization

### 3. Model Training
The generated dataset works seamlessly with:

- **Traditional TTS Models**:
  - Tacotron 2
  - FastSpeech/FastSpeech 2
  - Tacotron-DDC
  - Transformer-TTS

- **Modern Neural TTS Frameworks**:
  - 🔊 **VITS/VITS2**: Fully compatible with VITS training requirements
  - 🔊 **XTTS/Tortoise**: The output format is ready for fine-tuning
  - 🔊 **Coqui TTS**: Dataset directly works with Coqui's training scripts
  - 🔊 **ESPnet-TTS**: Compatible with minimal preprocessing
  - 🔊 **Mozilla TTS**: Ready for training without additional formatting

### Compatible Metadata Format

The generated `metadata.csv` follows the LJSpeech format widely used in TTS training:
--ljspeech True
```
segment_1|The quick brown fox jumps over the lazy dog.|The quick brown fox jumps over the lazy dog.
segment_2|She sells seashells by the seashore.|She sells seashells by the seashore.
```
--ljspeech False
```
wavs/segment_1.wav|The quick brown fox jumps over the lazy dog.
wavs/segment_2.wav|She sells seashells by the seashore.
```

This format is supported by most TTS frameworks out-of-the-box or with minimal adaptation.

### Integration Examples

For **Coqui TTS**:
```bash
# Train a Tacotron2 model using our generated dataset
tts train --config_path config.json --coqpit.datasets.0.path ./MyTTSDataset
```

For **VITS**:
```bash
# Modify VITS config to point to our dataset
sed -i 's|"training_files":.*|"training_files":"./MyTTSDataset/metadata.csv",|g' configs/vits.json
# Start training
python train.py -c configs/vits.json -m vits
```

## 🧪 Example Workflow

Let's walk through a complete example:

1. **Prepare a video file** of someone speaking clearly
2. **Run the tool** to process the file:

```bash
python main.py --file interview.mp4 --model medium --language en
```

3. **Examine the output**:
   - Audio segments are saved in `MyTTSDataset/wavs/`
   - Transcriptions are in `MyTTSDataset/metadata.csv`

4. **Format of ljspeech metadata.csv**:
  wav_filename|text|normalized_text or text
```
segment_1|Hello and welcome to our tutorial on text to speech.|Hello and welcome to our tutorial on text to speech.
segment_2|Today we'll learn how to create high quality voice datasets.|Today we'll learn how to create high quality voice datasets.
segment_3|The first step is to record clear audio samples.|The first step is to record clear audio samples.
```

5. **Format of metadata.csv**:
  wav_filename|text
```
wavs/segment_1.wav|Hello and welcome to our tutorial on text to speech.
wavs/segment_2.wav|Today we'll learn how to create high quality voice datasets.
wavs/segment_3.wav|The first step is to record clear audio samples.
```

6. **Use the dataset** for training TTS models like Tacotron, VITS, F5-TTS, piper or other custom voice systems

## 🚀 Performance Tips

- For faster transcription, use a machine with a CUDA-compatible GPU
- For better transcription accuracy, use the `large` model (requires more RAM/VRAM)
- For faster processing but less accuracy, use the `small` or `base` models
- Adjust the `silence-threshold` parameter if your audio has background noise

## 🔧 Dataset Quality Recommendations

For optimal TTS training results:

1. **Recording Quality**:
   - Use a high-quality microphone in a quiet environment
   - Maintain consistent audio levels and microphone distance
   - Sample rate of 22050Hz or 44100Hz is recommended

2. **Speech Characteristics**:
   - Clear, consistent speaking style
   - Natural but not overly dramatic prosody
   - Consistent speaking pace

3. **Dataset Composition**:
   - Aim for 30+ minutes of clean audio for basic voice cloning
   - 1-2 hours for high-quality results
   - 5+ hours for production-grade TTS systems
   - Include diverse phonetic coverage (pangrams, digit sequences, etc.)


## 🙏 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for the transcription model
- [pydub](https://github.com/jiaaro/pydub) for audio processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
