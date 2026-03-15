"""
Dagster Assets for Irish Handwriting Recognition (HTR) Training Pipeline.

End-to-end pipeline for:
1. Dúchas.ie manuscript ingestion
2. Line segmentation and dataset generation
3. VLM fine-tuning (Modal GPU)
4. Model comparison and evaluation
5. Mobile deployment optimization

Supports concurrent LanceDB Cloud + local lakehouse storage.

Usage:
    dagster dev -m sruth.oideachais.dagster_defs

    # Materialize HTR pipeline
    dagster job execute -m sruth.oideachais.dagster_defs -j htr_training_job
"""

# Note: Removed future annotations for Dagster compatibility

from pathlib import Path

import dagster as dg
from dagster import (
    AssetIn,
    Config,
    MaterializeResult,
    MetadataValue,
    StaticPartitionsDefinition,
    asset,
)

# Irish county partitions (32 counties)
IRISH_COUNTIES = [
    "antrim", "armagh", "carlow", "cavan", "clare", "cork", "derry",
    "donegal", "down", "dublin", "fermanagh", "galway", "kerry",
    "kildare", "kilkenny", "laois", "leitrim", "limerick", "longford",
    "louth", "mayo", "meath", "monaghan", "offaly", "roscommon",
    "sligo", "tipperary", "tyrone", "waterford", "westmeath",
    "wexford", "wicklow",
]

county_partitions = StaticPartitionsDefinition(IRISH_COUNTIES)

# VLM model partitions
VLM_MODELS = ["glm-4.6v-flash", "qwen3-vl-7b", "olmocr-2-7b", "gemma-3-4b"]
vlm_partitions = StaticPartitionsDefinition(VLM_MODELS)


class HTRDatasetConfig(Config):
    """Configuration for HTR dataset generation."""

    target_samples: int = 50000
    target_height: int = 64
    max_width: int = 2048
    min_line_length: int = 3
    max_line_length: int = 500
    augmentation_factor: int = 3
    train_split: float = 0.8
    val_split: float = 0.1
    use_lancedb_cloud: bool = True


class VLMFinetuneConfig(Config):
    """Configuration for VLM fine-tuning."""

    model_name: str = "glm-4.6v-flash"
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-4
    lora_r: int = 16
    lora_alpha: int = 32
    use_4bit: bool = True
    gpu_type: str = "A10G"


@asset(
    key=["htr", "duchas_pages"],
    group_name="htr_training",
    partitions_def=county_partitions,
    compute_kind="dlt",
    description="Ingest Dúchas.ie manuscript pages by county",
    metadata={
        "source": "duchas.ie",
        "collection": "cbes",
        "rate_limit": "1 req/sec",
    },
)
def duchas_pages(
    context,
) -> MaterializeResult:
    """
    Ingest manuscript pages from Dúchas.ie Schools' Collection.

    Partitioned by Irish county for parallel processing.
    Uses DLT incremental loading with cursor tracking.
    """
    county = context.partition_key
    context.log.info(f"Ingesting Dúchas pages for county: {county}")

    try:
        import dlt

        from dlt_sources.celtic.duchas_images import duchas_images_source

        pipeline = dlt.pipeline(
            pipeline_name=f"duchas_{county}",
            destination="duckdb",
            dataset_name=f"duchas_{county}",
        )

        source = duchas_images_source(
            collection="cbes",
            max_pages=500,
            county=county,
            transcribed_only=True,
            download_images=True,
            image_size="1024,",
        )

        info = pipeline.run(source)

        # Get row counts
        with pipeline.sql_client() as client:
            pages_count = client.execute_sql(
                "SELECT COUNT(*) FROM manuscript_pages"
            ).fetchone()[0]
            trans_count = client.execute_sql(
                "SELECT COUNT(*) FROM transcriptions"
            ).fetchone()[0]

        return MaterializeResult(
            metadata={
                "county": county,
                "pages_ingested": pages_count,
                "transcriptions": trans_count,
                "load_info": str(info),
            }
        )

    except Exception as e:
        context.log.error(f"DLT ingestion failed: {e}")
        return MaterializeResult(
            metadata={
                "county": county,
                "error": str(e),
                "status": "failed",
            }
        )


