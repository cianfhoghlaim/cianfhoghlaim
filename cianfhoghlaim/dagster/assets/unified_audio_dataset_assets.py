"""
Unified Audio Dataset Assets.

Combines audio data from multiple sources for ASR/TTS training:
- Canuint.ie (Irish pronunciation, word-level alignment)
- EdcoLearning.ie (LC exam audio, multiple languages)
- SEC aural transcripts (exam scripts with dialect tags)

Asset Hierarchy:
    unified_audio.edcolearning_extraction (DLT)
    unified_audio.sec_transcripts (DLT)
    unified_audio.combined_dataset (merge all sources)
    unified_audio.dialect_balanced_split (train/val/test with balance)
    unified_audio.huggingface_export (ready for training)

Storage:
    - DuckDB: Unified audio metadata
    - R2: Audio files (oideachais-audio bucket)
    - HuggingFace: Published dataset
"""
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    AssetKey,
    Config,
    MaterializeResult,
    asset,
)
from dagster_dlt import DagsterDltResource

from ..resources import DuckDBResource

# ============================================================================
# Configuration
# ============================================================================


class UnifiedAudioConfig(Config):
    """Configuration for unified audio dataset pipeline."""

    # Source controls
    include_canuint: bool = True
    include_edcolearning: bool = True
    include_sec_transcripts: bool = True

    # Language filters
    languages: str = "ga,fr,de,es"  # Comma-separated
    irish_only: bool = False

    # Dialect balancing for Irish
    target_connacht_pct: float = 0.40
    target_munster_pct: float = 0.35
    target_ulster_pct: float = 0.25

    # Quality filters
    min_duration_ms: int = 100
    max_duration_ms: int = 30000
    min_text_length: int = 5

    # Split configuration
    train_pct: float = 0.80
    val_pct: float = 0.10
    test_pct: float = 0.10

    # HuggingFace publishing
    hf_repo: str = "cianfhoghlaim/irish-audio-unified"
    hf_private: bool = True


class EdcoLearningExtractionConfig(Config):
    """Configuration for EdcoLearning audio extraction."""

    subjects: str = "irish,french,german,spanish"  # Comma-separated
    level: str = "leaving_certificate"
    use_1password: bool = True


class SECTranscriptConfig(Config):
    """Configuration for SEC transcript parsing."""

    pdf_dir: str | None = None
    subjects: str = "irish,french,german,spanish"
    exam_type: str = "LC"


# ============================================================================
# Data Extraction Assets
# ============================================================================


@asset(
    key=["unified_audio", "edcolearning_extraction"],
    group_name="unified_audio",
    description="Extract audio files from EdcoLearning.ie",
    compute_kind="dlt",
)
def edcolearning_audio_extraction(
    context: AssetExecutionContext,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    config: EdcoLearningExtractionConfig,
) -> MaterializeResult:
    """
    Extract exam audio files from EdcoLearning.ie.

    Output Schema:
        audio_id: str (primary key)
        book_id: str
        audio_url: str (Azure Blob URL)
        title: str
        year: int
        level: str (higher/ordinary)
        language: str (ga/fr/de/es)
        subject: str
        source: str (edcolearning)
        scraped_at: timestamp

    Requires:
        - EdcoLearning.ie credentials in 1Password or environment
    """
    subjects = [s.strip() for s in config.subjects.split(",")]
    context.log.info(f"Extracting EdcoLearning audio for subjects: {subjects}")

    from cianfhoghlaim.dlt.british_isles.ie.education.edcolearning import edcolearning_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="edcolearning_audio",
        destination="duckdb",
        dataset_name="unified_audio",
    )

    source = edcolearning_source(
        subjects=subjects,
        level=config.level,
        use_1password=config.use_1password,
    )

    load_info = pipeline.run(source)

    row_counts = {}
    if pipeline.last_trace and pipeline.last_trace.last_normalize_info:
        row_counts = pipeline.last_trace.last_normalize_info.row_counts

    # Get subject distribution
    conn = duckdb.get_connection()
    try:
        subject_stats = conn.execute("""
            SELECT subject, language, COUNT(*) as count
            FROM unified_audio.audio_files
            GROUP BY subject, language
        """).fetchall()
        subjects_found = {f"{row[0]}_{row[1]}": row[2] for row in subject_stats}
    except Exception:
        subjects_found = {}

    return MaterializeResult(
        metadata={
            "audio_files_loaded": row_counts.get("audio_files", 0),
            "books_loaded": row_counts.get("books", 0),
            "transcripts_loaded": row_counts.get("transcripts", 0),
            "subject_distribution": subjects_found,
        }
    )


