"""
Modal Unsloth TTS Training - Irish Dialect Speech Synthesis with LoRA.

Fine-tunes Orpheus-TTS-3B using Unsloth's efficient LoRA implementation
for high-quality Irish text-to-speech with per-dialect voices.

Unsloth Benefits (Jan 2025):
- 1.5x faster training
- 50% less VRAM (fits on single A100)
- LoRA 16-bit for models <3B
- Native support for Orpheus/Sesame TTS

Usage:
    # Local testing (dry run)
    modal run unsloth_tts_modal.py --dry-run

    # Train Connacht dialect
    modal run unsloth_tts_modal.py --dialect connacht

    # Train all dialects
    modal run unsloth_tts_modal.py --all-dialects

    # Deploy synthesis endpoint
    modal deploy unsloth_tts_modal.py

Cost Estimate:
    - A100-40GB: ~$4.68/hr
    - Per dialect training: ~$28 (6 hours with Unsloth)
    - All 3 dialects: ~$84
    - Remaining from $280 budget after ASR training

Dialects:
    - Connacht (Conamara, Aran): Target 40% of training data
    - Munster (Kerry, Cork, Waterford): Target 35%
    - Ulster (Donegal): Target 25%

References:
    - Unsloth: https://github.com/unslothai/unsloth
    - Orpheus-TTS: https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod
    - Sesame CSM: https://github.com/SesameAI/csm-1b
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import modal

# =============================================================================
# Modal Configuration
# =============================================================================

app = modal.App("unsloth-irish-tts")

# Volumes for persistent storage
audio_volume = modal.Volume.from_name("tts-training-audio", create_if_missing=True)
model_volume = modal.Volume.from_name("tts-models", create_if_missing=True)

AUDIO_PATH = "/audio"
MODEL_PATH = "/models"


# =============================================================================
# Docker Image with Unsloth
# =============================================================================

tts_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1-cudnn8-devel-ubuntu22.04",
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
        # Core ML
        "torch>=2.2.0",
        "torchaudio>=2.2.0",
        "transformers>=4.45.0",
        "datasets>=2.16.0",
        "accelerate>=0.25.0",
        "bitsandbytes>=0.42.0",
        # Unsloth for efficient LoRA
        "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git@main",
        "xformers>=0.0.23",
        # TTS-specific
        "orpheus-speech @ git+https://github.com/canopylabs/orpheus-tts.git@main",
        "snac @ git+https://github.com/hubertsiuzdak/snac.git@main",
        # Audio processing
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "phonemizer>=3.2.0",
        "num2words>=0.5.13",
        "pydub>=0.25.0",
        # Observability
        "boto3>=1.34.0",
        "mlflow>=2.9.0",
        "wandb>=0.16.0",
        "huggingface_hub>=0.20.0",
        "pyyaml>=6.0.0",
        "tqdm>=4.66.0",
        "peft>=0.7.0",
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
class UnslothTTSConfig:
    """Configuration for Unsloth TTS fine-tuning."""
    # Model
    model_name: str = "canopylabs/orpheus-tts-0.1-finetune-prod"
    max_seq_length: int = 2048

    # LoRA settings (Unsloth optimized)
    lora_r: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.0
    target_modules: list[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])

    # Training
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    num_epochs: int = 50
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"

    # Audio processing
    sample_rate: int = 24000  # Orpheus uses 24kHz
    max_audio_length: float = 30.0  # seconds
    min_audio_length: float = 0.5   # seconds

    # Optimization
    use_4bit: bool = False  # Unsloth LoRA 16-bit for <3B models
    use_gradient_checkpointing: bool = True

    # Outputs
    checkpoint_dir: str = "/models/checkpoints"
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10


@dataclass
class DialectDataConfig:
    """Configuration for dialect-specific training data."""
    # R2 storage
    r2_bucket: str = "oideachais-audio"
    r2_prefix: str = "unified/"

    # Local paths
    local_data_dir: str = "/audio/unified"

    # Dialect settings
    dialect: IrishDialect = IrishDialect.CONNACHT

    # Data split
    train_split: float = 0.9
    val_split: float = 0.1

    # Filtering
    min_text_length: int = 5
    max_text_length: int = 300


@dataclass
class OrpheusTTSDataset:
    """Dataset for Orpheus TTS fine-tuning.

    Orpheus uses a special format:
    - Input: Text + speaker embedding
    - Output: SNAC tokens (multi-scale audio codes)
    """
    metadata_path: Path
    sample_rate: int = 24000

    def __post_init__(self):
        import json
        import pandas as pd

        # Load metadata
        if self.metadata_path.suffix == ".json":
            with open(self.metadata_path) as f:
                self.data = json.load(f)
        else:
            self.data = pd.read_csv(self.metadata_path).to_dict("records")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        import librosa
        import numpy as np

        item = self.data[idx]

        # Load audio
        audio, _ = librosa.load(
            item["audio_path"],
            sr=self.sample_rate,
        )

        return {
            "text": item["text"],
            "audio": audio,
            "speaker_id": item.get("speaker_name", "default"),
            "dialect": item.get("dialect", "unknown"),
        }


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
def download_unified_dataset(
    data_config: DialectDataConfig,
    max_samples: int | None = None,
) -> dict[str, Any]:
    """
    Download unified audio dataset for a specific dialect.

    Args:
        data_config: Data configuration with dialect
        max_samples: Maximum samples to download

    Returns:
        Download statistics
    """
    import boto3
    import json
    from pathlib import Path

    r2 = boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )

    # Create local directory
    data_dir = Path(data_config.local_data_dir) / data_config.dialect.value
    data_dir.mkdir(parents=True, exist_ok=True)

    # Download manifest for this dialect
    manifest_key = f"{data_config.r2_prefix}{data_config.dialect.value}/manifest.json"
    manifest_path = data_dir / "manifest.json"

    try:
        r2.download_file(data_config.r2_bucket, manifest_key, str(manifest_path))

        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception:
        # No manifest, scan for files
        manifest = {"samples": []}

        paginator = r2.get_paginator("list_objects_v2")
        prefix = f"{data_config.r2_prefix}{data_config.dialect.value}/"

        for page in paginator.paginate(Bucket=data_config.r2_bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                if obj["Key"].endswith((".wav", ".mp3", ".flac")):
                    manifest["samples"].append({"key": obj["Key"]})

    # Download audio files
    downloaded = 0
    total_duration = 0.0
    samples = []

    for sample in manifest.get("samples", []):
        if max_samples and downloaded >= max_samples:
            break

        key = sample.get("key", sample.get("audio_path", ""))
        if not key:
            continue

        filename = Path(key).name
        audio_path = data_dir / "wavs" / filename
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        if not audio_path.exists():
            try:
                r2.download_file(data_config.r2_bucket, key, str(audio_path))
            except Exception:
                continue

        # Get metadata
        meta_key = key.replace(".wav", ".json").replace(".mp3", ".json")
        meta_path = data_dir / "metadata" / f"{Path(key).stem}.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            r2.download_file(data_config.r2_bucket, meta_key, str(meta_path))

            with open(meta_path) as f:
                meta = json.load(f)

            duration = meta.get("duration_ms", 0) / 1000
            total_duration += duration

            samples.append({
                "audio_path": str(audio_path),
                "text": meta.get("text", ""),
                "speaker_name": meta.get("speaker_name", "unknown"),
                "dialect": data_config.dialect.value,
                "duration": duration,
            })
        except Exception:
            # Use audio file without metadata
            samples.append({
                "audio_path": str(audio_path),
                "text": sample.get("text", ""),
                "speaker_name": sample.get("speaker_name", "unknown"),
                "dialect": data_config.dialect.value,
            })

        downloaded += 1

    # Save processed manifest
    with open(data_dir / "samples.json", "w") as f:
        json.dump(samples, f, indent=2)

    audio_volume.commit()

    return {
        "dialect": data_config.dialect.value,
        "samples_downloaded": downloaded,
        "total_duration_hours": total_duration / 3600,
        "data_dir": str(data_dir),
    }


@app.function(
    image=tts_image,
    gpu="A100",
    volumes={AUDIO_PATH: audio_volume},
    timeout=3600,
)
def prepare_snac_tokens(
    data_config: DialectDataConfig,
    tts_config: UnslothTTSConfig,
) -> dict[str, Any]:
    """
    Pre-compute SNAC tokens for training.

    SNAC (Scalable Neural Audio Codec) provides multi-scale
    audio tokens used by Orpheus TTS.

    Returns:
        Tokenization statistics
    """
    import torch
    import json
    from pathlib import Path
    import librosa
    import numpy as np
    from snac import SNAC
    from tqdm import tqdm

    # Load SNAC model
    snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").to("cuda")
    snac.eval()

    data_dir = Path(data_config.local_data_dir) / data_config.dialect.value

    # Load samples
    with open(data_dir / "samples.json") as f:
        samples = json.load(f)

    # Create tokens directory
    tokens_dir = data_dir / "snac_tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0

    for sample in tqdm(samples, desc="Computing SNAC tokens"):
        audio_path = sample["audio_path"]
        token_path = tokens_dir / f"{Path(audio_path).stem}.pt"

        if token_path.exists():
            processed += 1
            continue

        try:
            # Load and resample audio
            audio, _ = librosa.load(audio_path, sr=tts_config.sample_rate)

            # Check duration
            duration = len(audio) / tts_config.sample_rate
            if duration < tts_config.min_audio_length or duration > tts_config.max_audio_length:
                skipped += 1
                continue

            # Convert to tensor
            audio_tensor = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0).to("cuda")

            # Encode to SNAC tokens
            with torch.no_grad():
                codes = snac.encode(audio_tensor)

            # Save tokens
            torch.save({
                "codes": [c.cpu() for c in codes],
                "text": sample["text"],
                "speaker": sample.get("speaker_name", "unknown"),
                "dialect": sample.get("dialect", data_config.dialect.value),
            }, token_path)

            processed += 1

        except Exception as e:
            print(f"Error processing {audio_path}: {e}")
            skipped += 1

    audio_volume.commit()

    return {
        "dialect": data_config.dialect.value,
        "processed": processed,
        "skipped": skipped,
        "tokens_dir": str(tokens_dir),
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
    timeout=6 * 60 * 60,  # 6 hours
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("huggingface"),
        modal.Secret.from_name("mlflow"),
    ],
)
def train_tts(
    tts_config: UnslothTTSConfig,
    data_config: DialectDataConfig,
    experiment_name: str = "irish-tts-unsloth",
    run_name: str | None = None,
    push_to_hub: bool = False,
    hub_model_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Fine-tune Orpheus TTS using Unsloth LoRA.

    Uses Unsloth's efficient LoRA implementation for:
    - 1.5x faster training
    - 50% less VRAM
    - Native gradient checkpointing

    Args:
        tts_config: Model and training configuration
        data_config: Data paths and settings
        experiment_name: MLflow experiment name
        run_name: W&B run name
        push_to_hub: Upload to HuggingFace Hub
        hub_model_id: Hub model ID
        dry_run: Quick test run

    Returns:
        Training results and model path
    """
    import torch
    import json
    from pathlib import Path
    import mlflow
    import wandb
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset
    from tqdm import tqdm

    dialect = data_config.dialect.value
    run_name = run_name or f"unsloth-tts-{dialect}"
    hub_model_id = hub_model_id or f"cianfhoghlaim/irish-tts-{dialect}"

    # Initialize logging
    wandb.init(
        project="irish-tts-unsloth",
        name=run_name,
        config={
            "dialect": dialect,
            "model": tts_config.model_name,
            "lora_r": tts_config.lora_r,
            "lora_alpha": tts_config.lora_alpha,
            "batch_size": tts_config.batch_size,
            "learning_rate": tts_config.learning_rate,
            "num_epochs": tts_config.num_epochs,
        },
    )

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "dialect": dialect,
            "model": tts_config.model_name,
            "lora_r": tts_config.lora_r,
            "lora_alpha": tts_config.lora_alpha,
            "batch_size": tts_config.batch_size,
            "learning_rate": tts_config.learning_rate,
        })

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            tts_config.model_name,
            trust_remote_code=True,
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load model with Unsloth optimizations
        try:
            from unsloth import FastLanguageModel

            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=tts_config.model_name,
                max_seq_length=tts_config.max_seq_length,
                dtype=torch.bfloat16,
                load_in_4bit=tts_config.use_4bit,
            )

            # Apply Unsloth LoRA
            model = FastLanguageModel.get_peft_model(
                model,
                r=tts_config.lora_r,
                lora_alpha=tts_config.lora_alpha,
                lora_dropout=tts_config.lora_dropout,
                target_modules=tts_config.target_modules,
                bias="none",
                use_gradient_checkpointing="unsloth",
                random_state=42,
            )

            use_unsloth = True
            print("Using Unsloth optimizations")

        except ImportError:
            # Fallback to standard PEFT
            print("Unsloth not available, using standard PEFT")

            model = AutoModelForCausalLM.from_pretrained(
                tts_config.model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )

            if tts_config.use_gradient_checkpointing:
                model.gradient_checkpointing_enable()
                model = prepare_model_for_kbit_training(model)

            lora_config = LoraConfig(
                r=tts_config.lora_r,
                lora_alpha=tts_config.lora_alpha,
                lora_dropout=tts_config.lora_dropout,
                target_modules=tts_config.target_modules,
                bias="none",
                task_type="CAUSAL_LM",
            )

            model = get_peft_model(model, lora_config)
            use_unsloth = False

        # Log model info
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())

        print(f"Trainable params: {trainable_params:,} ({100*trainable_params/total_params:.2f}%)")
        mlflow.log_params({
            "trainable_params": trainable_params,
            "total_params": total_params,
            "use_unsloth": use_unsloth,
        })

        # Load tokenized data
        data_dir = Path(data_config.local_data_dir) / dialect
        tokens_dir = data_dir / "snac_tokens"

        # Build training dataset
        train_data = []

        for token_file in tqdm(list(tokens_dir.glob("*.pt")), desc="Loading tokens"):
            try:
                token_data = torch.load(token_file)

                # Format for TTS: <text> <speaker> <audio_tokens>
                text = token_data["text"]
                speaker = token_data.get("speaker", "default")
                codes = token_data["codes"]

                # Flatten SNAC codes to sequence
                audio_tokens = []
                for scale_codes in codes:
                    audio_tokens.extend(scale_codes.flatten().tolist())

                # Create training example
                prompt = f"<speaker>{speaker}</speaker><text>{text}</text>"

                train_data.append({
                    "text": prompt,
                    "audio_tokens": audio_tokens[:tts_config.max_seq_length],
                })

            except Exception as e:
                print(f"Error loading {token_file}: {e}")

        print(f"Loaded {len(train_data)} training examples")

        if not train_data:
            raise ValueError("No training data found!")

        # Limit for dry run
        if dry_run:
            train_data = train_data[:50]

        # Split train/val
        split_idx = int(len(train_data) * data_config.train_split)
        train_samples = train_data[:split_idx]
        val_samples = train_data[split_idx:]

        # Create HF datasets
        def tokenize_fn(examples):
            # Tokenize text prompts
            tokenized = tokenizer(
                examples["text"],
                truncation=True,
                max_length=tts_config.max_seq_length,
                padding="max_length",
                return_tensors="pt",
            )

            # Add audio token labels (simplified - real impl would interleave)
            tokenized["labels"] = tokenized["input_ids"].clone()

            return tokenized

        train_dataset = Dataset.from_list(train_samples).map(
            tokenize_fn,
            batched=True,
            remove_columns=["text", "audio_tokens"],
        )

        val_dataset = Dataset.from_list(val_samples).map(
            tokenize_fn,
            batched=True,
            remove_columns=["text", "audio_tokens"],
        )

        # Training arguments
        output_dir = Path(tts_config.checkpoint_dir) / f"unsloth-{dialect}"
        output_dir.mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=str(output_dir),
            per_device_train_batch_size=tts_config.batch_size,
            gradient_accumulation_steps=tts_config.gradient_accumulation_steps,
            num_train_epochs=tts_config.num_epochs if not dry_run else 1,
            learning_rate=tts_config.learning_rate,
            weight_decay=tts_config.weight_decay,
            warmup_ratio=tts_config.warmup_ratio,
            lr_scheduler_type=tts_config.lr_scheduler_type,
            logging_steps=tts_config.logging_steps,
            save_steps=tts_config.save_steps if not dry_run else 50,
            eval_strategy="steps",
            eval_steps=tts_config.eval_steps if not dry_run else 25,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            bf16=True,
            report_to=["wandb", "mlflow"],
            run_name=run_name,
            dataloader_num_workers=4,
            optim="adamw_8bit" if use_unsloth else "adamw_torch",
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )

        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
        )

        # Train
        print(f"\nStarting training for {dialect} dialect...")
        train_result = trainer.train()

        # Log final metrics
        mlflow.log_metrics({
            "train_loss": train_result.training_loss,
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
        })

        # Save final model
        final_model_dir = Path(MODEL_PATH) / f"irish-tts-{dialect}"
        final_model_dir.mkdir(parents=True, exist_ok=True)

        # Save LoRA adapters
        model.save_pretrained(str(final_model_dir))
        tokenizer.save_pretrained(str(final_model_dir))

        # Save config
        with open(final_model_dir / "training_config.json", "w") as f:
            json.dump({
                "dialect": dialect,
                "base_model": tts_config.model_name,
                "lora_r": tts_config.lora_r,
                "lora_alpha": tts_config.lora_alpha,
                "train_loss": train_result.training_loss,
                "epochs": tts_config.num_epochs if not dry_run else 1,
                "use_unsloth": use_unsloth,
            }, f, indent=2)

        # Push to Hub
        if push_to_hub and not dry_run:
            from huggingface_hub import HfApi

            api = HfApi(token=os.environ["HF_TOKEN"])
            api.create_repo(hub_model_id, exist_ok=True, private=True)
            api.upload_folder(
                folder_path=str(final_model_dir),
                repo_id=hub_model_id,
                commit_message=f"Upload Irish TTS LoRA ({dialect})",
            )

            mlflow.log_param("hub_url", f"https://huggingface.co/{hub_model_id}")

        # Commit volumes
        audio_volume.commit()
        model_volume.commit()

        wandb.finish()

        return {
            "dialect": dialect,
            "train_loss": train_result.training_loss,
            "train_samples": len(train_samples),
            "val_samples": len(val_samples),
            "model_dir": str(final_model_dir),
            "use_unsloth": use_unsloth,
            "hub_url": f"https://huggingface.co/{hub_model_id}" if push_to_hub else None,
        }