@asset(
    key=["htr", "segmented_lines"],
    group_name="htr_training",
    partitions_def=county_partitions,
    ins={"duchas_pages": AssetIn(key=["htr", "duchas_pages"])},
    compute_kind="python",
    description="Segment manuscript pages into individual text lines",
    metadata={
        "algorithm": "horizontal_projection_profile",
        "target_height": "64px",
    },
)
def segmented_lines(
    context,
    config: HTRDatasetConfig,
    duchas_pages: MaterializeResult,
) -> MaterializeResult:
    """
    Segment manuscript pages into individual text lines.

    Uses horizontal projection profiles with connected component refinement.
    Outputs MNIST-style line crops with aligned transcriptions.
    """
    county = context.partition_key
    context.log.info(f"Segmenting lines for county: {county}")

    try:
        from ocr.line_segmentation import LineSegmenter, SegmentationConfig

        segmenter = LineSegmenter(SegmentationConfig(
            target_height=config.target_height,
            max_width=config.max_width,
            min_line_height=20,
            max_line_height=200,
        ))

        # Load pages from DuckDB
        import duckdb

        conn = duckdb.connect(f"duchas_{county}.duckdb")
        pages_df = conn.execute("""
            SELECT p.volume_number, p.page_id, p.image_bytes, t.full_text, t.lines
            FROM manuscript_pages p
            JOIN transcriptions t ON p.volume_number = t.volume_number
                                 AND p.page_id = t.page_id
            WHERE p.image_bytes IS NOT NULL
        """).fetchdf()
        conn.close()

        total_lines = 0
        samples_generated = 0

        for _, row in pages_df.iterrows():
            if row["image_bytes"] is None:
                continue

            # Load image from bytes
            import io

            from PIL import Image

            image = Image.open(io.BytesIO(row["image_bytes"]))
            transcription_lines = row["full_text"].split("\n") if row["full_text"] else []

            # Segment page
            lines = segmenter.segment_page(image, transcription_lines)
            total_lines += len(lines)

            for line in lines:
                if len(line.transcription) >= config.min_line_length:
                    samples_generated += 1

        return MaterializeResult(
            metadata={
                "county": county,
                "pages_processed": len(pages_df),
                "total_lines": total_lines,
                "samples_generated": samples_generated,
            }
        )

    except Exception as e:
        context.log.error(f"Segmentation failed: {e}")
        return MaterializeResult(
            metadata={
                "county": county,
                "error": str(e),
                "status": "failed",
            }
        )


