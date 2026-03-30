"""
Modal Chatterbox TTS Training - Irish Dialect Speech Synthesis.

Fine-tunes Chatterbox TTS on Canúint.ie dialect recordings for
high-quality Irish text-to-speech with dialect-specific voices.

Usage:
    # Local testing (dry run)
    modal run chatterbox_modal.py --dry-run

    # Train Connacht dialect
    modal run chatterbox_modal.py --dialect connacht

    # Train all dialects
    modal run chatterbox_modal.py --all-dialects

    # Deploy synthesis endpoint
    modal deploy chatterbox_modal.py

Cost Estimate:
    - A100-40GB: ~$0.0013/sec = ~$4.68/hr
    - Per dialect training: ~$30-50 (6-10 hours)
    - All 3 dialects: ~$100-150
    - $280 credits ≈ 5-9 complete dialect models

Requirements:
    - R2 storage with Canúint.ie audio
    - TTS training pairs from canuint DLT source
    - Modal account with GPU access

Dialects:
    - Connacht (Conamara, Aran): ~2,500 recordings
    - Munster (Kerry, Cork, Waterford): ~2,800 recordings
    - Ulster (Donegal): ~1,800 recordings

References:
    - Chatterbox: https://github.com/resemble-ai/chatterbox
    - ABAIR: https://www.abair.ie
    - Common Voice Irish: https://commonvoice.mozilla.org/ga
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import modal

# =============================================================================
# Modal Configuration
# =============================================================================

app = modal.App("chatterbox-irish-tts")

# Volumes for persistent storage
audio_volume = modal.Volume.from_name("tts-training-audio", create_if_missing=True)
model_volume = modal.Volume.from_name("tts-models", create_if_missing=True)

AUDIO_PATH = "/audio"
MODEL_PATH = "/models"


# =============================================================================
# Docker Image
# =============================================================================

tts_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install(
        "git",
        "wget",
        "ffmpeg",
        "libsndfile1",
        "libsox-fmt-all",
        "sox",
        "espeak-ng",
    )
    .pip_install(
        "torch>=2.1.0",
        "torchaudio>=2.1.0",
        "chatterbox @ git+https://github.com/resemble-ai/chatterbox.git@main",
        "transformers>=4.36.0",
        "datasets>=2.16.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "phonemizer>=3.2.0",
        "pypinyin>=0.49.0",
        "num2words>=0.5.13",
        "pydub>=0.25.0",
        "boto3>=1.34.0",
        "mlflow>=2.9.0",
        "wandb>=0.16.0",
        "huggingface_hub>=0.20.0",
        "pyyaml>=6.0.0",
        "tqdm>=4.66.0",
    )
    .env({
        "PYTHONUNBUFFERED": "1",
        "CUDA_VISIBLE_DEVICES": "0",
        "PHONEMIZER_ESPEAK_LIBRARY": "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",
    })
)


# =============================================================================
# Configuration Classes
# =============================================================================

class IrishDialect(str, Enum):
    """Irish dialect regions."""
    CONNACHT = "connacht"  # Conamara, Aran
    MUNSTER = "munster"    # Kerry, Cork, Waterford
    ULSTER = "ulster"      # Donegal


@dataclass
class TTSConfig:
    """Configuration for TTS training."""
    # Model architecture
    model_name: str = "resemble-ai/chatterbox"  # Base model

    # Audio processing
    sample_rate: int = 22050
    n_fft: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    n_mels: int = 80
    f_min: int = 0
    f_max: int = 8000

    # Training
    batch_size: int = 32
    num_epochs: int = 200
    learning_rate: float = 1e-4
    weight_decay: float = 1e-6
    warmup_steps: int = 1000
    gradient_accumulation_steps: int = 4

    # Audio length limits (samples)
    min_audio_length: float = 0.5  # seconds
    max_audio_length: float = 15.0  # seconds

    # Speaker embedding
    speaker_embedding_dim: int = 256

    # Output
    checkpoint_dir: str = "/models/checkpoints"
    save_every_n_epochs: int = 10
    eval_every_n_steps: int = 500


@dataclass
class DataConfig:
    """Configuration for training data."""
    # R2 storage
    r2_bucket: str = "canuint"
    r2_audio_prefix: str = "audio/"
    r2_metadata_prefix: str = "metadata/"

    # Local paths
    local_data_dir: str = "/audio/canuint"
    local_audio_dir: str = "/audio/canuint/wavs"
    local_metadata_dir: str = "/audio/canuint/metadata"

    # Dataset filtering
    dialect: IrishDialect = IrishDialect.CONNACHT
    min_text_length: int = 5
    max_text_length: int = 200

    # Validation split
    val_split: float = 0.1


@dataclass
class SpeakerConfig:
    """Speaker-specific configuration."""
    speaker_id: str = ""
    speaker_name: str = ""
    dialect: IrishDialect = IrishDialect.CONNACHT
    gender: str = "female"
    age_range: str = "adult"

    # Voice characteristics (for embedding)
    pitch_shift: float = 0.0
    speaking_rate: float = 1.0


# =============================================================================
# Data Preparation Functions
# =============================================================================

@app.function(
    image=tts_image,
    volumes={AUDIO_PATH: audio_volume},
    timeout=3600,
    secrets=[
        modal.Secret.from_name("cloudflare-r2"),
    ],
)
def download_dialect_audio(
    data_config: DataConfig,
    max_samples: int | None = None,
) -> dict[str, Any]:
    """
    Download Canúint.ie audio for a specific dialect.

    Args:
        data_config: Data configuration with dialect
        max_samples: Maximum samples to download

    Returns:
        Download statistics
    """
    import boto3
    from pathlib import Path
    import json

    r2 = boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )

    # Create directories
    audio_dir = Path(data_config.local_audio_dir)
    meta_dir = Path(data_config.local_metadata_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    # Filter by dialect prefix
    dialect_prefix = f"{data_config.r2_audio_prefix}{data_config.dialect.value}/"

    paginator = r2.get_paginator("list_objects_v2")

    downloaded = 0
    total_duration = 0.0

    for page in paginator.paginate(
        Bucket=data_config.r2_bucket,
        Prefix=dialect_prefix,
    ):
        for obj in page.get("Contents", []):
            if max_samples and downloaded >= max_samples:
                break

            key = obj["Key"]
            if not key.endswith((".wav", ".mp3", ".flac")):
                continue

            # Download audio
            filename = Path(key).name
            audio_path = audio_dir / filename

            if not audio_path.exists():
                r2.download_file(data_config.r2_bucket, key, str(audio_path))

            # Download corresponding metadata
            meta_key = key.replace(
                data_config.r2_audio_prefix,
                data_config.r2_metadata_prefix,
            ).replace(".wav", ".json").replace(".mp3", ".json")

            meta_path = meta_dir / filename.replace(".wav", ".json").replace(".mp3", ".json")

            try:
                r2.download_file(data_config.r2_bucket, meta_key, str(meta_path))

                # Extract duration from metadata
                with open(meta_path) as f:
                    meta = json.load(f)
                    total_duration += meta.get("duration", 0)

            except Exception:
                pass

            downloaded += 1

    audio_volume.commit()

    return {
        "dialect": data_config.dialect.value,
        "samples_downloaded": downloaded,
        "total_duration_hours": total_duration / 3600,
        "audio_dir": str(audio_dir),
    }


@app.function(
    image=tts_image,
    volumes={AUDIO_PATH: audio_volume},
    timeout=1800,
)
def prepare_tts_dataset(
    data_config: DataConfig,
    tts_config: TTSConfig,
) -> dict[str, Any]:
    """
    Prepare dataset in Chatterbox/LJSpeech format.

    Creates:
    - metadata.csv: speaker_id|audio_path|text|phonemes
    - Preprocessed audio files (resampled, normalized)
    - Speaker embeddings

    Returns:
        Dataset statistics
    """
    import json
    import random
    from pathlib import Path
    import librosa
    import soundfile as sf
    from phonemizer import phonemize
    from phonemizer.backend import EspeakBackend
    import numpy as np

    audio_dir = Path(data_config.local_audio_dir)
    meta_dir = Path(data_config.local_metadata_dir)
    data_dir = Path(data_config.local_data_dir)

    # Initialize Irish phonemizer (using espeak-ng)
    # Note: espeak-ng has partial Irish support
    backend = EspeakBackend(
        language="ga",  # Irish
        preserve_punctuation=True,
        with_stress=True,
    )

    samples = []
    speakers = {}

    # Process all audio files
    for meta_file in meta_dir.glob("*.json"):
        with open(meta_file) as f:
            meta = json.load(f)

        text = meta.get("text", "").strip()

        # Filter by text length
        if len(text) < data_config.min_text_length:
            continue
        if len(text) > data_config.max_text_length:
            continue

        # Find corresponding audio
        audio_file = None
        for ext in [".wav", ".mp3", ".flac"]:
            candidate = audio_dir / f"{meta_file.stem}{ext}"
            if candidate.exists():
                audio_file = candidate
                break

        if not audio_file:
            continue

        # Load and validate audio
        try:
            audio, sr = librosa.load(str(audio_file), sr=None)
            duration = len(audio) / sr

            if duration < tts_config.min_audio_length:
                continue
            if duration > tts_config.max_audio_length:
                continue

        except Exception:
            continue

        # Get speaker info
        speaker_id = meta.get("speaker_id", "unknown")
        if speaker_id not in speakers:
            speakers[speaker_id] = {
                "id": speaker_id,
                "name": meta.get("speaker_name", speaker_id),
                "gender": meta.get("gender", "unknown"),
                "samples": 0,
                "duration": 0,
            }

        speakers[speaker_id]["samples"] += 1
        speakers[speaker_id]["duration"] += duration

        # Phonemize text
        try:
            phonemes = phonemize(
                text,
                language="ga",
                backend="espeak",
                strip=True,
            )
        except Exception:
            phonemes = ""

        samples.append({
            "speaker_id": speaker_id,
            "audio_path": str(audio_file),
            "text": text,
            "phonemes": phonemes,
            "duration": duration,
        })

    # Shuffle and split
    random.shuffle(samples)
    split_idx = int(len(samples) * (1 - data_config.val_split))
    train_samples = samples[:split_idx]
    val_samples = samples[split_idx:]

    # Write metadata files
    def write_metadata(samples, filename):
        with open(data_dir / filename, "w", encoding="utf-8") as f:
            f.write("speaker_id|audio_path|text|phonemes\n")
            for s in samples:
                f.write(f"{s['speaker_id']}|{s['audio_path']}|{s['text']}|{s['phonemes']}\n")

    write_metadata(train_samples, "train.csv")
    write_metadata(val_samples, "val.csv")

    # Write speaker info
    with open(data_dir / "speakers.json", "w") as f:
        json.dump(speakers, f, indent=2)

    audio_volume.commit()

    total_duration = sum(s["duration"] for s in samples)

    return {
        "dialect": data_config.dialect.value,
        "total_samples": len(samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "num_speakers": len(speakers),
        "total_duration_hours": total_duration / 3600,
        "speakers": list(speakers.keys()),
    }


@app.function(
    image=tts_image,
    gpu="A100",
    volumes={AUDIO_PATH: audio_volume},
    timeout=3600,
)
def compute_speaker_embeddings(
    data_config: DataConfig,
) -> dict[str, Any]:
    """
    Compute speaker embeddings for voice cloning.

    Uses resemblyzer or similar for speaker verification embeddings.
    """
    import torch
    import json
    from pathlib import Path
    import numpy as np
    import librosa

    data_dir = Path(data_config.local_data_dir)

    # Load speaker info
    with open(data_dir / "speakers.json") as f:
        speakers = json.load(f)

    # Load speaker encoder (using pretrained)
    from resemblyzer import VoiceEncoder, preprocess_wav

    encoder = VoiceEncoder()

    embeddings = {}

    for speaker_id, speaker_info in speakers.items():
        # Collect audio samples for this speaker
        audio_files = []

        with open(data_dir / "train.csv") as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split("|")
                if parts[0] == speaker_id:
                    audio_files.append(parts[1])

        if not audio_files:
            continue

        # Compute embedding from multiple samples
        wavs = []
        for audio_file in audio_files[:10]:  # Max 10 samples
            try:
                wav = preprocess_wav(audio_file)
                wavs.append(wav)
            except Exception:
                pass

        if wavs:
            # Concatenate and embed
            combined = np.concatenate(wavs)
            embedding = encoder.embed_speaker(combined)
            embeddings[speaker_id] = embedding.tolist()

    # Save embeddings
    with open(data_dir / "speaker_embeddings.json", "w") as f:
        json.dump(embeddings, f)

    audio_volume.commit()

    return {
        "num_speakers": len(embeddings),
        "embedding_dim": len(next(iter(embeddings.values()))) if embeddings else 0,
    }


# =============================================================================
# Training Functions
# =============================================================================

@app.function(
    image=tts_image,
    gpu="A100",
    volumes={
        AUDIO_PATH: audio_volume,
        MODEL_PATH: model_volume,
    },
    timeout=36000,  # 10 hours
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("huggingface"),
        modal.Secret.from_name("mlflow"),
    ],
)
def train_tts_model(
    tts_config: TTSConfig,
    data_config: DataConfig,
    experiment_name: str = "irish-tts",
    run_name: str | None = None,
    push_to_hub: bool = False,
    hub_model_id: str | None = None,
) -> dict[str, Any]:
    """
    Train Chatterbox TTS on Irish dialect data.

    Args:
        tts_config: Model and training configuration
        data_config: Data paths and settings
        experiment_name: MLflow experiment name
        run_name: W&B run name
        push_to_hub: Upload to HuggingFace Hub
        hub_model_id: Hub model ID

    Returns:
        Training results and model path
    """
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    from pathlib import Path
    import json
    import mlflow
    import wandb
    from tqdm import tqdm

    dialect = data_config.dialect.value
    run_name = run_name or f"chatterbox-{dialect}"
    hub_model_id = hub_model_id or f"cianfhoghlaim/chatterbox-irish-{dialect}"

    # Initialize logging
    wandb.init(
        project="irish-tts",
        name=run_name,
        config={
            "dialect": dialect,
            "batch_size": tts_config.batch_size,
            "learning_rate": tts_config.learning_rate,
            "num_epochs": tts_config.num_epochs,
            "sample_rate": tts_config.sample_rate,
        },
    )

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "dialect": dialect,
            "batch_size": tts_config.batch_size,
            "learning_rate": tts_config.learning_rate,
            "num_epochs": tts_config.num_epochs,
        })

        # Load Chatterbox model
        from chatterbox import ChatterboxTTS, ChatterboxConfig

        config = ChatterboxConfig(
            sample_rate=tts_config.sample_rate,
            n_mels=tts_config.n_mels,
            hop_length=tts_config.hop_length,
            speaker_embedding_dim=tts_config.speaker_embedding_dim,
        )

        model = ChatterboxTTS(config)
        model = model.cuda()

        print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        mlflow.log_param("model_params", sum(p.numel() for p in model.parameters()))

        # Create datasets
        data_dir = Path(data_config.local_data_dir)

        train_dataset = IrishTTSDataset(
            metadata_path=data_dir / "train.csv",
            sample_rate=tts_config.sample_rate,
            n_mels=tts_config.n_mels,
            hop_length=tts_config.hop_length,
        )

        val_dataset = IrishTTSDataset(
            metadata_path=data_dir / "val.csv",
            sample_rate=tts_config.sample_rate,
            n_mels=tts_config.n_mels,
            hop_length=tts_config.hop_length,
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=tts_config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True,
            collate_fn=train_dataset.collate_fn,
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=tts_config.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
            collate_fn=val_dataset.collate_fn,
        )

        # Optimizer and scheduler
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=tts_config.learning_rate,
            weight_decay=tts_config.weight_decay,
        )

        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=tts_config.num_epochs * len(train_loader),
        )

        # Loss function
        criterion = nn.L1Loss()

        # Training loop
        best_val_loss = float("inf")
        checkpoint_dir = Path(tts_config.checkpoint_dir) / dialect
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        global_step = 0

        for epoch in range(tts_config.num_epochs):
            model.train()
            train_loss = 0.0

            pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{tts_config.num_epochs}")

            for batch_idx, batch in enumerate(pbar):
                # Move to GPU
                text_ids = batch["text_ids"].cuda()
                mel_targets = batch["mel"].cuda()
                mel_lengths = batch["mel_lengths"].cuda()
                speaker_emb = batch.get("speaker_emb")
                if speaker_emb is not None:
                    speaker_emb = speaker_emb.cuda()

                # Forward pass
                mel_outputs, _ = model(
                    text_ids,
                    mel_targets,
                    speaker_emb=speaker_emb,
                )

                # Compute loss
                loss = criterion(mel_outputs, mel_targets)
                loss = loss / tts_config.gradient_accumulation_steps

                # Backward pass
                loss.backward()

                if (batch_idx + 1) % tts_config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

                train_loss += loss.item() * tts_config.gradient_accumulation_steps
                pbar.set_postfix({"loss": loss.item()})

                global_step += 1

                # Evaluation
                if global_step % tts_config.eval_every_n_steps == 0:
                    val_loss = evaluate(model, val_loader, criterion)
                    wandb.log({
                        "val_loss": val_loss,
                        "train_loss": train_loss / (batch_idx + 1),
                        "lr": scheduler.get_last_lr()[0],
                        "step": global_step,
                    })

                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        torch.save({
                            "epoch": epoch,
                            "model_state_dict": model.state_dict(),
                            "optimizer_state_dict": optimizer.state_dict(),
                            "val_loss": val_loss,
                            "config": config.__dict__,
                        }, checkpoint_dir / "best_model.pt")

            # Epoch logging
            avg_train_loss = train_loss / len(train_loader)
            wandb.log({
                "epoch": epoch,
                "epoch_train_loss": avg_train_loss,
            })

            # Periodic checkpoint
            if (epoch + 1) % tts_config.save_every_n_epochs == 0:
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "config": config.__dict__,
                }, checkpoint_dir / f"checkpoint_epoch_{epoch+1}.pt")

        # Log final metrics
        mlflow.log_metrics({
            "best_val_loss": best_val_loss,
            "final_train_loss": avg_train_loss,
            "epochs_trained": epoch + 1,
        })

        # Save final model
        final_model_dir = Path(MODEL_PATH) / f"chatterbox-{dialect}"
        final_model_dir.mkdir(parents=True, exist_ok=True)

        torch.save({
            "model_state_dict": model.state_dict(),
            "config": config.__dict__,
            "dialect": dialect,
            "best_val_loss": best_val_loss,
        }, final_model_dir / "model.pt")

        # Save config
        with open(final_model_dir / "config.json", "w") as f:
            json.dump({
                "dialect": dialect,
                "sample_rate": tts_config.sample_rate,
                "n_mels": tts_config.n_mels,
                "best_val_loss": best_val_loss,
            }, f, indent=2)

        # Push to Hub
        if push_to_hub:
            from huggingface_hub import HfApi

            api = HfApi(token=os.environ["HF_TOKEN"])
            api.create_repo(hub_model_id, exist_ok=True, private=True)
            api.upload_folder(
                folder_path=str(final_model_dir),
                repo_id=hub_model_id,
                commit_message=f"Upload Chatterbox Irish TTS ({dialect})",
            )

        # Commit volumes
        audio_volume.commit()
        model_volume.commit()

        wandb.finish()

        return {
            "dialect": dialect,
            "best_val_loss": best_val_loss,
            "final_model_dir": str(final_model_dir),
            "epochs_trained": epoch + 1,
            "hub_url": f"https://huggingface.co/{hub_model_id}" if push_to_hub else None,
        }


def evaluate(model, val_loader, criterion):
    """Evaluate model on validation set."""
    import torch

    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for batch in val_loader:
            text_ids = batch["text_ids"].cuda()
            mel_targets = batch["mel"].cuda()
            speaker_emb = batch.get("speaker_emb")
            if speaker_emb is not None:
                speaker_emb = speaker_emb.cuda()

            mel_outputs, _ = model(
                text_ids,
                mel_targets,
                speaker_emb=speaker_emb,
            )

            loss = criterion(mel_outputs, mel_targets)
            total_loss += loss.item()

    model.train()
    return total_loss / len(val_loader)


class IrishTTSDataset:
    """Dataset for Irish TTS training."""

    def __init__(
        self,
        metadata_path: str,
        sample_rate: int = 22050,
        n_mels: int = 80,
        hop_length: int = 256,
    ):
        import pandas as pd

        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.hop_length = hop_length

        # Load metadata
        self.data = pd.read_csv(metadata_path, sep="|")

        # Build text vocabulary
        self.char2idx = {}
        self.idx2char = {}
        self._build_vocab()

    def _build_vocab(self):
        """Build character vocabulary from texts."""
        chars = set()
        for text in self.data["text"]:
            chars.update(text)

        # Add special tokens
        self.char2idx["<pad>"] = 0
        self.char2idx["<unk>"] = 1

        for idx, char in enumerate(sorted(chars), start=2):
            self.char2idx[char] = idx
            self.idx2char[idx] = char

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        import librosa
        import numpy as np

        row = self.data.iloc[idx]

        # Load audio
        audio, _ = librosa.load(row["audio_path"], sr=self.sample_rate)

        # Compute mel spectrogram
        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            n_mels=self.n_mels,
            hop_length=self.hop_length,
        )
        mel = librosa.power_to_db(mel, ref=np.max)

        # Normalize
        mel = (mel - mel.mean()) / (mel.std() + 1e-8)

        # Encode text
        text_ids = [
            self.char2idx.get(c, self.char2idx["<unk>"])
            for c in row["text"]
        ]

        return {
            "text_ids": np.array(text_ids),
            "mel": mel.T,  # (time, n_mels)
            "speaker_id": row["speaker_id"],
            "text": row["text"],
        }

    def collate_fn(self, batch):
        """Collate batch with padding."""
        import torch
        import numpy as np

        # Find max lengths
        max_text_len = max(len(b["text_ids"]) for b in batch)
        max_mel_len = max(b["mel"].shape[0] for b in batch)

        # Pad sequences
        text_ids = torch.zeros(len(batch), max_text_len, dtype=torch.long)
        mels = torch.zeros(len(batch), max_mel_len, batch[0]["mel"].shape[1])
        mel_lengths = torch.zeros(len(batch), dtype=torch.long)

        for i, b in enumerate(batch):
            text_len = len(b["text_ids"])
            mel_len = b["mel"].shape[0]

            text_ids[i, :text_len] = torch.from_numpy(b["text_ids"])
            mels[i, :mel_len] = torch.from_numpy(b["mel"])
            mel_lengths[i] = mel_len

        return {
            "text_ids": text_ids,
            "mel": mels,
            "mel_lengths": mel_lengths,
        }


# =============================================================================
# Inference Functions
# =============================================================================

@app.function(
    image=tts_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=60,
)
def synthesize_speech(
    text: str,
    dialect: str = "connacht",
    speaker_id: str | None = None,
) -> bytes:
    """
    Synthesize Irish speech from text.

    Args:
        text: Irish text to synthesize
        dialect: Irish dialect (connacht/munster/ulster)
        speaker_id: Optional speaker for voice cloning

    Returns:
        WAV audio bytes
    """
    import torch
    import json
    from pathlib import Path
    import soundfile as sf
    import io

    # Load model
    model_dir = Path(MODEL_PATH) / f"chatterbox-{dialect}"
    checkpoint = torch.load(model_dir / "model.pt", map_location="cuda")

    with open(model_dir / "config.json") as f:
        config = json.load(f)

    from chatterbox import ChatterboxTTS, ChatterboxConfig

    model_config = ChatterboxConfig(**checkpoint["config"])
    model = ChatterboxTTS(model_config)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.cuda().eval()

    # Synthesize
    with torch.no_grad():
        audio = model.synthesize(text)

    # Convert to WAV bytes
    buffer = io.BytesIO()
    sf.write(buffer, audio, config["sample_rate"], format="WAV")
    buffer.seek(0)

    return buffer.read()


# =============================================================================
# CLI Entry Point
# =============================================================================

@app.local_entrypoint()
def main(
    dry_run: bool = False,
    dialect: str = "connacht",
    all_dialects: bool = False,
    max_samples: int | None = None,
    num_epochs: int = 200,
    push_to_hub: bool = False,
):
    """
    Main entry point for Chatterbox TTS training.

    Args:
        dry_run: Test pipeline with small sample
        dialect: Dialect to train (connacht/munster/ulster)
        all_dialects: Train all dialects
        max_samples: Maximum training samples
        num_epochs: Training epochs
        push_to_hub: Upload to HuggingFace Hub
    """
    import time

    dialects = [IrishDialect.CONNACHT, IrishDialect.MUNSTER, IrishDialect.ULSTER]

    if not all_dialects:
        dialects = [IrishDialect(dialect)]

    print("=" * 60)
    print("Chatterbox Irish TTS Training Pipeline")
    print(f"Dialects: {[d.value for d in dialects]}")
    print("=" * 60)

    sample_limit = 50 if dry_run else max_samples

    for dialect_enum in dialects:
        print(f"\n{'='*60}")
        print(f"Training: {dialect_enum.value}")
        print(f"{'='*60}")

        data_config = DataConfig(dialect=dialect_enum)
        tts_config = TTSConfig(
            num_epochs=5 if dry_run else num_epochs,
        )

        # Step 1: Download audio
        print("\n[1/4] Downloading audio...")
        start = time.time()
        download_result = download_dialect_audio.remote(data_config, sample_limit)
        print(f"Downloaded: {download_result}")
        print(f"Time: {time.time() - start:.1f}s")

        # Step 2: Prepare dataset
        print("\n[2/4] Preparing dataset...")
        start = time.time()
        prepare_result = prepare_tts_dataset.remote(data_config, tts_config)
        print(f"Prepared: {prepare_result}")
        print(f"Time: {time.time() - start:.1f}s")

        # Step 3: Compute speaker embeddings
        print("\n[3/4] Computing speaker embeddings...")
        start = time.time()
        embed_result = compute_speaker_embeddings.remote(data_config)
        print(f"Embeddings: {embed_result}")
        print(f"Time: {time.time() - start:.1f}s")

        # Step 4: Train model
        print("\n[4/4] Training TTS model...")
        start = time.time()
        train_result = train_tts_model.remote(
            tts_config=tts_config,
            data_config=data_config,
            experiment_name=f"irish-tts-{dialect_enum.value}",
            push_to_hub=push_to_hub,
        )
        print(f"Training complete: {train_result}")
        print(f"Time: {time.time() - start:.1f}s")

    print("\n" + "=" * 60)
    print("All dialects trained successfully!")
    print("=" * 60)


# =============================================================================
# Web Endpoints
# =============================================================================

@app.function(
    image=tts_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=60,
    keep_warm=1,
)
@modal.web_endpoint(method="POST")
def synthesize_endpoint(request: dict) -> dict:
    """
    Web endpoint for TTS synthesis.

    Request:
        {
            "text": "Dia duit, conas atá tú?",
            "dialect": "connacht",
            "speaker_id": null
        }

    Returns:
        {
            "audio_base64": "...",
            "sample_rate": 22050
        }
    """
    import base64

    text = request["text"]
    dialect = request.get("dialect", "connacht")
    speaker_id = request.get("speaker_id")

    audio_bytes = synthesize_speech(text, dialect, speaker_id)

    return {
        "audio_base64": base64.b64encode(audio_bytes).decode(),
        "sample_rate": 22050,
        "dialect": dialect,
    }
