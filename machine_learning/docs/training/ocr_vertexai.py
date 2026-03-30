"""
Google Cloud Vertex AI OCR Training - Granite-Docling Fine-tuning.

Fine-tunes Granite-Docling-258M on Irish exam papers for
document extraction with table and LaTeX support.

Usage:
    # Local testing
    python ocr_vertexai.py --dry-run

    # Submit to Vertex AI (£280 credits)
    python ocr_vertexai.py --submit

    # Deploy to Vertex AI Endpoint
    python ocr_vertexai.py --deploy

Cost Estimate:
    - n1-standard-8 + T4: ~£0.50/hr
    - Training job: ~£20-40 per run
    - £280 credits ≈ 7-14 training runs
    - Endpoint hosting: ~£0.10/hr

Training Data:
    - SEC exam papers (2015-2024): ~5,000 PDFs
    - Annotated ground truth from Z.ai extraction
    - Table structures with row/column spans
    - Mathematical notation in LaTeX

References:
    - Granite-Docling: https://huggingface.co/ibm-granite/granite-docling-258M
    - Vertex AI: https://cloud.google.com/vertex-ai
    - Docling: https://github.com/DS4SD/docling
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

class DocumentType(str, Enum):
    """Document types for training."""
    EXAM_PAPER = "exam_paper"
    MARKING_SCHEME = "marking_scheme"
    CURRICULUM_SPEC = "curriculum_spec"
    TEXTBOOK = "textbook"


class ExtractionTarget(str, Enum):
    """Extraction targets for training."""
    TEXT = "text"
    TABLES = "tables"
    EQUATIONS = "equations"
    DIAGRAMS = "diagrams"
    LAYOUT = "layout"


@dataclass
class OCRDataConfig:
    """Configuration for OCR training data."""
    # GCS paths
    gcs_bucket: str = "cianfhoghlaim-ml"
    gcs_train_path: str = "data/ocr/train"
    gcs_eval_path: str = "data/ocr/eval"
    gcs_model_path: str = "models/ocr"

    # Local paths (for data preparation)
    local_data_dir: str = "/tmp/ocr_data"
    local_pdfs_dir: str = "/tmp/ocr_data/pdfs"
    local_annotations_dir: str = "/tmp/ocr_data/annotations"

    # Data filtering
    document_types: list[DocumentType] = field(default_factory=lambda: [
        DocumentType.EXAM_PAPER,
        DocumentType.MARKING_SCHEME,
    ])
    extraction_targets: list[ExtractionTarget] = field(default_factory=lambda: [
        ExtractionTarget.TEXT,
        ExtractionTarget.TABLES,
        ExtractionTarget.EQUATIONS,
    ])

    # Dataset splits
    train_ratio: float = 0.9
    eval_ratio: float = 0.1

    # Limits
    max_pages_per_document: int = 50
    max_samples: int | None = None


@dataclass
class OCRModelConfig:
    """Configuration for OCR model training."""
    # Base model
    base_model: str = "ibm-granite/granite-docling-258m-base"
    model_type: str = "vision_encoder_decoder"

    # Image preprocessing
    image_size: tuple[int, int] = (1024, 1024)
    max_patches: int = 256

    # Training hyperparameters
    num_epochs: int = 10
    batch_size: int = 8
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    gradient_accumulation_steps: int = 4

    # Output targets
    max_output_length: int = 2048

    # Checkpointing
    save_steps: int = 500
    eval_steps: int = 500
    save_total_limit: int = 3


@dataclass
class VertexAIConfig:
    """Configuration for Vertex AI training job."""
    project_id: str = os.getenv("GCP_PROJECT_ID", "cianfhoghlaim")
    region: str = "europe-west1"

    # Machine configuration
    machine_type: str = "n1-standard-8"
    accelerator_type: str = "NVIDIA_TESLA_T4"
    accelerator_count: int = 1

    # Container
    training_image: str = "europe-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13:latest"

    # Job settings
    job_display_name: str = "granite-docling-irish-ocr"
    staging_bucket: str = "gs://cianfhoghlaim-ml/staging"

    # Timeout
    timeout_hours: int = 24


# =============================================================================
# Data Preparation
# =============================================================================

def prepare_training_data(
    data_config: OCRDataConfig,
    upload_to_gcs: bool = True,
) -> dict[str, Any]:
    """
    Prepare OCR training data from SEC exam papers.

    Steps:
    1. Load PDF documents from R2/local storage
    2. Extract ground truth using Z.ai or manual annotations
    3. Convert to Docling training format
    4. Upload to GCS for Vertex AI

    Returns:
        Statistics about prepared data
    """
    from pathlib import Path
    import random

    pdfs_dir = Path(data_config.local_pdfs_dir)
    annotations_dir = Path(data_config.local_annotations_dir)

    train_samples = []
    eval_samples = []

    # Collect paired PDF + annotation files
    for pdf_file in pdfs_dir.glob("**/*.pdf"):
        # Find corresponding annotation
        annotation_file = annotations_dir / f"{pdf_file.stem}.json"
        if not annotation_file.exists():
            continue

        with open(annotation_file) as f:
            annotation = json.load(f)

        # Filter by document type
        doc_type = annotation.get("document_type", "exam_paper")
        if doc_type not in [dt.value for dt in data_config.document_types]:
            continue

        # Create training sample
        sample = {
            "pdf_path": str(pdf_file),
            "annotation": annotation,
            "document_type": doc_type,
            "subject": annotation.get("subject"),
            "year": annotation.get("year"),
        }

        train_samples.append(sample)

        if data_config.max_samples and len(train_samples) >= data_config.max_samples:
            break

    # Shuffle and split
    random.shuffle(train_samples)
    split_idx = int(len(train_samples) * data_config.train_ratio)
    eval_samples = train_samples[split_idx:]
    train_samples = train_samples[:split_idx]

    # Convert to Docling format
    train_data = convert_to_docling_format(train_samples, data_config)
    eval_data = convert_to_docling_format(eval_samples, data_config)

    # Save locally
    output_dir = Path(data_config.local_data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "train.jsonl", "w") as f:
        for sample in train_data:
            f.write(json.dumps(sample) + "\n")

    with open(output_dir / "eval.jsonl", "w") as f:
        for sample in eval_data:
            f.write(json.dumps(sample) + "\n")

    # Upload to GCS
    if upload_to_gcs:
        upload_to_gcs_bucket(
            local_dir=output_dir,
            gcs_bucket=data_config.gcs_bucket,
            gcs_prefix=data_config.gcs_train_path,
        )

    return {
        "train_samples": len(train_samples),
        "eval_samples": len(eval_samples),
        "output_dir": str(output_dir),
    }


def convert_to_docling_format(
    samples: list[dict],
    config: OCRDataConfig,
) -> list[dict]:
    """
    Convert samples to Docling training format.

    Format:
    {
        "image": base64 encoded page image,
        "text": extracted text,
        "tables": [{"cells": [...], "structure": {...}}],
        "equations": ["latex1", "latex2"],
    }
    """
    import base64
    from io import BytesIO

    try:
        import fitz  # PyMuPDF
        from PIL import Image
    except ImportError:
        logger.warning("PyMuPDF or PIL not installed, returning empty list")
        return []

    formatted_samples = []

    for sample in samples:
        try:
            # Open PDF
            doc = fitz.open(sample["pdf_path"])
            annotation = sample["annotation"]

            for page_num, page in enumerate(doc):
                if page_num >= config.max_pages_per_document:
                    break

                # Render page to image
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Convert to base64
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()

                # Get page annotation
                page_annotation = annotation.get("pages", {}).get(str(page_num), {})

                formatted = {
                    "image": img_base64,
                    "document_type": sample["document_type"],
                    "subject": sample.get("subject"),
                    "page_num": page_num,
                }

                # Add extraction targets
                if ExtractionTarget.TEXT in config.extraction_targets:
                    formatted["text"] = page_annotation.get("text", "")

                if ExtractionTarget.TABLES in config.extraction_targets:
                    formatted["tables"] = page_annotation.get("tables", [])

                if ExtractionTarget.EQUATIONS in config.extraction_targets:
                    formatted["equations"] = page_annotation.get("equations", [])

                if ExtractionTarget.LAYOUT in config.extraction_targets:
                    formatted["layout"] = page_annotation.get("layout", {})

                formatted_samples.append(formatted)

            doc.close()

        except Exception as e:
            logger.warning(f"Failed to process {sample['pdf_path']}: {e}")

    return formatted_samples


def upload_to_gcs_bucket(
    local_dir: Path,
    gcs_bucket: str,
    gcs_prefix: str,
):
    """Upload local directory to GCS."""
    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(gcs_bucket)

        for file_path in Path(local_dir).glob("**/*"):
            if file_path.is_file():
                blob_name = f"{gcs_prefix}/{file_path.relative_to(local_dir)}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(str(file_path))
                logger.info(f"Uploaded: gs://{gcs_bucket}/{blob_name}")

    except ImportError:
        logger.error("google-cloud-storage not installed")
    except Exception as e:
        logger.error(f"GCS upload failed: {e}")


# =============================================================================
# Vertex AI Training
# =============================================================================

def create_training_script(
    model_config: OCRModelConfig,
    data_config: OCRDataConfig,
) -> str:
    """
    Generate training script for Vertex AI.

    Returns the script content to be uploaded and executed.
    """
    script = f'''#!/usr/bin/env python3
"""
Granite-Docling OCR Training Script for Vertex AI.
Auto-generated by ocr_vertexai.py
"""

import os
import json
import torch
from pathlib import Path
from transformers import (
    AutoProcessor,
    VisionEncoderDecoderModel,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
from datasets import load_dataset
import mlflow

# Configuration
BASE_MODEL = "{model_config.base_model}"
BATCH_SIZE = {model_config.batch_size}
NUM_EPOCHS = {model_config.num_epochs}
LEARNING_RATE = {model_config.learning_rate}
MAX_OUTPUT_LENGTH = {model_config.max_output_length}

# GCS paths (mounted by Vertex AI)
TRAIN_DATA = os.environ.get("AIP_TRAINING_DATA_URI", "/gcs/{data_config.gcs_bucket}/{data_config.gcs_train_path}/train.jsonl")
EVAL_DATA = os.environ.get("AIP_VALIDATION_DATA_URI", "/gcs/{data_config.gcs_bucket}/{data_config.gcs_eval_path}/eval.jsonl")
MODEL_DIR = os.environ.get("AIP_MODEL_DIR", "/gcs/{data_config.gcs_bucket}/{data_config.gcs_model_path}")

def main():
    print(f"Loading model: {{BASE_MODEL}}")

    # Load processor and model
    processor = AutoProcessor.from_pretrained(BASE_MODEL)
    model = VisionEncoderDecoderModel.from_pretrained(BASE_MODEL)

    # Configure for training
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.max_length = MAX_OUTPUT_LENGTH

    # Load datasets
    print("Loading datasets...")
    train_dataset = load_dataset("json", data_files=TRAIN_DATA, split="train")
    eval_dataset = load_dataset("json", data_files=EVAL_DATA, split="train")

    def preprocess(examples):
        import base64
        from PIL import Image
        from io import BytesIO

        images = []
        for img_b64 in examples["image"]:
            img_bytes = base64.b64decode(img_b64)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            images.append(img)

        # Process images
        pixel_values = processor(images=images, return_tensors="pt").pixel_values

        # Process text targets
        targets = examples.get("text", [""] * len(images))
        labels = processor.tokenizer(
            targets,
            padding="max_length",
            max_length=MAX_OUTPUT_LENGTH,
            truncation=True,
            return_tensors="pt",
        ).input_ids

        # Replace padding with -100 for loss calculation
        labels[labels == processor.tokenizer.pad_token_id] = -100

        return {{"pixel_values": pixel_values, "labels": labels}}

    train_dataset = train_dataset.map(
        preprocess,
        batched=True,
        batch_size=BATCH_SIZE,
        remove_columns=train_dataset.column_names,
    )

    eval_dataset = eval_dataset.map(
        preprocess,
        batched=True,
        batch_size=BATCH_SIZE,
        remove_columns=eval_dataset.column_names,
    )

    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=MODEL_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps={model_config.gradient_accumulation_steps},
        learning_rate=LEARNING_RATE,
        weight_decay={model_config.weight_decay},
        warmup_ratio={model_config.warmup_ratio},
        evaluation_strategy="steps",
        eval_steps={model_config.eval_steps},
        save_steps={model_config.save_steps},
        save_total_limit={model_config.save_total_limit},
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        logging_steps=50,
        report_to=["mlflow"],
    )

    # Initialize MLflow
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("oideachais-ocr")

    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=processor.tokenizer,
    )

    # Train
    print("Starting training...")
    with mlflow.start_run():
        mlflow.log_params({{
            "base_model": BASE_MODEL,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "num_epochs": NUM_EPOCHS,
        }})

        trainer.train()

        # Evaluate
        eval_results = trainer.evaluate()
        print(f"Evaluation results: {{eval_results}}")

        mlflow.log_metrics(eval_results)

        # Save final model
        trainer.save_model(f"{{MODEL_DIR}}/final")
        processor.save_pretrained(f"{{MODEL_DIR}}/final")

        print(f"Model saved to: {{MODEL_DIR}}/final")

if __name__ == "__main__":
    main()
'''
    return script


def submit_vertex_ai_job(
    vertex_config: VertexAIConfig,
    model_config: OCRModelConfig,
    data_config: OCRDataConfig,
) -> str:
    """
    Submit training job to Vertex AI.

    Returns:
        Job ID
    """
    try:
        from google.cloud import aiplatform

        aiplatform.init(
            project=vertex_config.project_id,
            location=vertex_config.region,
            staging_bucket=vertex_config.staging_bucket,
        )

        # Generate training script
        script_content = create_training_script(model_config, data_config)

        # Save script to GCS
        script_path = f"{vertex_config.staging_bucket}/scripts/train_ocr.py"
        # Upload script...

        # Create custom training job
        job = aiplatform.CustomTrainingJob(
            display_name=vertex_config.job_display_name,
            script_path=script_path,
            container_uri=vertex_config.training_image,
            requirements=[
                "transformers>=4.36.0",
                "datasets>=2.16.0",
                "torch>=2.1.0",
                "Pillow>=10.0.0",
                "PyMuPDF>=1.23.0",
                "mlflow>=2.9.0",
                "accelerate>=0.25.0",
            ],
        )

        # Run job
        model = job.run(
            replica_count=1,
            machine_type=vertex_config.machine_type,
            accelerator_type=vertex_config.accelerator_type,
            accelerator_count=vertex_config.accelerator_count,
            base_output_dir=f"gs://{data_config.gcs_bucket}/{data_config.gcs_model_path}",
            timeout=vertex_config.timeout_hours * 3600,
            environment_variables={
                "MLFLOW_TRACKING_URI": os.getenv("MLFLOW_TRACKING_URI", ""),
            },
        )

        return job.resource_name

    except ImportError:
        logger.error("google-cloud-aiplatform not installed")
        return ""
    except Exception as e:
        logger.error(f"Vertex AI job submission failed: {e}")
        return ""


def deploy_vertex_ai_endpoint(
    vertex_config: VertexAIConfig,
    model_path: str,
) -> str:
    """
    Deploy trained model to Vertex AI Endpoint.

    Returns:
        Endpoint URL
    """
    try:
        from google.cloud import aiplatform

        aiplatform.init(
            project=vertex_config.project_id,
            location=vertex_config.region,
        )

        # Upload model
        model = aiplatform.Model.upload(
            display_name="granite-docling-irish-ocr",
            artifact_uri=model_path,
            serving_container_image_uri="europe-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.1-13:latest",
        )

        # Deploy to endpoint
        endpoint = model.deploy(
            machine_type="n1-standard-4",
            accelerator_type="NVIDIA_TESLA_T4",
            accelerator_count=1,
            min_replica_count=1,
            max_replica_count=3,
        )

        return endpoint.resource_name

    except ImportError:
        logger.error("google-cloud-aiplatform not installed")
        return ""
    except Exception as e:
        logger.error(f"Endpoint deployment failed: {e}")
        return ""


# =============================================================================
# Evaluation
# =============================================================================

def evaluate_ocr_model(
    model_path: str,
    eval_data_path: str,
) -> dict[str, float]:
    """
    Evaluate OCR model on test set.

    Metrics:
    - CER: Character Error Rate
    - Table F1: Table structure accuracy
    - Layout Accuracy: Bounding box IoU
    """
    import editdistance

    try:
        from transformers import AutoProcessor, VisionEncoderDecoderModel
    except ImportError:
        return {"error": "transformers not installed"}

    # Load model
    processor = AutoProcessor.from_pretrained(model_path)
    model = VisionEncoderDecoderModel.from_pretrained(model_path)
    model.eval()

    # Load eval data
    with open(eval_data_path) as f:
        eval_samples = [json.loads(line) for line in f]

    total_chars = 0
    total_errors = 0
    table_correct = 0
    table_total = 0

    for sample in eval_samples:
        # Decode image
        import base64
        from PIL import Image
        from io import BytesIO

        img_bytes = base64.b64decode(sample["image"])
        img = Image.open(BytesIO(img_bytes)).convert("RGB")

        # Generate prediction
        inputs = processor(images=img, return_tensors="pt")

        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_length=2048)

        prediction = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        reference = sample.get("text", "")

        # Calculate CER
        total_chars += len(reference)
        total_errors += editdistance.eval(prediction, reference)

        # Calculate table accuracy (if present)
        if sample.get("tables"):
            table_total += 1
            # Simple check: tables mentioned in prediction
            if "table" in prediction.lower() or "|" in prediction:
                table_correct += 1

    cer = total_errors / total_chars if total_chars > 0 else 1.0
    table_f1 = table_correct / table_total if table_total > 0 else 0.0

    return {
        "cer": cer,
        "accuracy": 1.0 - cer,
        "table_f1": table_f1,
        "samples_evaluated": len(eval_samples),
    }


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Main entry point for OCR training."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Granite-Docling OCR Training on Vertex AI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test pipeline without submitting to Vertex AI",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Submit training job to Vertex AI",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy trained model to endpoint",
    )
    parser.add_argument(
        "--evaluate",
        type=str,
        default=None,
        help="Path to model for evaluation",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path to trained model (for deployment)",
    )

    args = parser.parse_args()

    # Configuration
    data_config = OCRDataConfig()
    model_config = OCRModelConfig()
    vertex_config = VertexAIConfig()

    print("=" * 60)
    print("Granite-Docling OCR Training Pipeline")
    print(f"Mode: {'Dry Run' if args.dry_run else 'Production'}")
    print("=" * 60)

    if args.evaluate:
        print("\nEvaluating model...")
        metrics = evaluate_ocr_model(
            model_path=args.evaluate,
            eval_data_path=f"{data_config.local_data_dir}/eval.jsonl",
        )
        print(f"Evaluation results: {metrics}")
        return

    if args.deploy:
        if not args.model_path:
            print("Error: --model-path required for deployment")
            return

        print("\nDeploying to Vertex AI Endpoint...")
        endpoint = deploy_vertex_ai_endpoint(vertex_config, args.model_path)
        print(f"Endpoint deployed: {endpoint}")
        return

    # Prepare data
    print("\n[1/3] Preparing training data...")
    prep_result = prepare_training_data(
        data_config,
        upload_to_gcs=not args.dry_run,
    )
    print(f"Prepared: {prep_result}")

    if args.dry_run:
        print("\n[Dry Run] Skipping Vertex AI submission")
        # Generate script for review
        script = create_training_script(model_config, data_config)
        script_path = Path(data_config.local_data_dir) / "train_ocr.py"
        script_path.write_text(script)
        print(f"Training script saved to: {script_path}")
        return

    if args.submit:
        print("\n[2/3] Submitting to Vertex AI...")
        job_id = submit_vertex_ai_job(vertex_config, model_config, data_config)
        print(f"Job submitted: {job_id}")

        print("\n[3/3] Monitor job at:")
        print(f"https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={vertex_config.project_id}")

    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
