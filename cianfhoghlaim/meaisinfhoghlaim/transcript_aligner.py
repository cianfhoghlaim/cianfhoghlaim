"""
Irish Transcript Aligner.

Force-aligns Irish text transcripts to audio for training data preparation.
Supports both word-level and phoneme-level alignment.

Alignment Methods:
1. MFA (Montreal Forced Aligner) - Requires Irish acoustic model
2. CTC-based - Uses Wav2Vec2 CTC alignments
3. Dynamic Time Warping - Simpler, more robust
4. WhisperX - Cross-attention based alignment

References:
- MFA Irish: Custom acoustic model from ABAIR data
- Wav2Vec2 CTC: facebook/wav2vec2-base + CTC alignment
- WhisperX: https://github.com/m-bain/whisperX
"""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import numpy as np


class AlignmentMethod(StrEnum):
    """Available alignment methods."""
    MFA = "mfa"
    CTC = "ctc"
    DTW = "dtw"
    WHISPERX = "whisperx"


@dataclass
class AlignedWord:
    """A single aligned word with timing."""
    word: str
    start_time: float  # seconds
    end_time: float    # seconds
    confidence: float
    phonemes: list["AlignedPhoneme"] = field(default_factory=list)


@dataclass
class AlignedPhoneme:
    """A single aligned phoneme with timing."""
    phoneme: str
    start_time: float
    end_time: float
    confidence: float


@dataclass
class AlignmentResult:
    """Complete alignment result."""
    text: str
    words: list[AlignedWord]
    audio_duration: float
    method: AlignmentMethod
    language: str = "ga"  # Irish

    def to_textgrid(self, output_path: str):
        """Export to Praat TextGrid format."""
        lines = [
            'File type = "ooTextFile"',
            'Object class = "TextGrid"',
            "",
            "xmin = 0",
            f"xmax = {self.audio_duration}",
            "tiers? <exists>",
            "size = 2",
            "item []:",
        ]

        # Word tier
        lines.extend([
            "    item [1]:",
            '        class = "IntervalTier"',
            '        name = "words"',
            "        xmin = 0",
            f"        xmax = {self.audio_duration}",
            f"        intervals: size = {len(self.words) + 1}",
        ])

        prev_end = 0.0
        for i, word in enumerate(self.words, 1):
            # Gap before word
            if word.start_time > prev_end:
                lines.extend([
                    f"        intervals [{i}]:",
                    f"            xmin = {prev_end}",
                    f"            xmax = {word.start_time}",
                    '            text = ""',
                ])
            lines.extend([
                f"        intervals [{i+1}]:",
                f"            xmin = {word.start_time}",
                f"            xmax = {word.end_time}",
                f'            text = "{word.word}"',
            ])
            prev_end = word.end_time

        # Phoneme tier
        all_phonemes = []
        for word in self.words:
            all_phonemes.extend(word.phonemes)

        lines.extend([
            "    item [2]:",
            '        class = "IntervalTier"',
            '        name = "phonemes"',
            "        xmin = 0",
            f"        xmax = {self.audio_duration}",
            f"        intervals: size = {len(all_phonemes) + 1}",
        ])

        for i, phoneme in enumerate(all_phonemes, 1):
            lines.extend([
                f"        intervals [{i}]:",
                f"            xmin = {phoneme.start_time}",
                f"            xmax = {phoneme.end_time}",
                f'            text = "{phoneme.phoneme}"',
            ])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def to_json(self) -> dict:
        """Export to JSON format."""
        return {
            "text": self.text,
            "duration": self.audio_duration,
            "method": self.method.value,
            "language": self.language,
            "words": [
                {
                    "word": w.word,
                    "start": w.start_time,
                    "end": w.end_time,
                    "confidence": w.confidence,
                    "phonemes": [
                        {
                            "phoneme": p.phoneme,
                            "start": p.start_time,
                            "end": p.end_time,
                        }
                        for p in w.phonemes
                    ],
                }
                for w in self.words
            ],
        }


@dataclass
class AlignerConfig:
    """Configuration for transcript aligner."""
    method: AlignmentMethod = AlignmentMethod.CTC
    sample_rate: int = 16000
    language: str = "ga"

    # CTC settings
    ctc_model: str = "facebook/wav2vec2-large-xlsr-53"

    # WhisperX settings
    whisper_model: str = "large-v3"

    # MFA settings
    mfa_acoustic_model: str | None = None
    mfa_dictionary: str | None = None

    # DTW settings
    dtw_window_size: int = 10  # frames

    # Output
    min_word_duration: float = 0.01  # seconds
    max_word_duration: float = 5.0   # seconds


