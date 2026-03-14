"""
Modal PyLaia HTR Training - Irish Historical Handwriting Recognition.

Fine-tunes PyLaia (BLSTM + CTC) on Dúchas.ie Schools' Collection
handwriting for Handwritten Text Recognition (HTR).

Usage:
    # Local testing (dry run)
    modal run pylaia_modal.py --dry-run

    # Full training on Modal A100
    modal run pylaia_modal.py

    # Deploy as web endpoint
    modal deploy pylaia_modal.py

Cost Estimate:
    - A100-40GB: ~$0.0013/sec = ~$4.68/hr
    - $280 credits ≈ 60 hours training time
    - Full Dúchas HTR training: ~$50-100 per run

Requirements:
    - R2 storage with Dúchas images
    - Ground truth transcriptions from duchas_transcriptions asset
    - Modal account with GPU access

References:
    - PyLaia: https://github.com/jpuigcerver/PyLaia
    - eScriptorium: https://escriptorium.fr
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import modal

# =============================================================================
# Modal Configuration
# =============================================================================

# Define Modal app
app = modal.App("pylaia-irish-htr")

# Volume for persistent storage
volume = modal.Volume.from_name("htr-training-data", create_if_missing=True)
VOLUME_PATH = "/data"

# Model registry volume
model_volume = modal.Volume.from_name("htr-models", create_if_missing=True)
MODEL_PATH = "/models"


# =============================================================================
# Docker Image
# =============================================================================

pylaia_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install(
        "git",
        "wget",
        "libgl1-mesa-glx",
        "libglib2.0-0",
        "libsm6",
        "libxext6",
        "libxrender-dev",
        "libgomp1",
    )
    .pip_install(
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "torchaudio>=2.1.0",
        "pytorch-lightning>=2.1.0",
        "pylaia @ git+https://github.com/jpuigcerver/PyLaia.git@master",
        "nnutils-pytorch>=1.12.0",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "opencv-python-headless>=4.8.0",
        "lmdb>=1.4.0",
        "boto3>=1.34.0",  # For R2 access
        "mlflow>=2.9.0",
        "editdistance>=0.6.0",
        "huggingface_hub>=0.20.0",
        "wandb>=0.16.0",
        "pyyaml>=6.0.0",
    )
    .env({
        "PYTHONUNBUFFERED": "1",
        "CUDA_VISIBLE_DEVICES": "0",
    })
)


# =============================================================================
# Configuration Classes
# =============================================================================

class HTRModelArchitecture(str, Enum):
    """Supported HTR model architectures."""
    CRNN = "crnn"  # CNN + BLSTM
    TRANSFORMER = "transformer"  # Vision Transformer
    HYBRID = "hybrid"  # CNN + Transformer


@dataclass
class HTRConfig:
    """Configuration for HTR training."""
    # Model architecture
    architecture: HTRModelArchitecture = HTRModelArchitecture.CRNN

    # Image preprocessing
    img_height: int = 128
    img_width: int = 2048  # Max width, will pad/crop

    # Network architecture (CRNN)
    cnn_num_features: list[int] = None
    cnn_kernel_sizes: list[int] = None
    cnn_stride: list[int] = None
    cnn_dilation: list[int] = None
    rnn_layers: int = 4
    rnn_units: int = 256
    dropout: float = 0.5

    # Training
    batch_size: int = 16
    num_epochs: int = 100
    learning_rate: float = 3e-4
    weight_decay: float = 1e-5
    lr_scheduler: str = "cosine"
    warmup_epochs: int = 5

    # Augmentation
    augment: bool = True
    augment_affine: bool = True
    augment_morphological: bool = True

    # Data
    train_split: float = 0.9
    val_split: float = 0.1
    max_label_length: int = 256

    # Output
    checkpoint_dir: str = "/data/checkpoints"
    save_top_k: int = 3

    def __post_init__(self):
        if self.cnn_num_features is None:
            self.cnn_num_features = [16, 32, 48, 64, 80]
        if self.cnn_kernel_sizes is None:
            self.cnn_kernel_sizes = [3, 3, 3, 3, 3]
        if self.cnn_stride is None:
            self.cnn_stride = [1, 1, 1, 1, 1]
        if self.cnn_dilation is None:
            self.cnn_dilation = [1, 1, 1, 1, 1]


@dataclass
class DataConfig:
    """Configuration for training data."""
    # R2 storage paths
    r2_bucket: str = "duchas"
    r2_images_prefix: str = "images/"
    r2_transcriptions_prefix: str = "transcriptions/"

    # Local paths (on Modal volume)
    local_data_dir: str = "/data/duchas"
    local_images_dir: str = "/data/duchas/images"
    local_gt_dir: str = "/data/duchas/ground_truth"

    # Dataset filtering
    counties: list[str] = None  # None = all counties
    min_transcription_length: int = 10
    max_transcription_length: int = 500
    min_image_width: int = 100

    # Character set
    charset_path: str = "/data/charset.txt"

    def __post_init__(self):
        if self.counties is None:
            self.counties = []  # All counties


# =============================================================================
# Data Preparation Functions
# =============================================================================

@app.function(
    image=pylaia_image,
    volumes={VOLUME_PATH: volume},
    timeout=3600,
    secrets=[
        modal.Secret.from_name("cloudflare-r2"),
    ],
)
def download_training_data(
    data_config: DataConfig,
    max_samples: int | None = None,
) -> dict[str, Any]:
    """
    Download Dúchas.ie training data from R2 to Modal volume.

    Args:
        data_config: Data configuration
        max_samples: Maximum samples to download (None = all)

    Returns:
        Statistics about downloaded data
    """
    import boto3
    from pathlib import Path

    # Initialize R2 client
    r2 = boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )

    # Create directories
    images_dir = Path(data_config.local_images_dir)
    gt_dir = Path(data_config.local_gt_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    # List and download images with transcriptions
    paginator = r2.get_paginator("list_objects_v2")

    downloaded = 0
    paired = 0

    for page in paginator.paginate(
        Bucket=data_config.r2_bucket,
        Prefix=data_config.r2_images_prefix,
    ):
        for obj in page.get("Contents", []):
            if max_samples and downloaded >= max_samples:
                break

            key = obj["Key"]
            if not key.endswith((".jpg", ".jpeg", ".png")):
                continue

            # Download image
            image_name = Path(key).name
            image_path = images_dir / image_name

            if not image_path.exists():
                r2.download_file(data_config.r2_bucket, key, str(image_path))
                downloaded += 1

            # Check for corresponding transcription
            gt_key = key.replace(
                data_config.r2_images_prefix,
                data_config.r2_transcriptions_prefix,
            ).replace(".jpg", ".txt").replace(".png", ".txt")

            gt_path = gt_dir / image_name.replace(".jpg", ".txt").replace(".png", ".txt")

            try:
                r2.download_file(data_config.r2_bucket, gt_key, str(gt_path))
                paired += 1
            except Exception:
                # No transcription available
                pass

    volume.commit()

    return {
        "images_downloaded": downloaded,
        "paired_samples": paired,
        "images_dir": str(images_dir),
        "gt_dir": str(gt_dir),
    }


@app.function(
    image=pylaia_image,
    volumes={VOLUME_PATH: volume},
    timeout=1800,
)
def prepare_pylaia_dataset(
    data_config: DataConfig,
    htr_config: HTRConfig,
) -> dict[str, Any]:
    """
    Prepare dataset in PyLaia format.

    Creates:
    - train.txt: Training image paths + transcriptions
    - val.txt: Validation split
    - charset.txt: Character set
    - LMDB database for fast loading

    Returns:
        Dataset statistics
    """
    import random
    from pathlib import Path
    import lmdb
    import cv2
    import numpy as np

    images_dir = Path(data_config.local_images_dir)
    gt_dir = Path(data_config.local_gt_dir)

    # Collect paired samples
    samples = []
    charset = set()

    for gt_file in gt_dir.glob("*.txt"):
        image_name = gt_file.stem + ".jpg"
        image_path = images_dir / image_name

        if not image_path.exists():
            image_name = gt_file.stem + ".png"
            image_path = images_dir / image_name
            if not image_path.exists():
                continue

        # Read transcription
        with open(gt_file, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # Filter by length
        if len(text) < data_config.min_transcription_length:
            continue
        if len(text) > data_config.max_transcription_length:
            continue

        # Check image dimensions
        img = cv2.imread(str(image_path))
        if img is None or img.shape[1] < data_config.min_image_width:
            continue

        samples.append((str(image_path), text))
        charset.update(text)

    # Sort charset (preserve Irish character ordering)
    sorted_charset = sorted(charset)

    # Write charset file
    charset_path = Path(data_config.charset_path)
    charset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(charset_path, "w", encoding="utf-8") as f:
        for char in sorted_charset:
            f.write(f"{char}\n")

    # Shuffle and split
    random.shuffle(samples)
    split_idx = int(len(samples) * htr_config.train_split)
    train_samples = samples[:split_idx]
    val_samples = samples[split_idx:]

    # Write train/val files
    data_dir = Path(data_config.local_data_dir)

    with open(data_dir / "train.txt", "w", encoding="utf-8") as f:
        for img_path, text in train_samples:
            f.write(f"{img_path}\t{text}\n")

    with open(data_dir / "val.txt", "w", encoding="utf-8") as f:
        for img_path, text in val_samples:
            f.write(f"{img_path}\t{text}\n")

    # Create LMDB database for fast loading
    lmdb_path = data_dir / "train_lmdb"
    env = lmdb.open(str(lmdb_path), map_size=1024 * 1024 * 1024 * 50)  # 50GB

    with env.begin(write=True) as txn:
        for idx, (img_path, text) in enumerate(train_samples):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            # Resize to target height
            h, w = img.shape
            new_w = int(w * htr_config.img_height / h)
            img = cv2.resize(img, (new_w, htr_config.img_height))

            # Store image and label
            txn.put(f"image-{idx:08d}".encode(), cv2.imencode(".png", img)[1].tobytes())
            txn.put(f"label-{idx:08d}".encode(), text.encode("utf-8"))

        txn.put(b"num_samples", str(len(train_samples)).encode())

    env.close()
    volume.commit()

    return {
        "total_samples": len(samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "charset_size": len(sorted_charset),
        "charset_path": str(charset_path),
        "lmdb_path": str(lmdb_path),
    }


# =============================================================================
# Training Functions
# =============================================================================

@app.function(
    image=pylaia_image,
    gpu="A100",
    volumes={
        VOLUME_PATH: volume,
        MODEL_PATH: model_volume,
    },
    timeout=14400,  # 4 hours
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("huggingface"),
        modal.Secret.from_name("mlflow"),
    ],
)
def train_htr_model(
    htr_config: HTRConfig,
    data_config: DataConfig,
    experiment_name: str = "duchas-htr",
    run_name: str | None = None,
    push_to_hub: bool = False,
    hub_model_id: str = "cianfhoghlaim/pylaia-irish-htr",
) -> dict[str, Any]:
    """
    Train PyLaia HTR model on Irish handwriting.

    Args:
        htr_config: Model and training configuration
        data_config: Data paths configuration
        experiment_name: MLflow experiment name
        run_name: Optional run name
        push_to_hub: Push final model to HuggingFace Hub
        hub_model_id: Hub model ID if pushing

    Returns:
        Training results including metrics and model path
    """
    import torch
    import pytorch_lightning as pl
    from pytorch_lightning.callbacks import (
        ModelCheckpoint,
        EarlyStopping,
        LearningRateMonitor,
    )
    from pytorch_lightning.loggers import WandbLogger, MLFlowLogger
    import mlflow
    import wandb
    from pathlib import Path
    import json

    # Initialize logging
    wandb.init(
        project="irish-htr",
        name=run_name or f"pylaia-{experiment_name}",
        config={
            "architecture": htr_config.architecture.value,
            "img_height": htr_config.img_height,
            "batch_size": htr_config.batch_size,
            "learning_rate": htr_config.learning_rate,
            "num_epochs": htr_config.num_epochs,
        },
    )

    # MLflow tracking
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name):
        # Log parameters
        mlflow.log_params({
            "architecture": htr_config.architecture.value,
            "img_height": htr_config.img_height,
            "rnn_layers": htr_config.rnn_layers,
            "rnn_units": htr_config.rnn_units,
            "batch_size": htr_config.batch_size,
            "learning_rate": htr_config.learning_rate,
            "num_epochs": htr_config.num_epochs,
        })

        # Load charset
        with open(data_config.charset_path, "r", encoding="utf-8") as f:
            charset = [line.strip() for line in f.readlines()]

        print(f"Charset size: {len(charset)}")
        print(f"Sample chars: {charset[:20]}")

        # Build PyLaia model
        from laia.models.htr import LaiaCRNN
        from laia.data import TextImageFromTextTableDataset
        from laia.engine import HtrEngine
        from laia.utils.symbols_table import SymbolsTable

        # Create symbol table
        syms = SymbolsTable()
        for char in charset:
            syms.add(char)

        # Build model
        model = LaiaCRNN(
            num_input_channels=1,
            num_output_labels=len(charset) + 1,  # +1 for CTC blank
            cnn_num_features=htr_config.cnn_num_features,
            cnn_kernel_size=htr_config.cnn_kernel_sizes,
            cnn_stride=htr_config.cnn_stride,
            cnn_dilation=htr_config.cnn_dilation,
            cnn_activation=torch.nn.LeakyReLU,
            cnn_poolsize=[(2, 2), (2, 2), (0, 0), (2, 2), (0, 0)],
            cnn_dropout=htr_config.dropout,
            cnn_batchnorm=True,
            rnn_units=htr_config.rnn_units,
            rnn_layers=htr_config.rnn_layers,
            rnn_dropout=htr_config.dropout,
        )

        print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        mlflow.log_param("model_params", sum(p.numel() for p in model.parameters()))

        # Create datasets
        data_dir = Path(data_config.local_data_dir)

        train_dataset = TextImageFromTextTableDataset(
            txt_table=str(data_dir / "train.txt"),
            img_dirs=[data_config.local_images_dir],
            img_transform=get_image_transform(htr_config, train=True),
        )

        val_dataset = TextImageFromTextTableDataset(
            txt_table=str(data_dir / "val.txt"),
            img_dirs=[data_config.local_images_dir],
            img_transform=get_image_transform(htr_config, train=False),
        )

        # Create data loaders
        train_loader = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=htr_config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True,
            collate_fn=train_dataset.collate_fn,
        )

        val_loader = torch.utils.data.DataLoader(
            val_dataset,
            batch_size=htr_config.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
            collate_fn=val_dataset.collate_fn,
        )

        # Create HTR engine (PyTorch Lightning module)
        engine = HtrEngine(
            model=model,
            syms=syms,
            optimizer_class=torch.optim.AdamW,
            optimizer_kwargs={
                "lr": htr_config.learning_rate,
                "weight_decay": htr_config.weight_decay,
            },
            scheduler_class=torch.optim.lr_scheduler.CosineAnnealingLR,
            scheduler_kwargs={"T_max": htr_config.num_epochs},
        )

        # Callbacks
        checkpoint_callback = ModelCheckpoint(
            dirpath=htr_config.checkpoint_dir,
            filename="pylaia-irish-{epoch:02d}-{val_cer:.4f}",
            monitor="val_cer",
            mode="min",
            save_top_k=htr_config.save_top_k,
        )

        early_stopping = EarlyStopping(
            monitor="val_cer",
            patience=15,
            mode="min",
        )

        lr_monitor = LearningRateMonitor(logging_interval="step")

        # Loggers
        wandb_logger = WandbLogger(project="irish-htr")
        mlflow_logger = MLFlowLogger(
            experiment_name=experiment_name,
            tracking_uri=os.environ.get("MLFLOW_TRACKING_URI"),
        )

        # Trainer
        trainer = pl.Trainer(
            max_epochs=htr_config.num_epochs,
            accelerator="gpu",
            devices=1,
            precision="16-mixed",
            callbacks=[checkpoint_callback, early_stopping, lr_monitor],
            logger=[wandb_logger, mlflow_logger],
            log_every_n_steps=10,
            gradient_clip_val=5.0,
        )

        # Train
        print("Starting training...")
        trainer.fit(engine, train_loader, val_loader)

        # Get best model
        best_model_path = checkpoint_callback.best_model_path
        best_cer = checkpoint_callback.best_model_score

        print(f"Best model: {best_model_path}")
        print(f"Best CER: {best_cer:.4f}")

        # Log final metrics
        mlflow.log_metrics({
            "best_cer": float(best_cer),
            "final_epoch": trainer.current_epoch,
        })

        # Save final model
        final_model_dir = Path(MODEL_PATH) / experiment_name
        final_model_dir.mkdir(parents=True, exist_ok=True)

        # Save checkpoint
        torch.save({
            "model_state_dict": engine.model.state_dict(),
            "charset": charset,
            "config": {
                "img_height": htr_config.img_height,
                "rnn_layers": htr_config.rnn_layers,
                "rnn_units": htr_config.rnn_units,
            },
        }, final_model_dir / "model.pt")

        # Save config
        with open(final_model_dir / "config.json", "w") as f:
            json.dump({
                "architecture": htr_config.architecture.value,
                "img_height": htr_config.img_height,
                "charset_size": len(charset),
                "best_cer": float(best_cer),
            }, f, indent=2)

        # Push to Hub
        if push_to_hub:
            from huggingface_hub import HfApi

            api = HfApi(token=os.environ["HF_TOKEN"])
            api.create_repo(hub_model_id, exist_ok=True, private=True)
            api.upload_folder(
                folder_path=str(final_model_dir),
                repo_id=hub_model_id,
                commit_message=f"Upload PyLaia Irish HTR model (CER: {best_cer:.4f})",
            )
            print(f"Model pushed to: https://huggingface.co/{hub_model_id}")

        # Commit volumes
        volume.commit()
        model_volume.commit()

        wandb.finish()

        return {
            "best_cer": float(best_cer),
            "best_model_path": best_model_path,
            "final_model_dir": str(final_model_dir),
            "epochs_trained": trainer.current_epoch,
            "hub_url": f"https://huggingface.co/{hub_model_id}" if push_to_hub else None,
        }


def get_image_transform(config: HTRConfig, train: bool = True):
    """Get image transformation pipeline."""
    import torchvision.transforms as T

    transforms = [
        T.Grayscale(num_output_channels=1),
        T.Resize((config.img_height, None)),  # Resize height, preserve aspect
    ]

    if train and config.augment:
        if config.augment_affine:
            transforms.extend([
                T.RandomAffine(
                    degrees=2,
                    translate=(0.02, 0.02),
                    scale=(0.98, 1.02),
                    shear=2,
                ),
            ])

        transforms.extend([
            T.ColorJitter(brightness=0.2, contrast=0.2),
        ])

    transforms.extend([
        T.ToTensor(),
        T.Normalize(mean=[0.5], std=[0.5]),
    ])

    return T.Compose(transforms)


# =============================================================================
# Inference Functions
# =============================================================================

@app.function(
    image=pylaia_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=300,
)
def transcribe_image(
    image_bytes: bytes,
    model_name: str = "duchas-htr",
) -> dict[str, Any]:
    """
    Transcribe a handwritten image using trained HTR model.

    Args:
        image_bytes: PNG/JPEG image bytes
        model_name: Name of trained model

    Returns:
        Transcription result with confidence
    """
    import torch
    import cv2
    import numpy as np
    from pathlib import Path
    import json

    # Load model
    model_dir = Path(MODEL_PATH) / model_name
    checkpoint = torch.load(model_dir / "model.pt", map_location="cuda")

    with open(model_dir / "config.json") as f:
        config = json.load(f)

    # Build model
    from laia.models.htr import LaiaCRNN

    charset = checkpoint["charset"]
    model_config = checkpoint["config"]

    model = LaiaCRNN(
        num_input_channels=1,
        num_output_labels=len(charset) + 1,
        cnn_num_features=[16, 32, 48, 64, 80],
        cnn_kernel_size=[3, 3, 3, 3, 3],
        rnn_units=model_config["rnn_units"],
        rnn_layers=model_config["rnn_layers"],
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.cuda().eval()

    # Preprocess image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # Resize to target height
    h, w = img.shape
    new_w = int(w * model_config["img_height"] / h)
    img = cv2.resize(img, (new_w, model_config["img_height"]))

    # Convert to tensor
    img_tensor = torch.from_numpy(img).float().unsqueeze(0).unsqueeze(0)
    img_tensor = (img_tensor / 255.0 - 0.5) / 0.5
    img_tensor = img_tensor.cuda()

    # Inference
    with torch.no_grad():
        output = model(img_tensor)

        # CTC decode
        output = output.log_softmax(2)
        output = output.squeeze(0)

        # Greedy decoding
        _, indices = output.max(dim=1)
        indices = indices.cpu().numpy()

        # Remove blanks and duplicates
        decoded = []
        prev_idx = -1
        for idx in indices:
            if idx != prev_idx and idx != len(charset):  # Not blank
                decoded.append(charset[idx])
            prev_idx = idx

        transcription = "".join(decoded)

    return {
        "transcription": transcription,
        "confidence": float(output.max(dim=1).values.mean().exp()),
        "model": model_name,
    }


# =============================================================================
# CLI Entry Points
# =============================================================================

@app.local_entrypoint()
def main(
    dry_run: bool = False,
    max_samples: int | None = None,
    num_epochs: int = 100,
    batch_size: int = 16,
    push_to_hub: bool = False,
):
    """
    Main entry point for PyLaia HTR training.

    Args:
        dry_run: Only download a small sample and test pipeline
        max_samples: Maximum training samples (None = all)
        num_epochs: Number of training epochs
        batch_size: Training batch size
        push_to_hub: Push trained model to HuggingFace Hub
    """
    import time

    print("=" * 60)
    print("PyLaia Irish HTR Training Pipeline")
    print("=" * 60)

    # Configuration
    data_config = DataConfig()
    htr_config = HTRConfig(
        num_epochs=5 if dry_run else num_epochs,
        batch_size=batch_size,
    )

    # Limit samples for dry run
    sample_limit = 100 if dry_run else max_samples

    # Step 1: Download data
    print("\n[1/3] Downloading training data from R2...")
    start = time.time()
    download_result = download_training_data.remote(data_config, sample_limit)
    print(f"Downloaded: {download_result}")
    print(f"Time: {time.time() - start:.1f}s")

    # Step 2: Prepare dataset
    print("\n[2/3] Preparing PyLaia dataset...")
    start = time.time()
    prepare_result = prepare_pylaia_dataset.remote(data_config, htr_config)
    print(f"Prepared: {prepare_result}")
    print(f"Time: {time.time() - start:.1f}s")

    # Step 3: Train model
    print("\n[3/3] Training HTR model...")
    start = time.time()
    train_result = train_htr_model.remote(
        htr_config=htr_config,
        data_config=data_config,
        experiment_name="duchas-htr" if not dry_run else "duchas-htr-test",
        push_to_hub=push_to_hub,
    )
    print(f"Training complete: {train_result}")
    print(f"Time: {time.time() - start:.1f}s")

    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print(f"Best CER: {train_result['best_cer']:.4f}")
    print(f"Model: {train_result['final_model_dir']}")
    if train_result.get("hub_url"):
        print(f"Hub: {train_result['hub_url']}")
    print("=" * 60)


# =============================================================================
# Web Endpoint for Inference
# =============================================================================

@app.function(
    image=pylaia_image,
    gpu="T4",
    volumes={MODEL_PATH: model_volume},
    timeout=60,
    keep_warm=1,
)
@modal.web_endpoint(method="POST")
def transcribe_endpoint(item: dict) -> dict:
    """
    Web endpoint for HTR transcription.

    Request body:
        {
            "image_base64": "base64-encoded-image",
            "model": "duchas-htr"
        }

    Returns:
        {
            "transcription": "recognized text",
            "confidence": 0.95
        }
    """
    import base64

    image_bytes = base64.b64decode(item["image_base64"])
    model_name = item.get("model", "duchas-htr")

    return transcribe_image(image_bytes, model_name)
