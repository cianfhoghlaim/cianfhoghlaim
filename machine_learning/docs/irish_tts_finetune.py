"""
Irish TTS Fine-tuning with Chatterbox.

This notebook fine-tunes a Chatterbox TTS model for Irish speech synthesis,
supporting the three main dialects: Connacht, Munster, and Ulster.

Based on /taighde/teanga/chatterbox-finetuning/ patterns.

Requirements:
- 1+ hour of Irish audio per target voice
- GPU with 12GB+ VRAM
- Custom Irish tokenizer (~2500 tokens)

Usage:
    # Run as marimo notebook
    marimo edit irish_tts_finetune.py

    # Or run directly
    python irish_tts_finetune.py
"""

# %% [markdown]
# # Irish TTS Fine-tuning with Chatterbox
#
# This notebook walks through fine-tuning a Chatterbox text-to-speech model
# for Irish (Gaeilge), supporting all three main dialects.

# %% Imports and Setup
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Configuration
@dataclass
class IrishTTSConfig:
    """Configuration for Irish TTS fine-tuning."""

    # Data paths
    dataset_path: Path = Path("../datasets/irish_tts")
    output_dir: Path = Path("../models/tts/chatterbox_irish")

    # Training parameters
    batch_size: int = 8
    learning_rate: float = 1e-5
    num_epochs: int = 100
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 500
    save_steps: int = 1000

    # Model configuration
    base_model: str = "chatterbox-tts-base"
    vocab_size: int = 2500  # Extended for Irish
    sample_rate: int = 22050

    # Irish-specific
    dialects: list[str] = field(
        default_factory=lambda: ["connacht", "munster", "ulster"]
    )
    include_fada_tokens: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_path": str(self.dataset_path),
            "output_dir": str(self.output_dir),
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "num_epochs": self.num_epochs,
            "vocab_size": self.vocab_size,
            "dialects": self.dialects,
        }


# %% [markdown]
# ## 1. Irish Tokenizer
#
# Chatterbox requires a custom tokenizer with Irish-specific tokens:
# - Fada vowels: á, é, í, ó, ú
# - Lenition combinations: bh, ch, dh, fh, gh, mh, ph, sh, th
# - Common Irish phoneme patterns

# %% Irish Tokenizer Implementation
IRISH_SPECIAL_CHARS = [
    # Fada vowels (lowercase and uppercase)
    "á", "é", "í", "ó", "ú",
    "Á", "É", "Í", "Ó", "Ú",
]

IRISH_DIGRAPHS = [
    # Lenition combinations (aspirated consonants)
    "bh", "ch", "dh", "fh", "gh", "mh", "ph", "sh", "th",
    "Bh", "Ch", "Dh", "Fh", "Gh", "Mh", "Ph", "Sh", "Th",
    "BH", "CH", "DH", "FH", "GH", "MH", "PH", "SH", "TH",
    # Eclipsis (urú)
    "mb", "gc", "nd", "bhf", "ng", "bp", "dt",
    "mB", "gC", "nD", "bhF", "nG", "bP", "dT",
]


def create_irish_tokenizer(base_tokenizer_path: str | None = None) -> Any:
    """
    Create or extend a tokenizer for Irish TTS.

    Args:
        base_tokenizer_path: Path to base tokenizer to extend

    Returns:
        Tokenizer with Irish characters
    """
    try:
        from tokenizers import Tokenizer
        from tokenizers.models import BPE
        from tokenizers.trainers import BpeTrainer
        from tokenizers.pre_tokenizers import Whitespace

        # Create new tokenizer or load base
        if base_tokenizer_path and Path(base_tokenizer_path).exists():
            tokenizer = Tokenizer.from_file(base_tokenizer_path)
            logger.info(f"Loaded base tokenizer from {base_tokenizer_path}")
        else:
            tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
            tokenizer.pre_tokenizer = Whitespace()
            logger.info("Created new BPE tokenizer")

        # Add Irish special tokens
        special_tokens = ["[PAD]", "[UNK]", "[BOS]", "[EOS]"]
        special_tokens.extend(IRISH_SPECIAL_CHARS)
        special_tokens.extend(IRISH_DIGRAPHS)

        # This is a simplified version - full implementation would:
        # 1. Load training corpus from Irish text
        # 2. Train BPE with Irish-specific normalization
        # 3. Add special tokens for prosody markers

        return tokenizer

    except ImportError:
        logger.warning("tokenizers library not installed")
        return None


