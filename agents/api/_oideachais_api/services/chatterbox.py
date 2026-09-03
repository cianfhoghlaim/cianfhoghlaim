"""
Chatterbox TTS Service.

Provides Irish pronunciation using Chatterbox multilingual TTS.
Supports dialect variants: Connacht, Munster, Ulster, Standard.

For POC: Uses base multilingual model.
For Production: Finetune with Irish speech data (see taighde/teanga/chatterbox-finetuning).
"""

import asyncio
import io
import os
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

import torch
import torchaudio


class IrishDialect(StrEnum):
    """Irish dialect variants."""

    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"
    STANDARD = "standard"


def _default_tts_model_name() -> str:
    """Resolve the canonical Chatterbox TTS model from MODEL_REGISTRY.

    Per the centralized-model-registry openspec change, the TTS
    model is resolved via ``MODEL_REGISTRY.resolve("voice", "tts")``
    which maps to ``chatterbox`` (the canonical short key). Falls
    back to the historical ``ResembleAI/chatterbox`` HF ID when the
    registry import fails (e.g. minimal container builds).
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        return MODEL_REGISTRY.resolve("voice", "tts")
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return "ResembleAI/chatterbox"


@dataclass
class TTSConfig:
    """TTS configuration."""

    model_name: str = field(
        default_factory=lambda: os.environ.get(
            "CHATTERBOX_MODEL", _default_tts_model_name()
        )
    )
    device: str = "auto"  # auto, cuda, mps, cpu
    sample_rate: int = 24000
    voices_dir: Path = Path("voices")
    exaggeration: float = 0.5
    cfg_weight: float = 0.3
    temperature: float = 0.8


class ChatterboxTTSService:
    """
    Chatterbox TTS service for Irish pronunciation.

    Uses Chatterbox multilingual model with dialect-specific voice prompts.
    """

    def __init__(self, config: TTSConfig | None = None):
        self.config = config or TTSConfig()
        self._model = None
        self._device = None

    @property
    def device(self) -> str:
        """Detect best available device."""
        if self._device is None:
            if self.config.device != "auto":
                self._device = self.config.device
            elif torch.cuda.is_available():
                self._device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = "mps"
            else:
                self._device = "cpu"
        return self._device

    @property
    def model(self):
        """Lazy-load the TTS model."""
        if self._model is None:
            try:
                from chatterbox.tts import ChatterboxTTS

                self._model = ChatterboxTTS.from_pretrained(device=self.device)
            except ImportError:
                # Fallback: try multilingual model
                try:
                    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

                    self._model = ChatterboxMultilingualTTS.from_pretrained(
                        device=self.device
                    )
                except ImportError as e:
                    raise ImportError(
                        "Chatterbox TTS not installed. Run: pip install chatterbox-tts"
                    ) from e
        return self._model

    def _get_voice_prompt(self, dialect: IrishDialect) -> Path | None:
        """Get voice prompt file for dialect."""
        voice_file = self.config.voices_dir / f"{dialect.value}.wav"
        if voice_file.exists():
            return voice_file
        # Fallback to standard if dialect not available
        standard = self.config.voices_dir / "standard.wav"
        return standard if standard.exists() else None

    async def synthesize(
        self,
        text: str,
        dialect: IrishDialect = IrishDialect.STANDARD,
        language: str = "ga",
    ) -> bytes:
        """
        Synthesize Irish text to speech.

        Args:
            text: Text to synthesize (Irish or English)
            dialect: Irish dialect for voice style
            language: Language code (ga for Irish, en for English)

        Returns:
            WAV audio bytes (24kHz, mono)
        """
        # Run synthesis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        wav = await loop.run_in_executor(
            None, self._synthesize_sync, text, dialect, language
        )
        return wav

    def _synthesize_sync(
        self, text: str, dialect: IrishDialect, language: str
    ) -> bytes:
        """Synchronous synthesis."""
        voice_prompt = self._get_voice_prompt(dialect)

        try:
            # Generate audio
            if voice_prompt:
                wav = self.model.generate(
                    text=text,
                    audio_prompt_path=str(voice_prompt),
                    exaggeration=self.config.exaggeration,
                    cfg_weight=self.config.cfg_weight,
                    temperature=self.config.temperature,
                )
            else:
                # No voice prompt - use default
                wav = self.model.generate(
                    text=text,
                    exaggeration=self.config.exaggeration,
                    cfg_weight=self.config.cfg_weight,
                    temperature=self.config.temperature,
                )

            # Convert to bytes
            return self._wav_to_bytes(wav)
        except Exception as e:
            raise TTSError(f"Synthesis failed: {e}") from e

    def _wav_to_bytes(self, wav: torch.Tensor) -> bytes:
        """Convert wav tensor to bytes."""
        buffer = io.BytesIO()
        torchaudio.save(
            buffer,
            wav.unsqueeze(0) if wav.dim() == 1 else wav,
            self.config.sample_rate,
            format="wav",
        )
        buffer.seek(0)
        return buffer.read()

    async def pronounce(
        self,
        word: str,
        dialect: IrishDialect = IrishDialect.STANDARD,
    ) -> bytes:
        """
        Pronounce a single Irish word.

        Optimized for short utterances like vocabulary words.
        """
        # Clean the word
        word = word.strip()
        if not word:
            raise ValueError("Empty word")

        return await self.synthesize(word, dialect=dialect, language="ga")

    def close(self):
        """Release model resources."""
        if self._model is not None:
            del self._model
            self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


class TTSError(Exception):
    """TTS synthesis error."""

    pass


# Singleton instance
_service: ChatterboxTTSService | None = None


def get_tts_service() -> ChatterboxTTSService:
    """Get singleton TTS service instance."""
    global _service
    if _service is None:
        _service = ChatterboxTTSService()
    return _service


@lru_cache(maxsize=100)
def get_cached_pronunciation(word: str, dialect: str) -> bytes:
    """
    Get cached pronunciation for common words.

    Uses LRU cache to avoid re-synthesizing frequently requested words.
    """
    import asyncio

    service = get_tts_service()
    dialect_enum = IrishDialect(dialect)
    return asyncio.get_event_loop().run_until_complete(
        service.pronounce(word, dialect=dialect_enum)
    )


# Mock implementation for POC without GPU
class MockTTSService:
    """
    Mock TTS service for development/testing without Chatterbox.

    Returns silence or a test tone instead of real synthesis.
    """

    def __init__(self, config: TTSConfig | None = None):
        self.config = config or TTSConfig()

    async def synthesize(
        self,
        text: str,
        dialect: IrishDialect = IrishDialect.STANDARD,
        language: str = "ga",
    ) -> bytes:
        """Return mock audio (silence)."""
        # Generate 1 second of silence
        sample_rate = self.config.sample_rate
        duration = max(len(text) * 0.1, 1.0)  # ~100ms per character
        samples = int(sample_rate * duration)

        wav = torch.zeros(1, samples)

        buffer = io.BytesIO()
        torchaudio.save(buffer, wav, sample_rate, format="wav")
        buffer.seek(0)
        return buffer.read()

    async def pronounce(
        self,
        word: str,
        dialect: IrishDialect = IrishDialect.STANDARD,
    ) -> bytes:
        return await self.synthesize(word, dialect=dialect)

    def close(self):
        pass


def get_mock_tts_service() -> MockTTSService:
    """Get mock TTS service for testing."""
    return MockTTSService()