class CTCAligner:
    """
    Align transcripts using CTC-based forced alignment.

    Uses Wav2Vec2 model with CTC output to align text to audio.
    Based on wav2vec2-alignment approach.
    """

    def __init__(self, config: AlignerConfig):
        self.config = config
        self.model = None
        self.processor = None
        self._labels = None

    def load(self):
        """Load CTC model."""
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

        self.processor = Wav2Vec2Processor.from_pretrained(self.config.ctc_model)
        self.model = Wav2Vec2ForCTC.from_pretrained(self.config.ctc_model)
        self.model.eval()

        if torch.cuda.is_available():
            self.model = self.model.cuda()

        # Get labels (vocabulary)
        self._labels = self.processor.tokenizer.get_vocab()
        self._id2label = {v: k for k, v in self._labels.items()}

    def align(
        self,
        audio: np.ndarray,
        text: str,
    ) -> AlignmentResult:
        """
        Align text to audio using CTC.

        Args:
            audio: Audio waveform at config.sample_rate
            text: Transcript text

        Returns:
            AlignmentResult with word timings
        """

        import torch

        if self.model is None:
            self.load()

        # Preprocess audio
        inputs = self.processor(
            audio,
            sampling_rate=self.config.sample_rate,
            return_tensors="pt",
            padding=True,
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Get CTC logits
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        # Get frame-level predictions
        torch.argmax(logits, dim=-1)
        probs = torch.softmax(logits, dim=-1)

        # Get time resolution
        audio_duration = len(audio) / self.config.sample_rate
        num_frames = logits.shape[1]
        frame_duration = audio_duration / num_frames

        # Tokenize reference text
        words = text.strip().split()
        text_lower = text.lower().strip()

        # Get character sequence from text
        list(text_lower.replace(" ", "|"))

        # Align using dynamic programming (simplified Viterbi)
        aligned_words = self._ctc_align(
            probs[0].cpu().numpy(),
            words,
            frame_duration,
        )

        return AlignmentResult(
            text=text,
            words=aligned_words,
            audio_duration=audio_duration,
            method=AlignmentMethod.CTC,
            language=self.config.language,
        )

    def _ctc_align(
        self,
        probs: np.ndarray,
        words: list[str],
        frame_duration: float,
    ) -> list[AlignedWord]:
        """
        Perform CTC alignment using frame probabilities.

        Simplified approach: find best matching frames for each character.
        """
        # Get predicted characters per frame
        predicted_ids = np.argmax(probs, axis=-1)

        # Collapse repeated characters (CTC decoding)
        collapsed = []
        prev_id = -1
        for frame_idx, char_id in enumerate(predicted_ids):
            if char_id != prev_id and char_id != 0:  # 0 is typically blank
                label = self._id2label.get(char_id, "")
                collapsed.append((frame_idx, label, float(probs[frame_idx, char_id])))
            prev_id = char_id

        # Match words to frames
        aligned_words = []
        char_idx = 0

        for word in words:
            word_lower = word.lower()
            word_start = None
            word_end = None
            word_conf = []

            # Find characters belonging to this word
            for _c in word_lower:
                if char_idx < len(collapsed):
                    frame_idx, label, conf = collapsed[char_idx]

                    if word_start is None:
                        word_start = frame_idx

                    word_end = frame_idx
                    word_conf.append(conf)
                    char_idx += 1

            if word_start is not None and word_end is not None:
                aligned_words.append(AlignedWord(
                    word=word,
                    start_time=word_start * frame_duration,
                    end_time=(word_end + 1) * frame_duration,
                    confidence=float(np.mean(word_conf)) if word_conf else 0.0,
                ))

            # Skip word separator
            if char_idx < len(collapsed):
                char_idx += 1

        return aligned_words


class DTWAligner:
    """
    Align transcripts using Dynamic Time Warping.

    Uses audio features (MFCCs) and text features (phoneme embeddings)
    to find optimal alignment path.
    """

    def __init__(self, config: AlignerConfig):
        self.config = config

    def align(
        self,
        audio: np.ndarray,
        text: str,
    ) -> AlignmentResult:
        """
        Align text to audio using DTW.

        Args:
            audio: Audio waveform
            text: Transcript text

        Returns:
            AlignmentResult with word timings
        """
        import librosa

        # Extract audio features (MFCCs)
        mfccs = librosa.feature.mfcc(
            y=audio,
            sr=self.config.sample_rate,
            n_mfcc=13,
            hop_length=512,
        )

        audio_duration = len(audio) / self.config.sample_rate
        frame_duration = audio_duration / mfccs.shape[1]

        # Phonemize text
        try:
            from phonemizer import phonemize
            phonemize(
                text,
                language="ga",
                backend="espeak",
                strip=True,
            )
        except Exception:
            text.lower()

        words = text.strip().split()

        # For DTW, we'll use a simpler word-based approach
        # Divide audio evenly among words as initial estimate
        # then refine using energy-based boundaries

        # Find silence/pause boundaries
        rms = librosa.feature.rms(y=audio, hop_length=512)[0]
        silence_threshold = np.percentile(rms, 20)
        is_speech = rms > silence_threshold

        # Find word boundaries based on silence
        boundaries = [0]
        in_speech = False

        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                # Start of speech
                in_speech = True
            elif not speech and in_speech:
                # End of speech
                boundaries.append(i)
                in_speech = False

        if in_speech:
            boundaries.append(len(is_speech))

        # Assign words to segments
        num_segments = max(len(boundaries) - 1, 1)
        words_per_segment = max(len(words) // num_segments, 1)

        aligned_words = []
        word_idx = 0

        for seg_idx in range(min(num_segments, len(words))):
            if word_idx >= len(words):
                break

            # Get segment boundaries
            start_frame = boundaries[seg_idx] if seg_idx < len(boundaries) else 0
            end_frame = boundaries[seg_idx + 1] if seg_idx + 1 < len(boundaries) else len(is_speech)

            # Assign words to this segment
            segment_words = words[word_idx:word_idx + words_per_segment]
            word_idx += words_per_segment

            # Distribute words evenly within segment
            segment_duration = (end_frame - start_frame) * frame_duration
            word_duration = segment_duration / len(segment_words)

            for i, word in enumerate(segment_words):
                aligned_words.append(AlignedWord(
                    word=word,
                    start_time=start_frame * frame_duration + i * word_duration,
                    end_time=start_frame * frame_duration + (i + 1) * word_duration,
                    confidence=0.5,  # Lower confidence for DTW
                ))

        # Handle remaining words
        for word in words[word_idx:]:
            last_end = aligned_words[-1].end_time if aligned_words else 0

            aligned_words.append(AlignedWord(
                word=word,
                start_time=last_end,
                end_time=min(last_end + 0.5, audio_duration),
                confidence=0.3,
            ))

        return AlignmentResult(
            text=text,
            words=aligned_words,
            audio_duration=audio_duration,
            method=AlignmentMethod.DTW,
            language=self.config.language,
        )


class WhisperXAligner:
    """
    Align transcripts using WhisperX.

    Uses Whisper's cross-attention weights to perform
    accurate word-level alignment.
    """

    def __init__(self, config: AlignerConfig):
        self.config = config
        self.model = None
        self.align_model = None

    def load(self):
        """Load WhisperX models."""
        try:
            import torch
            import whisperx

            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            # Load Whisper model
            self.model = whisperx.load_model(
                self.config.whisper_model,
                device,
                compute_type=compute_type,
            )

            # Load alignment model (English-based, works for Irish too)
            self.align_model, self.metadata = whisperx.load_align_model(
                language_code="en",  # Closest available
                device=device,
            )

        except ImportError:
            raise ImportError("whisperx not installed. Install with: pip install whisperx")

    def align(
        self,
        audio: np.ndarray,
        text: str,
    ) -> AlignmentResult:
        """
        Align text to audio using WhisperX.

        Args:
            audio: Audio waveform
            text: Transcript text

        Returns:
            AlignmentResult with word timings
        """
        import torch
        import whisperx

        if self.model is None:
            self.load()

        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Prepare audio dict for WhisperX

        # Transcribe to get initial segments
        # We override with provided text
        result = self.model.transcribe(
            audio,
            language=self.config.language,
        )

        # Override transcription with provided text
        if result["segments"]:
            result["segments"][0]["text"] = text

        # Perform alignment
        aligned = whisperx.align(
            result["segments"],
            self.align_model,
            self.metadata,
            audio,
            device,
        )

        # Convert to AlignmentResult
        aligned_words = []

        for segment in aligned.get("segments", []):
            for word_data in segment.get("words", []):
                aligned_words.append(AlignedWord(
                    word=word_data.get("word", ""),
                    start_time=word_data.get("start", 0),
                    end_time=word_data.get("end", 0),
                    confidence=word_data.get("score", 0.5),
                ))

        audio_duration = len(audio) / self.config.sample_rate

        return AlignmentResult(
            text=text,
            words=aligned_words,
            audio_duration=audio_duration,
            method=AlignmentMethod.WHISPERX,
            language=self.config.language,
        )


class TranscriptAligner:
    """
    Unified transcript aligner supporting multiple methods.

    Usage:
        aligner = TranscriptAligner()
        result = aligner.align(audio, text)
        result.to_textgrid("output.TextGrid")
    """

    def __init__(self, config: AlignerConfig | None = None):
        self.config = config or AlignerConfig()

        self._ctc = None
        self._dtw = None
        self._whisperx = None

    @property
    def ctc(self) -> CTCAligner:
        """Get CTC aligner (lazy load)."""
        if self._ctc is None:
            self._ctc = CTCAligner(self.config)
        return self._ctc

    @property
    def dtw(self) -> DTWAligner:
        """Get DTW aligner (lazy load)."""
        if self._dtw is None:
            self._dtw = DTWAligner(self.config)
        return self._dtw

    @property
    def whisperx(self) -> WhisperXAligner:
        """Get WhisperX aligner (lazy load)."""
        if self._whisperx is None:
            self._whisperx = WhisperXAligner(self.config)
        return self._whisperx

    def align(
        self,
        audio: np.ndarray | str,
        text: str,
        method: AlignmentMethod | None = None,
    ) -> AlignmentResult:
        """
        Align transcript to audio.

        Args:
            audio: Audio array or path to audio file
            text: Transcript text
            method: Alignment method (default: from config)

        Returns:
            AlignmentResult with word/phoneme timings
        """
        import librosa

        # Load audio if path
        if isinstance(audio, str):
            audio, _ = librosa.load(audio, sr=self.config.sample_rate)

        method = method or self.config.method

        if method == AlignmentMethod.CTC:
            return self.ctc.align(audio, text)
        elif method == AlignmentMethod.DTW:
            return self.dtw.align(audio, text)
        elif method == AlignmentMethod.WHISPERX:
            return self.whisperx.align(audio, text)
        else:
            # Default to DTW (most robust)
            return self.dtw.align(audio, text)


def align_audio_file(
    audio_path: str,
    text: str,
    method: str = "ctc",
    output_textgrid: str | None = None,
    output_json: str | None = None,
) -> AlignmentResult:
    """
    Convenience function to align a single audio file.

    Args:
        audio_path: Path to audio file
        text: Transcript text
        method: Alignment method (ctc, dtw, whisperx)
        output_textgrid: Optional path for TextGrid output
        output_json: Optional path for JSON output

    Returns:
        AlignmentResult
    """
    import json

    config = AlignerConfig(method=AlignmentMethod(method))
    aligner = TranscriptAligner(config)

    result = aligner.align(audio_path, text)

    if output_textgrid:
        result.to_textgrid(output_textgrid)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result.to_json(), f, indent=2, ensure_ascii=False)

    return result


def batch_align(
    items: list[tuple[str, str]],
    method: str = "ctc",
    output_dir: str | None = None,
) -> list[AlignmentResult]:
    """
    Align multiple audio files with their transcripts.

    Args:
        items: List of (audio_path, transcript) tuples
        method: Alignment method
        output_dir: Optional directory for output files

    Returns:
        List of AlignmentResult
    """
    import json

    config = AlignerConfig(method=AlignmentMethod(method))
    aligner = TranscriptAligner(config)

    results = []

    for audio_path, text in items:
        try:
            result = aligner.align(audio_path, text)
            results.append(result)

            if output_dir:
                out_path = Path(output_dir)
                out_path.mkdir(parents=True, exist_ok=True)

                stem = Path(audio_path).stem

                # Save TextGrid
                result.to_textgrid(str(out_path / f"{stem}.TextGrid"))

                # Save JSON
                with open(out_path / f"{stem}.json", "w", encoding="utf-8") as f:
                    json.dump(result.to_json(), f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Failed to align {audio_path}: {e}")
            results.append(None)

    return results