# %% [markdown]
# ## 2. Dataset Loading
#
# Load LJSpeech-format dataset created by `training/tts_dataset_generator.py`

# %% Dataset Loading
def load_irish_tts_dataset(
    dataset_path: Path,
    dialect_filter: str | None = None,
) -> dict[str, Any]:
    """
    Load Irish TTS dataset in LJSpeech format.

    Args:
        dataset_path: Path to dataset directory
        dialect_filter: Optional filter by dialect

    Returns:
        Dataset dictionary with audio paths and transcripts
    """
    import csv

    metadata_path = dataset_path / "metadata.csv"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    samples = []
    with open(metadata_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) < 3:
                continue
            segment_id, text, normalized = row[:3]
            audio_path = dataset_path / "wavs" / f"{segment_id}.wav"

            if audio_path.exists():
                samples.append({
                    "id": segment_id,
                    "audio_path": str(audio_path),
                    "text": text,
                    "normalized_text": normalized,
                })

    logger.info(f"Loaded {len(samples)} samples from {dataset_path}")

    return {
        "samples": samples,
        "num_samples": len(samples),
        "dataset_path": str(dataset_path),
    }


# %% [markdown]
# ## 3. Model Architecture
#
# Chatterbox uses a T3 (Text-to-Token-to-Speech) architecture:
# - Text encoder (BERT-like)
# - Token predictor (autoregressive)
# - Vocoder (HiFi-GAN)

# %% Model Setup
def setup_chatterbox_model(config: IrishTTSConfig) -> Any:
    """
    Set up Chatterbox model for Irish fine-tuning.

    Args:
        config: Training configuration

    Returns:
        Model and tokenizer
    """
    try:
        # Check for chatterbox-tts library
        # Note: This is a placeholder - actual import would be:
        # from chatterbox import ChatterboxTTS

        logger.info(f"Loading base model: {config.base_model}")

        # Placeholder model setup
        model_config = {
            "base_model": config.base_model,
            "vocab_size": config.vocab_size,
            "sample_rate": config.sample_rate,
            "dialects": config.dialects,
        }

        logger.info("Model configuration:")
        for k, v in model_config.items():
            logger.info(f"  {k}: {v}")

        return model_config

    except ImportError as e:
        logger.error(f"Chatterbox not installed: {e}")
        logger.info("Install with: pip install chatterbox-tts")
        return None


# %% [markdown]
# ## 4. Training Loop
#
# Fine-tune the T3 module while keeping vocoder frozen.

# %% Training
def train_irish_tts(
    config: IrishTTSConfig,
    dataset: dict[str, Any],
    model: Any,
) -> dict[str, Any]:
    """
    Fine-tune Chatterbox on Irish dataset.

    Args:
        config: Training configuration
        dataset: Loaded dataset
        model: Model to fine-tune

    Returns:
        Training metrics
    """
    logger.info("Starting Irish TTS fine-tuning...")
    logger.info(f"  Samples: {dataset['num_samples']}")
    logger.info(f"  Epochs: {config.num_epochs}")
    logger.info(f"  Batch size: {config.batch_size}")

    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Training loop placeholder
    # Actual implementation would:
    # 1. Create data loaders
    # 2. Set up optimizer and scheduler
    # 3. Run training epochs with validation
    # 4. Save checkpoints

    metrics = {
        "status": "ready",
        "config": config.to_dict(),
        "dataset": dataset,
    }

    return metrics


# %% [markdown]
# ## 5. Evaluation
#
# Compare fine-tuned model against ABAIR API baseline.