@asset(
    key=["htr", "training_dataset"],
    group_name="htr_training",
    ins={"segmented_lines": AssetIn(key=["htr", "segmented_lines"])},
    compute_kind="python",
    description="Generate unified training dataset from all counties",
    metadata={
        "formats": "pylaia, unsloth, huggingface",
        "storage": "lancedb_cloud + local_lakehouse",
    },
)
def training_dataset(
    context,
    config: HTRDatasetConfig,
    segmented_lines,
) -> MaterializeResult:
    """
    Generate unified HTR training dataset.

    Combines segmented lines from all counties into:
    - PyLaia format (images/ + train.txt)
    - Unsloth JSONL (for VLM fine-tuning)
    - HuggingFace Parquet (for streaming)

    Stores in both LanceDB Cloud and local lakehouse.
    """
    context.log.info("Generating unified training dataset")

    try:
        from ocr.irish_htr_dataset import (
            DatasetConfig,
            IrishHTRDatasetGenerator,
        )

        generator = IrishHTRDatasetGenerator(
            output_dir="./irish_htr_dataset",
            config=DatasetConfig(
                target_samples=config.target_samples,
                target_height=config.target_height,
                augmentation_factor=config.augmentation_factor,
                train_split=config.train_split,
                val_split=config.val_split,
                use_lancedb=config.use_lancedb_cloud,
            ),
        )

        # Process all counties (in production, would iterate partitions)
        # For now, simulate with statistics

        # Export to all formats
        results = generator.export_all()
        stats = generator.get_statistics()

        return MaterializeResult(
            metadata={
                "total_samples": stats.get("total_samples", 0),
                "original_samples": stats.get("original_samples", 0),
                "augmented_samples": stats.get("augmented_samples", 0),
                "samples_with_fada": stats.get("samples_with_fada", 0),
                "county_distribution": MetadataValue.json(
                    stats.get("county_distribution", {})
                ),
                "export_paths": MetadataValue.json({
                    k: str(v) for k, v in results.items()
                    if isinstance(v, Path)
                }),
            }
        )

    except Exception as e:
        context.log.error(f"Dataset generation failed: {e}")
        return MaterializeResult(
            metadata={
                "error": str(e),
                "status": "failed",
            }
        )


@asset(
    key=["htr", "vlm_finetune"],
    group_name="htr_training",
    partitions_def=vlm_partitions,
    ins={"training_dataset": AssetIn(key=["htr", "training_dataset"])},
    compute_kind="modal",
    description="Fine-tune VLM model on Irish HTR dataset",
    metadata={
        "gpu": "A10G",
        "framework": "unsloth",
        "quantization": "4bit_qlora",
    },
)
def vlm_finetune(
    context,
    config: VLMFinetuneConfig,
    training_dataset: MaterializeResult,
) -> MaterializeResult:
    """
    Fine-tune a VLM model on Irish HTR dataset using Modal GPU.

    Uses Unsloth for 70% VRAM reduction with QLoRA quantization.
    Tracks experiments in MLflow.
    """
    model_name = context.partition_key
    context.log.info(f"Fine-tuning model: {model_name}")

    try:
        # Import Modal function (would be deployed separately)
        # from modal_defs.finetune_irish import finetune_vlm

        # For now, simulate the fine-tuning call
        finetune_config = {
            "model_name": model_name,
            "dataset_path": "./irish_htr_dataset/unsloth/train.jsonl",
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "lora_r": config.lora_r,
            "lora_alpha": config.lora_alpha,
            "use_4bit": config.use_4bit,
        }

        # This would call Modal
        # result = modal.Function.lookup("finetune_vlm").remote(**finetune_config)

        # Simulate result
        output_dir = f"./finetune_output/{model_name}"

        return MaterializeResult(
            metadata={
                "model_name": model_name,
                "output_dir": output_dir,
                "config": MetadataValue.json(finetune_config),
                "status": "simulated",
                "note": "Would run on Modal GPU in production",
            }
        )

    except Exception as e:
        context.log.error(f"Fine-tuning failed: {e}")
        return MaterializeResult(
            metadata={
                "model_name": model_name,
                "error": str(e),
                "status": "failed",
            }
        )