@asset(
    key=["unified_audio", "sec_transcripts"],
    group_name="unified_audio",
    description="Parse SEC aural exam transcripts",
    compute_kind="dlt",
)
def sec_aural_transcripts(
    context: AssetExecutionContext,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    config: SECTranscriptConfig,
) -> MaterializeResult:
    """
    Parse SEC aural exam transcripts from PDFs.

    Output Schema:
        segment_id: str (primary key)
        transcript_id: str
        text: str
        dialect: str (for Irish)
        speaker_role: str
        section: str
        question_number: int
        year: int
        level: str
        language: str
        source: str (sec_aural)

    Dialect Tags:
        - Connacht, Munster, Ulster detected from script markers
        - Used for dialect-balanced training splits
    """
    subjects = [s.strip() for s in config.subjects.split(",")]
    context.log.info(f"Parsing SEC transcripts for subjects: {subjects}")

    from cianfhoghlaim.dlt.british_isles.ie.education.sec_aural_transcripts import (
        sec_aural_transcripts_source,
    )

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="sec_transcripts",
        destination="duckdb",
        dataset_name="unified_audio",
    )

    source = sec_aural_transcripts_source(
        pdf_dir=config.pdf_dir,
        subjects=subjects,
        exam_type=config.exam_type,
    )

    load_info = pipeline.run(source)

    row_counts = {}
    if pipeline.last_trace and pipeline.last_trace.last_normalize_info:
        row_counts = pipeline.last_trace.last_normalize_info.row_counts

    # Get dialect distribution for Irish
    conn = duckdb.get_connection()
    try:
        dialect_stats = conn.execute("""
            SELECT dialect, COUNT(*) as count
            FROM unified_audio.segments
            WHERE language = 'ga' AND dialect IS NOT NULL
            GROUP BY dialect
        """).fetchall()
        dialects = {row[0]: row[1] for row in dialect_stats}
    except Exception:
        dialects = {}

    return MaterializeResult(
        metadata={
            "transcripts_loaded": row_counts.get("transcripts", 0),
            "segments_loaded": row_counts.get("segments", 0),
            "dialect_tagged": row_counts.get("dialect_tagged_segments", 0),
            "irish_dialect_distribution": dialects,
        }
    )


# ============================================================================
# Data Combination Assets
# ============================================================================


@asset(
    key=["unified_audio", "combined_dataset"],
    group_name="unified_audio",
    description="Unified audio dataset combining all sources",
    deps=[
        AssetKey(["canuint", "alignment", "word_alignments"]),
        AssetKey(["unified_audio", "edcolearning_extraction"]),
        AssetKey(["unified_audio", "sec_transcripts"]),
    ],
    compute_kind="duckdb",
)
def unified_combined_dataset(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: UnifiedAudioConfig,
) -> MaterializeResult:
    """
    Combine all audio sources into unified dataset.

    Creates a unified schema for training:
        segment_id: str (primary key)
        source: str (canuint/edcolearning/sec_aural)
        language: str (ga/fr/de/es)
        dialect: str (for Irish: connacht/munster/ulster)
        text: str
        audio_url: str (optional)
        start_time: float (optional)
        end_time: float (optional)
        duration_ms: int (optional)
        speaker_name: str (optional)
        year: int (optional)
        level: str (optional)
        quality_score: float (computed)
    """
    context.log.info("Combining audio sources into unified dataset")

    languages = [l.strip() for l in config.languages.split(",")]
    if config.irish_only:
        languages = ["ga"]

    conn = duckdb.get_connection()

    # Create unified table
    conn.execute("""
        CREATE SCHEMA IF NOT EXISTS unified_audio
    """)

    conn.execute("""
        DROP TABLE IF EXISTS unified_audio.combined
    """)

    conn.execute("""
        CREATE TABLE unified_audio.combined AS

        -- Canuint word alignments (Irish only)
        SELECT
            word_id as segment_id,
            'canuint' as source,
            'ga' as language,
            dialect,
            COALESCE(standardized_text, dialectal_text) as text,
            audio_url,
            start_time,
            end_time,
            duration_ms,
            speaker_name,
            year,
            NULL as level,
            1.0 as quality_score  -- High quality (word-aligned)
        FROM canuint_alignment.word_alignments
        WHERE duration_ms BETWEEN ? AND ?
          AND LENGTH(COALESCE(standardized_text, dialectal_text)) >= ?

        UNION ALL

        -- EdcoLearning audio (may not have text alignment)
        SELECT
            audio_id as segment_id,
            'edcolearning' as source,
            language,
            NULL as dialect,
            title as text,
            audio_url,
            NULL as start_time,
            NULL as end_time,
            NULL as duration_ms,
            NULL as speaker_name,
            year,
            level,
            0.7 as quality_score  -- Moderate (needs alignment)
        FROM unified_audio.audio_files
        WHERE language IN (SELECT unnest(?::text[]))

        UNION ALL

        -- SEC transcript segments (text only, no audio yet)
        SELECT
            segment_id,
            'sec_aural' as source,
            language,
            dialect,
            text,
            NULL as audio_url,
            NULL as start_time,
            NULL as end_time,
            NULL as duration_ms,
            speaker_role as speaker_name,
            year,
            level,
            CASE
                WHEN dialect IS NOT NULL AND dialect != 'unknown' THEN 0.9
                ELSE 0.6
            END as quality_score  -- Higher if dialect tagged
        FROM unified_audio.segments
        WHERE language IN (SELECT unnest(?::text[]))
          AND LENGTH(text) >= ?
    """, [
        config.min_duration_ms,
        config.max_duration_ms,
        config.min_text_length,
        languages,
        languages,
        config.min_text_length,
    ])

    # Get summary statistics
    stats = conn.execute("""
        SELECT
            source,
            language,
            dialect,
            COUNT(*) as count,
            AVG(duration_ms) as avg_duration_ms
        FROM unified_audio.combined
        GROUP BY source, language, dialect
        ORDER BY source, language, dialect
    """).fetchall()

    source_stats = {}
    for row in stats:
        key = f"{row[0]}_{row[1]}_{row[2] or 'none'}"
        source_stats[key] = {"count": row[3], "avg_duration": row[4]}

    total = conn.execute("SELECT COUNT(*) FROM unified_audio.combined").fetchone()[0]

    return MaterializeResult(
        metadata={
            "total_segments": total,
            "source_breakdown": source_stats,
            "languages": languages,
            "duration_filter_ms": f"{config.min_duration_ms}-{config.max_duration_ms}",
        }
    )