# %% Evaluation
async def evaluate_irish_tts(
    model_path: Path,
    test_sentences: list[str],
) -> dict[str, Any]:
    """
    Evaluate fine-tuned Irish TTS model.

    Args:
        model_path: Path to fine-tuned model
        test_sentences: Test sentences in Irish

    Returns:
        Evaluation metrics
    """
    results = {
        "model_path": str(model_path),
        "test_sentences": len(test_sentences),
        "metrics": {
            "mos_naturalness": None,  # Mean Opinion Score
            "dialect_accuracy": None,
            "fada_pronunciation": None,
            "latency_ms": None,
        },
    }

    # Evaluation would:
    # 1. Generate audio for test sentences
    # 2. Compare with ABAIR API output
    # 3. Calculate MOS, dialect accuracy, etc.

    return results


# %% [markdown]
# ## 6. Inference
#
# Generate Irish speech from text.

# %% Inference
def synthesize_irish(
    text: str,
    model_path: Path,
    dialect: str = "connacht",
    speaker_id: str | None = None,
) -> bytes:
    """
    Synthesize Irish speech from text.

    Args:
        text: Irish text to synthesize
        model_path: Path to fine-tuned model
        dialect: Target dialect
        speaker_id: Optional speaker ID for multi-speaker

    Returns:
        Audio bytes (WAV format)
    """
    logger.info(f"Synthesizing: '{text}' ({dialect})")

    # Placeholder - actual implementation would:
    # 1. Load model
    # 2. Tokenize text
    # 3. Generate tokens
    # 4. Vocoder synthesis

    return b""


# %% [markdown]
# ## 7. Main Training Pipeline

# %% Main Pipeline
def main():
    """Run Irish TTS fine-tuning pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Irish TTS Fine-tuning")
    parser.add_argument("--dataset", default="../datasets/irish_tts")
    parser.add_argument("--output", default="../models/tts/chatterbox_irish")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--dialect", choices=["connacht", "munster", "ulster", "all"])
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Configuration
    config = IrishTTSConfig(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output),
        num_epochs=args.epochs,
        batch_size=args.batch_size,
    )

    logger.info("Irish TTS Fine-tuning Pipeline")
    logger.info("=" * 50)
    logger.info(f"Configuration: {config.to_dict()}")

    # Step 1: Create tokenizer
    logger.info("\n1. Creating Irish tokenizer...")
    tokenizer = create_irish_tokenizer()

    # Step 2: Load dataset
    logger.info("\n2. Loading dataset...")
    try:
        dataset = load_irish_tts_dataset(config.dataset_path)
    except FileNotFoundError as e:
        logger.warning(f"Dataset not found: {e}")
        logger.info("Run training/tts_dataset_generator.py first to create dataset")
        dataset = {"samples": [], "num_samples": 0}

    # Step 3: Setup model
    logger.info("\n3. Setting up model...")
    model = setup_chatterbox_model(config)

    # Step 4: Train
    if dataset["num_samples"] > 0 and model:
        logger.info("\n4. Training...")
        metrics = train_irish_tts(config, dataset, model)
        logger.info(f"Training complete: {metrics}")
    else:
        logger.info("\n4. Skipping training (no data or model)")

    logger.info("\nPipeline complete!")


if __name__ == "__main__":
    main()


# %% [markdown]
# ## Notes
#
# ### Dataset Requirements
# - Minimum 1 hour of audio per voice/dialect
# - Audio quality: 22050 Hz, 16-bit, mono
# - Transcripts must include fada characters (á, é, í, ó, ú)
#
# ### Dialect Considerations
# - **Connacht (Conamara)**: Western/central dialect
# - **Munster (Corca Dhuibhne)**: Southern dialect
# - **Ulster (Donegal)**: Northern dialect
#
# ### Comparison with ABAIR
# The fine-tuned model should be compared against ABAIR.ie:
# - MOS (Mean Opinion Score) for naturalness
# - Dialect accuracy via listener evaluation
# - Latency and throughput benchmarks