# =============================================================================
# Inference Functions
# =============================================================================

@app.cls(
    image=tts_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=120,
)
class TTSInference:
    """TTS inference service for Irish dialects."""

    def __init__(self, dialect: str = "connacht"):
        self.dialect = dialect
        self.model = None
        self.tokenizer = None
        self.snac = None

    @modal.enter()
    def load_model(self):
        """Load model on container start."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        from snac import SNAC
        import json

        model_dir = Path(MODEL_PATH) / f"irish-tts-{self.dialect}"

        # Load config
        with open(model_dir / "training_config.json") as f:
            config = json.load(f)

        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            config["base_model"],
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )

        # Load LoRA adapters
        self.model = PeftModel.from_pretrained(base_model, str(model_dir))
        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))

        # Load SNAC decoder
        self.snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").to("cuda")
        self.snac.eval()

    @modal.method()
    def synthesize(
        self,
        text: str,
        speaker: str = "default",
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> bytes:
        """
        Synthesize Irish speech from text.

        Args:
            text: Irish text to synthesize
            speaker: Speaker identity
            temperature: Sampling temperature
            top_p: Nucleus sampling probability

        Returns:
            WAV audio bytes
        """
        import torch
        import soundfile as sf
        import io

        # Format prompt
        prompt = f"<speaker>{speaker}</speaker><text>{text}</text>"

        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to("cuda")

        # Generate audio tokens
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode audio tokens (simplified - real impl more complex)
        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]

        # Convert to SNAC codes and decode
        # Note: This is a simplified version - real Orpheus has specific token handling
        audio_codes = generated_ids.unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            audio = self.snac.decode(audio_codes)

        audio_np = audio.squeeze().cpu().numpy()

        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, 24000, format="WAV")
        buffer.seek(0)

        return buffer.read()


@app.function(
    image=tts_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=60,
)
def synthesize_speech(
    text: str,
    dialect: str = "connacht",
    speaker: str = "default",
) -> bytes:
    """
    Quick synthesis function (stateless).

    For production, use TTSInference class for persistent model loading.
    """
    inference = TTSInference(dialect=dialect)
    inference.load_model()
    return inference.synthesize(text, speaker)


# =============================================================================
# CLI Entry Point
# =============================================================================

@app.local_entrypoint()
def main(
    dry_run: bool = False,
    dialect: str = "connacht",
    all_dialects: bool = False,
    max_samples: int | None = None,
    num_epochs: int = 50,
    push_to_hub: bool = False,
):
    """
    Main entry point for Unsloth TTS training.

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
    print("Unsloth Irish TTS Training Pipeline")
    print(f"Dialects: {[d.value for d in dialects]}")
    print(f"Mode: {'Dry Run' if dry_run else 'Full Training'}")
    print("=" * 60)

    sample_limit = 100 if dry_run else max_samples

    results = []

    for dialect_enum in dialects:
        print(f"\n{'='*60}")
        print(f"Training: {dialect_enum.value}")
        print(f"{'='*60}")

        data_config = DialectDataConfig(dialect=dialect_enum)
        tts_config = UnslothTTSConfig(
            num_epochs=num_epochs if not dry_run else 1,
        )

        # Step 1: Download data
        print("\n[1/3] Downloading unified dataset...")
        start = time.time()
        download_result = download_unified_dataset.remote(data_config, sample_limit)
        print(f"Downloaded: {download_result}")
        print(f"Time: {time.time() - start:.1f}s")

        # Step 2: Prepare SNAC tokens
        print("\n[2/3] Computing SNAC tokens...")
        start = time.time()
        token_result = prepare_snac_tokens.remote(data_config, tts_config)
        print(f"Tokenized: {token_result}")
        print(f"Time: {time.time() - start:.1f}s")

        # Step 3: Train model
        print("\n[3/3] Training with Unsloth LoRA...")
        start = time.time()
        train_result = train_tts.remote(
            tts_config=tts_config,
            data_config=data_config,
            experiment_name=f"irish-tts-{dialect_enum.value}",
            push_to_hub=push_to_hub,
            dry_run=dry_run,
        )
        print(f"Training complete: {train_result}")
        print(f"Time: {time.time() - start:.1f}s")

        results.append({
            "dialect": dialect_enum.value,
            **train_result,
        })

    print("\n" + "=" * 60)
    print("All dialects trained successfully!")
    print("=" * 60)

    for r in results:
        print(f"\n{r['dialect'].upper()}:")
        print(f"  Train Loss: {r.get('train_loss', 'N/A'):.4f}")
        print(f"  Model: {r.get('model_dir', 'N/A')}")
        if r.get("hub_url"):
            print(f"  Hub: {r['hub_url']}")


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
            "speaker": "default"
        }

    Returns:
        {
            "audio_base64": "...",
            "sample_rate": 24000
        }
    """
    import base64

    text = request["text"]
    dialect = request.get("dialect", "connacht")
    speaker = request.get("speaker", "default")

    audio_bytes = synthesize_speech(text, dialect, speaker)

    return {
        "audio_base64": base64.b64encode(audio_bytes).decode(),
        "sample_rate": 24000,
        "dialect": dialect,
    }