@asset(
    key=["htr", "model_comparison"],
    group_name="htr_training",
    ins={"vlm_finetune": AssetIn(key=["htr", "vlm_finetune"])},
    compute_kind="python",
    description="Compare fine-tuned VLM models on Irish OCR",
    metadata={
        "metrics": "cer, wer, fada_accuracy, tironian_accuracy",
        "tracking": "mlflow",
    },
)
def model_comparison(
    context,
    vlm_finetune,
) -> MaterializeResult:
    """
    Compare fine-tuned VLM models on Irish OCR test set.

    Evaluates:
    - CER (Character Error Rate)
    - WER (Word Error Rate)
    - Fada Accuracy (á, é, í, ó, ú)
    - Tironian Et Detection (⁊)
    - Inference Speed

    Generates HTML report and MLflow comparison.
    """
    context.log.info("Running VLM model comparison")

    try:
        from ocr.vlm_finetune_comparison import VLMComparisonPipeline

        pipeline = VLMComparisonPipeline(
            dataset_path="./irish_htr_dataset/unsloth",
            models=VLM_MODELS,
            output_dir="./vlm_comparison",
        )

        results = pipeline.run_comparison(finetune=False, max_samples=500)

        # Export reports
        report_path = pipeline.export_report()
        json_path = pipeline.export_results_json()

        # Get best model
        best_result = min(results, key=lambda r: r.cer) if results else None

        return MaterializeResult(
            metadata={
                "models_evaluated": len(results),
                "best_model": best_result.model_name if best_result else "none",
                "best_cer": best_result.cer if best_result else 1.0,
                "best_fada_accuracy": max(r.fada_accuracy for r in results) if results else 0.0,
                "report_path": str(report_path),
                "results_json": str(json_path),
                "results": MetadataValue.json([r.to_dict() for r in results]),
            }
        )

    except Exception as e:
        context.log.error(f"Comparison failed: {e}")
        return MaterializeResult(
            metadata={
                "error": str(e),
                "status": "failed",
            }
        )


@asset(
    key=["htr", "mobile_deployment"],
    group_name="htr_training",
    ins={"model_comparison": AssetIn(key=["htr", "model_comparison"])},
    compute_kind="python",
    description="Generate mobile deployment artifacts",
    metadata={
        "targets": "iphone_15_pro, pixel_8_pro, samsung_s24",
        "quantization": "int4, int8",
    },
)
def mobile_deployment(
    context,
    model_comparison: MaterializeResult,
) -> MaterializeResult:
    """
    Generate mobile deployment artifacts for best model.

    Creates:
    - GGUF quantized model (Q4_K_M, Q8_0)
    - CoreML model (iOS)
    - TFLite model (Android)
    - Deployment recommendations by device
    """
    context.log.info("Generating mobile deployment artifacts")

    try:
        from ocr.vlm_finetune_comparison import (
            MOBILE_TARGETS,
            VLMComparisonPipeline,
        )

        # Get recommendations
        pipeline = VLMComparisonPipeline(
            dataset_path="./irish_htr_dataset/unsloth",
            output_dir="./vlm_comparison",
        )
        recommendations = pipeline.get_mobile_recommendations()

        # Determine best model for each target
        deployment_plan = {}
        for device, models in recommendations.items():
            if models:
                deployment_plan[device] = {
                    "recommended_model": models[0]["model"],
                    "quantization": models[0]["quantization"],
                    "size_gb": models[0]["quantized_size_gb"],
                    "alternatives": [m["model"] for m in models[1:3]],
                }

        return MaterializeResult(
            metadata={
                "targets": list(MOBILE_TARGETS.keys()),
                "deployment_plan": MetadataValue.json(deployment_plan),
                "status": "recommendations_generated",
                "note": "GGUF/CoreML/TFLite export requires additional setup",
            }
        )

    except Exception as e:
        context.log.error(f"Mobile deployment failed: {e}")
        return MaterializeResult(
            metadata={
                "error": str(e),
                "status": "failed",
            }
        )


# Asset group for HTR training
htr_training_assets = [
    duchas_pages,
    segmented_lines,
    training_dataset,
    vlm_finetune,
    model_comparison,
    mobile_deployment,
]

# Job definition
htr_training_job = dg.define_asset_job(
    name="htr_training_job",
    selection=dg.AssetSelection.groups("htr_training"),
    description="End-to-end Irish HTR training pipeline",
)

# Daily schedule for incremental updates
htr_daily_schedule = dg.ScheduleDefinition(
    job=htr_training_job,
    cron_schedule="0 2 * * *",  # 2 AM daily
    description="Daily HTR dataset update and model evaluation",
)