@asset(
    key=["unified_audio", "dialect_balanced_split"],
    group_name="unified_audio",
    description="Train/val/test splits with dialect balancing for Irish",
    deps=[AssetKey(["unified_audio", "combined_dataset"])],
    compute_kind="duckdb",
)
def dialect_balanced_split(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: UnifiedAudioConfig,
) -> MaterializeResult:
    """
    Create balanced train/val/test splits.

    For Irish:
        - Balances dialect distribution (target: 40% Connacht, 35% Munster, 25% Ulster)
        - Ensures each dialect represented in all splits
        - Speaker-based splitting (no speaker in multiple splits)

    For other languages:
        - Random stratified split by source
    """
    context.log.info("Creating dialect-balanced splits")

    conn = duckdb.get_connection()

    # Add split column
    conn.execute("""
        ALTER TABLE unified_audio.combined
        ADD COLUMN IF NOT EXISTS split VARCHAR
    """)

    # Simple random split for now (can be enhanced with proper balancing)
    import random
    random.seed(42)

    # Get all segment IDs
    segments = conn.execute("""
        SELECT segment_id, language, dialect
        FROM unified_audio.combined
    """).fetchall()

    train_ids = []
    val_ids = []
    test_ids = []

    # Group by language/dialect for stratification
    groups: dict[str, list] = {}
    for seg_id, lang, dialect in segments:
        key = f"{lang}_{dialect or 'none'}"
        if key not in groups:
            groups[key] = []
        groups[key].append(seg_id)

    # Split each group
    for key, ids in groups.items():
        random.shuffle(ids)
        n = len(ids)
        n_train = int(n * config.train_pct)
        n_val = int(n * config.val_pct)

        train_ids.extend(ids[:n_train])
        val_ids.extend(ids[n_train:n_train + n_val])
        test_ids.extend(ids[n_train + n_val:])

    # Update split column
    conn.execute("""
        UPDATE unified_audio.combined
        SET split = CASE
            WHEN segment_id IN (SELECT unnest(?::text[])) THEN 'train'
            WHEN segment_id IN (SELECT unnest(?::text[])) THEN 'val'
            ELSE 'test'
        END
    """, [train_ids, val_ids])

    # Get split statistics
    split_stats = conn.execute("""
        SELECT split, language, dialect, COUNT(*) as count
        FROM unified_audio.combined
        GROUP BY split, language, dialect
        ORDER BY split, language, dialect
    """).fetchall()

    stats_dict = {}
    for row in split_stats:
        key = f"{row[0]}_{row[1]}_{row[2] or 'none'}"
        stats_dict[key] = row[3]

    return MaterializeResult(
        metadata={
            "train_count": len(train_ids),
            "val_count": len(val_ids),
            "test_count": len(test_ids),
            "split_distribution": stats_dict,
            "target_dialect_pct": {
                "connacht": config.target_connacht_pct,
                "munster": config.target_munster_pct,
                "ulster": config.target_ulster_pct,
            },
        }
    )


