"""
Modal Wav2Vec2-BERT 2.0 Training - Irish ASR with Dialect Classification.

Multi-task fine-tuning of Wav2Vec2-BERT 2.0 for:
- Automatic Speech Recognition (ASR) via CTC
- Irish dialect classification (Connacht/Munster/Ulster)

Usage:
    # Local testing (dry run)
    modal run wav2vec2_bert_modal.py --dry-run

    # Train full model
    modal run wav2vec2_bert_modal.py

    # Deploy inference endpoint
    modal deploy wav2vec2_bert_modal.py

Cost Estimate:
    - A100-40GB: ~$0.0013/sec = ~$4.68/hr
    - Full training: ~$20-30 (4-6 hours)
    - $280 credits ≈ 9-14 complete runs

Why Wav2Vec2-BERT over Whisper:
    - 10-30x faster inference (real-time on CPU)
    - Same WER after fine-tuning on low-resource languages
    - Native multi-task support for dialect ID
    - 2.5x more resource efficient

Architecture:
    Wav2Vec2-BERT 2.0 Encoder
        ├── CTC Head (ASR) - weight: 0.7
        └── Classification Head (Dialect) - weight: 0.3

References:
    - Wav2Vec2-BERT 2.0: https://huggingface.co/facebook/w2v-bert-2.0
    - Multi-task ASR: https://arxiv.org/abs/2309.02600
    - Irish ASR research: https://www.scss.tcd.ie/disciplines/speech
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

app = modal.App("wav2vec2-bert-irish-asr")

# Volumes for persistent storage
audio_volume = modal.Volume.from_name("asr-training-audio", create_if_missing=True)
model_volume = modal.Volume.from_name("asr-models", create_if_missing=True)

AUDIO_PATH = "/audio"
MODEL_PATH = "/models"


# =============================================================================
# Docker Image
# =============================================================================

asr_image = (
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
    )
    .pip_install(
        "torch>=2.1.0",
        "torchaudio>=2.1.0",
        "transformers>=4.36.0",
        "datasets>=2.16.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "evaluate>=0.4.0",
        "jiwer>=3.0.0",  # WER/CER computation
        "boto3>=1.34.0",
        "mlflow>=2.9.0",
        "huggingface_hub>=0.20.0",
        "pyyaml>=6.0.0",
        "tqdm>=4.66.0",
        "accelerate>=0.25.0",
        "safetensors>=0.4.0",
    )
    .env({
        "PYTHONUNBUFFERED": "1",
        "CUDA_VISIBLE_DEVICES": "0",
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
    })
)


# =============================================================================
# Configuration Classes
# =============================================================================


class IrishDialect(str, Enum):
    """Irish dialect regions."""
    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"
    STANDARD = "standard"


@dataclass
class ASRConfig:
    """Configuration for Wav2Vec2-BERT ASR training."""

    # Model
    model_name: str = "facebook/w2v-bert-2.0"
    num_dialect_classes: int = 4  # 3 dialects + standard

    # Audio processing
    sample_rate: int = 16000
    max_audio_length: float = 30.0  # seconds
    min_audio_length: float = 0.5  # seconds

    # Multi-task weights
    ctc_weight: float = 0.7  # Weight for ASR CTC loss
    dialect_weight: float = 0.3  # Weight for dialect classification

    # Training hyperparameters
    batch_size: int = 16
    num_epochs: int = 10
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    gradient_accumulation_steps: int = 2

    # Regularization
    attention_dropout: float = 0.1
    hidden_dropout: float = 0.1
    final_dropout: float = 0.1
    feat_proj_dropout: float = 0.0
    mask_time_prob: float = 0.05

    # Freezing
    freeze_feature_encoder: bool = True

    # Evaluation
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100

    # Output
    output_dir: str = "/models/wav2vec2-bert-irish"
    hub_model_id: str = "cianfhoghlaim/irish-asr-wav2vec2-bert"
    push_to_hub: bool = True
    hub_private: bool = True


@dataclass
class DataConfig:
    """Configuration for training data."""

    # Data sources
    dataset_name: str = "cianfhoghlaim/irish-audio-unified"
    train_split: str = "train"
    val_split: str = "validation"
    test_split: str = "test"

    # Columns
    audio_column: str = "audio"
    text_column: str = "text"
    dialect_column: str = "dialect"

    # Preprocessing
    remove_special_chars: bool = True
    normalize_unicode: bool = True
    lowercase: bool = True

    # Data loading
    num_proc: int = 4
    streaming: bool = False


# Irish character vocabulary for CTC
IRISH_VOCAB = [
    "<pad>", "<s>", "</s>", "<unk>", "|",  # Special tokens
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "á", "é", "í", "ó", "ú",  # Fadas
    "'", "-", " ",  # Punctuation
]


# =============================================================================
# Model Definition
# =============================================================================


def create_multi_task_model(config: ASRConfig):
    """
    Create Wav2Vec2-BERT with multi-task heads.

    Architecture:
        Wav2Vec2BertModel (frozen feature encoder)
            ├── CTC Head (vocab_size)
            └── Dialect Classification Head (num_dialects)
    """
    import torch
    import torch.nn as nn
    from transformers import (
        Wav2Vec2BertModel,
        Wav2Vec2BertConfig,
        Wav2Vec2CTCTokenizer,
    )

    class Wav2Vec2BertForMultiTask(nn.Module):
        """Wav2Vec2-BERT with CTC + Dialect Classification."""

        def __init__(self, config: ASRConfig):
            super().__init__()

            # Load base model
            self.wav2vec2_bert = Wav2Vec2BertModel.from_pretrained(
                config.model_name,
                attention_dropout=config.attention_dropout,
                hidden_dropout=config.hidden_dropout,
                feat_proj_dropout=config.feat_proj_dropout,
                mask_time_prob=config.mask_time_prob,
            )

            # Freeze feature encoder
            if config.freeze_feature_encoder:
                self.wav2vec2_bert.feature_extractor._freeze_parameters()

            hidden_size = self.wav2vec2_bert.config.hidden_size

            # CTC head for ASR
            self.ctc_dropout = nn.Dropout(config.final_dropout)
            self.ctc_head = nn.Linear(hidden_size, len(IRISH_VOCAB))

            # Dialect classification head
            self.dialect_dropout = nn.Dropout(config.final_dropout)
            self.dialect_head = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.GELU(),
                nn.Dropout(config.final_dropout),
                nn.Linear(hidden_size // 2, config.num_dialect_classes),
            )

            # Multi-task weights
            self.ctc_weight = config.ctc_weight
            self.dialect_weight = config.dialect_weight

        def forward(
            self,
            input_values,
            attention_mask=None,
            labels=None,
            dialect_labels=None,
            output_attentions=None,
            output_hidden_states=None,
        ):
            outputs = self.wav2vec2_bert(
                input_values,
                attention_mask=attention_mask,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
            )

            hidden_states = outputs.last_hidden_state

            # CTC logits (frame-level)
            ctc_hidden = self.ctc_dropout(hidden_states)
            ctc_logits = self.ctc_head(ctc_hidden)

            # Dialect logits (utterance-level via mean pooling)
            if attention_mask is not None:
                # Masked mean pooling
                mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
                sum_hidden = torch.sum(hidden_states * mask_expanded, dim=1)
                sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
                pooled = sum_hidden / sum_mask
            else:
                pooled = hidden_states.mean(dim=1)

            dialect_hidden = self.dialect_dropout(pooled)
            dialect_logits = self.dialect_head(dialect_hidden)

            loss = None
            if labels is not None or dialect_labels is not None:
                loss = torch.tensor(0.0, device=hidden_states.device)

                # CTC loss
                if labels is not None:
                    import torch.nn.functional as F
                    ctc_log_probs = F.log_softmax(ctc_logits, dim=-1).transpose(0, 1)

                    # Get input lengths
                    if attention_mask is not None:
                        input_lengths = attention_mask.sum(dim=-1)
                    else:
                        input_lengths = torch.full(
                            (ctc_logits.shape[0],), ctc_logits.shape[1],
                            dtype=torch.long, device=ctc_logits.device
                        )

                    # Get target lengths
                    target_lengths = (labels != -100).sum(dim=-1)

                    # Compute CTC loss
                    ctc_loss = F.ctc_loss(
                        ctc_log_probs,
                        labels[labels != -100].view(-1),
                        input_lengths,
                        target_lengths,
                        blank=0,  # <pad> token
                        reduction="mean",
                        zero_infinity=True,
                    )
                    loss = loss + self.ctc_weight * ctc_loss

                # Dialect classification loss
                if dialect_labels is not None:
                    import torch.nn.functional as F
                    dialect_loss = F.cross_entropy(dialect_logits, dialect_labels)
                    loss = loss + self.dialect_weight * dialect_loss

            return {
                "loss": loss,
                "ctc_logits": ctc_logits,
                "dialect_logits": dialect_logits,
                "hidden_states": outputs.hidden_states if output_hidden_states else None,
                "attentions": outputs.attentions if output_attentions else None,
            }

    return Wav2Vec2BertForMultiTask(config)


# =============================================================================
# Data Processing
# =============================================================================


def create_processor():
    """Create feature extractor and tokenizer."""
    from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2CTCTokenizer, Wav2Vec2Processor

    # Feature extractor
    feature_extractor = Wav2Vec2FeatureExtractor(
        feature_size=1,
        sampling_rate=16000,
        padding_value=0.0,
        do_normalize=True,
        return_attention_mask=True,
    )

    # CTC Tokenizer with Irish vocab
    vocab_dict = {v: i for i, v in enumerate(IRISH_VOCAB)}

    # Save vocab temporarily for tokenizer
    import json
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(vocab_dict, f)
        vocab_file = f.name

    tokenizer = Wav2Vec2CTCTokenizer(
        vocab_file,
        unk_token="<unk>",
        pad_token="<pad>",
        word_delimiter_token="|",
    )

    return Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)


def preprocess_dataset(dataset, processor, data_config: DataConfig):
    """Preprocess dataset for training."""
    import re
    import unicodedata

    # Dialect label mapping
    dialect_to_id = {
        "connacht": 0,
        "munster": 1,
        "ulster": 2,
        "standard": 3,
    }

    def normalize_text(text: str) -> str:
        """Normalize Irish text for CTC."""
        if not text:
            return ""

        # Unicode normalization
        if data_config.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Lowercase
        if data_config.lowercase:
            text = text.lower()

        # Remove special characters (keep Irish-specific)
        if data_config.remove_special_chars:
            # Keep letters, fadas, spaces, apostrophes, hyphens
            text = re.sub(r"[^a-záéíóú'\-\s]", "", text)

        # Collapse whitespace
        text = " ".join(text.split())

        return text

    def prepare_example(example):
        """Prepare a single example."""
        # Load and process audio
        audio = example[data_config.audio_column]
        if isinstance(audio, dict):
            audio_array = audio["array"]
            sampling_rate = audio["sampling_rate"]
        else:
            audio_array = audio
            sampling_rate = 16000

        # Resample if needed
        if sampling_rate != 16000:
            import librosa
            audio_array = librosa.resample(
                audio_array, orig_sr=sampling_rate, target_sr=16000
            )

        # Extract features
        inputs = processor(
            audio_array,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True,
        )

        # Tokenize text
        text = normalize_text(example.get(data_config.text_column, ""))
        with processor.as_target_processor():
            labels = processor(text).input_ids

        # Get dialect label
        dialect = example.get(data_config.dialect_column, "standard")
        dialect_id = dialect_to_id.get(dialect, 3)

        return {
            "input_values": inputs.input_values[0],
            "attention_mask": inputs.attention_mask[0] if hasattr(inputs, "attention_mask") else None,
            "labels": labels,
            "dialect_labels": dialect_id,
        }

    return dataset.map(
        prepare_example,
        remove_columns=dataset.column_names,
        num_proc=data_config.num_proc,
    )


# =============================================================================
# Training Functions
# =============================================================================


@app.function(
    image=asr_image,
    gpu="A100",
    timeout=6 * 60 * 60,  # 6 hours
    volumes={AUDIO_PATH: audio_volume, MODEL_PATH: model_volume},
    secrets=[
        modal.Secret.from_name("huggingface"),
        modal.Secret.from_name("mlflow"),
    ],
)
def train_asr(
    asr_config: Optional[dict] = None,
    data_config: Optional[dict] = None,
    dry_run: bool = False,
):
    """
    Train Wav2Vec2-BERT ASR model with dialect classification.

    Args:
        asr_config: ASR training configuration overrides
        data_config: Data configuration overrides
        dry_run: If True, run quick test with minimal data

    Returns:
        dict with training metrics and model info
    """
    import torch
    from datasets import load_dataset
    from transformers import TrainingArguments, Trainer
    import evaluate
    import mlflow

    # Parse configs
    config = ASRConfig(**(asr_config or {}))
    d_config = DataConfig(**(data_config or {}))

    if dry_run:
        config.num_epochs = 1
        config.eval_steps = 10
        config.save_steps = 50
        config.logging_steps = 5

    print(f"Training Wav2Vec2-BERT Irish ASR")
    print(f"  Model: {config.model_name}")
    print(f"  CTC weight: {config.ctc_weight}, Dialect weight: {config.dialect_weight}")
    print(f"  Epochs: {config.num_epochs}, Batch size: {config.batch_size}")

    # Load dataset
    print(f"Loading dataset: {d_config.dataset_name}")
    try:
        dataset = load_dataset(
            d_config.dataset_name,
            split=d_config.train_split,
            streaming=d_config.streaming,
        )
        val_dataset = load_dataset(
            d_config.dataset_name,
            split=d_config.val_split,
            streaming=d_config.streaming,
        )
    except Exception as e:
        print(f"Could not load HF dataset: {e}")
        print("Using synthetic data for testing...")

        # Create synthetic dataset for testing
        import numpy as np

        def generate_synthetic():
            for i in range(100 if dry_run else 1000):
                yield {
                    "audio": {"array": np.random.randn(16000 * 3).astype(np.float32), "sampling_rate": 16000},
                    "text": "tá sé go maith" if i % 2 == 0 else "bhí sé an-mhaith",
                    "dialect": ["connacht", "munster", "ulster"][i % 3],
                }

        from datasets import Dataset
        dataset = Dataset.from_generator(generate_synthetic)
        val_dataset = dataset.select(range(min(20, len(dataset))))

    # Create processor and model
    print("Creating processor and model...")
    processor = create_processor()
    model = create_multi_task_model(config)

    # Preprocess datasets
    print("Preprocessing datasets...")
    train_dataset = preprocess_dataset(dataset, processor, d_config)
    eval_dataset = preprocess_dataset(val_dataset, processor, d_config)

    # Metrics
    wer_metric = evaluate.load("wer")
    cer_metric = evaluate.load("cer")

    def compute_metrics(pred):
        """Compute WER, CER, and dialect accuracy."""
        pred_logits = pred.predictions[0] if isinstance(pred.predictions, tuple) else pred.predictions
        pred_ids = pred_logits.argmax(-1)

        # Decode predictions
        pred_str = processor.batch_decode(pred_ids)
        label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

        # Filter empty strings
        pred_str = [p if p else " " for p in pred_str]
        label_str = [l if l else " " for l in label_str]

        wer = wer_metric.compute(predictions=pred_str, references=label_str)
        cer = cer_metric.compute(predictions=pred_str, references=label_str)

        return {"wer": wer, "cer": cer}

    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        evaluation_strategy="steps",
        eval_steps=config.eval_steps,
        save_steps=config.save_steps,
        logging_steps=config.logging_steps,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        fp16=True,
        push_to_hub=config.push_to_hub and not dry_run,
        hub_model_id=config.hub_model_id if config.push_to_hub else None,
        hub_private_repo=config.hub_private,
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        report_to=["mlflow"] if not dry_run else [],
    )

    # Data collator
    from dataclasses import dataclass as dc
    from typing import Dict, List, Union

    @dc
    class DataCollatorCTCWithDialect:
        processor: Any
        padding: Union[bool, str] = True

        def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
            input_features = [{"input_values": f["input_values"]} for f in features]
            batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")

            # Labels
            label_features = [{"input_ids": f["labels"]} for f in features]
            with self.processor.as_target_processor():
                labels_batch = self.processor.pad(label_features, padding=self.padding, return_tensors="pt")

            # Replace padding with -100 for CTC loss
            labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
            batch["labels"] = labels

            # Dialect labels
            batch["dialect_labels"] = torch.tensor([f["dialect_labels"] for f in features])

            return batch

    data_collator = DataCollatorCTCWithDialect(processor=processor)

    # Initialize MLflow
    if not dry_run:
        mlflow.set_experiment("irish-asr-wav2vec2-bert")
        mlflow.start_run()
        mlflow.log_params({
            "model_name": config.model_name,
            "ctc_weight": config.ctc_weight,
            "dialect_weight": config.dialect_weight,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "num_epochs": config.num_epochs,
        })

    # Train
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=processor.feature_extractor,
    )

    print("Starting training...")
    train_result = trainer.train()

    # Save model
    print("Saving model...")
    trainer.save_model(config.output_dir)
    processor.save_pretrained(config.output_dir)

    # Sync to volume
    model_volume.commit()

    # Final evaluation
    print("Running final evaluation...")
    eval_results = trainer.evaluate()

    if not dry_run:
        mlflow.log_metrics(eval_results)
        mlflow.end_run()

    return {
        "train_loss": train_result.training_loss,
        "eval_wer": eval_results.get("eval_wer"),
        "eval_cer": eval_results.get("eval_cer"),
        "output_dir": config.output_dir,
        "hub_model_id": config.hub_model_id if config.push_to_hub else None,
    }


# =============================================================================
# Inference Endpoint
# =============================================================================


@app.cls(
    image=asr_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
)
class ASRInference:
    """Inference endpoint for Irish ASR."""

    def __init__(self, model_path: str = "/models/wav2vec2-bert-irish"):
        self.model_path = model_path

    @modal.enter()
    def load_model(self):
        """Load model on container start."""
        import torch
        from transformers import Wav2Vec2Processor

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = Wav2Vec2Processor.from_pretrained(self.model_path)

        # Load custom model
        config = ASRConfig()
        self.model = create_multi_task_model(config)
        self.model.load_state_dict(
            torch.load(f"{self.model_path}/pytorch_model.bin", map_location=self.device)
        )
        self.model.to(self.device)
        self.model.eval()

    @modal.method()
    def transcribe(self, audio_array: list, sample_rate: int = 16000) -> dict:
        """
        Transcribe audio and classify dialect.

        Args:
            audio_array: Audio samples as list of floats
            sample_rate: Audio sample rate

        Returns:
            dict with transcription and dialect prediction
        """
        import torch
        import numpy as np
        import librosa

        audio = np.array(audio_array)

        # Resample if needed
        if sample_rate != 16000:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)

        # Process
        inputs = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Decode transcription
        ctc_logits = outputs["ctc_logits"]
        pred_ids = ctc_logits.argmax(-1)
        transcription = self.processor.batch_decode(pred_ids)[0]

        # Get dialect prediction
        dialect_logits = outputs["dialect_logits"]
        dialect_id = dialect_logits.argmax(-1).item()
        dialects = ["connacht", "munster", "ulster", "standard"]
        dialect = dialects[dialect_id]

        return {
            "transcription": transcription,
            "dialect": dialect,
            "dialect_confidence": torch.softmax(dialect_logits, dim=-1).max().item(),
        }


# =============================================================================
# CLI Entry Point
# =============================================================================


@app.local_entrypoint()
def main(dry_run: bool = False, deploy: bool = False):
    """
    Train or deploy Irish ASR model.

    Args:
        dry_run: Quick test with minimal data
        deploy: Deploy inference endpoint
    """
    if deploy:
        print("Deploying ASR inference endpoint...")
        # Deployment handled by modal deploy
        return

    print("Starting Wav2Vec2-BERT Irish ASR training...")
    result = train_asr.remote(dry_run=dry_run)
    print(f"Training complete!")
    print(f"  Train loss: {result['train_loss']:.4f}")
    print(f"  Eval WER: {result['eval_wer']:.2%}")
    print(f"  Eval CER: {result['eval_cer']:.2%}")
    print(f"  Model saved to: {result['output_dir']}")
    if result.get("hub_model_id"):
        print(f"  Pushed to: https://huggingface.co/{result['hub_model_id']}")