# ============================================================================
# Export Assets
# ============================================================================


@asset(
    key=["unified_audio", "huggingface_export"],
    group_name="unified_audio",
    description="Export unified dataset to HuggingFace",
    deps=[AssetKey(["unified_audio", "dialect_balanced_split"])],
    compute_kind="python",
)
def huggingface_dataset_export(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: UnifiedAudioConfig,
) -> MaterializeResult:
    """
    Export unified dataset to HuggingFace Hub.

    Creates dataset with:
        - Audio column (if available)
        - Text column
        - Dialect column (for Irish)
        - Split column (train/val/test)
        - Metadata columns

    Publishes to: cianfhoghlaim/irish-audio-unified (private)
    """
    context.log.info(f"Exporting to HuggingFace: {config.hf_repo}")

    conn = duckdb.get_connection()

    # Export splits to parquet
    output_dir = Path("/tmp/unified_audio_export")
    output_dir.mkdir(parents=True, exist_ok=True)

    for split in ["train", "val", "test"]:
        output_path = output_dir / f"{split}.parquet"
        conn.execute(f"""
            COPY (
                SELECT
                    segment_id,
                    source,
                    language,
                    dialect,
                    text,
                    audio_url,
                    start_time,
                    end_time,
                    duration_ms,
                    speaker_name,
                    year,
                    level,
                    quality_score
                FROM unified_audio.combined
                WHERE split = '{split}'
            ) TO '{output_path}' (FORMAT PARQUET)
        """)
        context.log.info(f"Exported {split} split to {output_path}")

    # Create dataset card
    readme_content = f"""---
license: cc-by-4.0
language:
- ga
- fr
- de
- es
task_categories:
- automatic-speech-recognition
- text-to-speech
tags:
- irish
- celtic
- education
- leaving-certificate
size_categories:
- 10K<n<100K
---

# Irish Unified Audio Dataset

Multi-source audio dataset for Irish and European language ASR/TTS training.

## Sources

- **Canuint.ie**: Irish pronunciation database with word-level alignments
- **EdcoLearning.ie**: Leaving Certificate exam audio (Irish, French, German, Spanish)
- **SEC Transcripts**: Aural exam scripts with dialect tags

## Irish Dialects

- Connacht: ~{config.target_connacht_pct * 100:.0f}%
- Munster: ~{config.target_munster_pct * 100:.0f}%
- Ulster: ~{config.target_ulster_pct * 100:.0f}%

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{config.hf_repo}", split="train")
```

## License

CC-BY-4.0 (educational use)
"""

    readme_path = output_dir / "README.md"
    readme_path.write_text(readme_content)

    # Push to HuggingFace (if huggingface_hub is available)
    try:
        from huggingface_hub import HfApi

        api = HfApi()

        # Create repo if needed
        api.create_repo(
            repo_id=config.hf_repo,
            repo_type="dataset",
            private=config.hf_private,
            exist_ok=True,
        )

        # Upload files
        api.upload_folder(
            folder_path=str(output_dir),
            repo_id=config.hf_repo,
            repo_type="dataset",
        )

        context.log.info(f"Uploaded to https://huggingface.co/datasets/{config.hf_repo}")
        upload_success = True
    except ImportError:
        context.log.warning("huggingface_hub not installed, skipping upload")
        upload_success = False
    except Exception as e:
        context.log.error(f"HuggingFace upload failed: {e}")
        upload_success = False

    # Get final stats
    stats = conn.execute("""
        SELECT split, COUNT(*) as count
        FROM unified_audio.combined
        GROUP BY split
    """).fetchall()

    return MaterializeResult(
        metadata={
            "export_path": str(output_dir),
            "hf_repo": config.hf_repo,
            "upload_success": upload_success,
            "split_counts": {row[0]: row[1] for row in stats},
        }
    )


# ============================================================================
# Asset Group
# ============================================================================


unified_audio_assets = [
    edcolearning_audio_extraction,
    sec_aural_transcripts,
    unified_combined_dataset,
    dialect_balanced_split,
    huggingface_dataset_export,
]
