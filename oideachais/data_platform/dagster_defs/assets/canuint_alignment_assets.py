"""
Canuint Word-Level Alignment Assets.

Pipeline for extracting word-level forced alignment data from Canuint.ie
for training Irish ASR/TTS models.

Asset Hierarchy:
    canuint.alignment.word_alignments (DLT extraction)
    canuint.alignment.character_alignments (interpolation)
    canuint.alignment.phoneme_alignments (G2P conversion)
    canuint.alignment.audio_downloads (MP3 cache)
    canuint.alignment.audio_slices (word-level WAV clips)
    canuint.alignment.ljspeech_dataset (TTS format)
    canuint.alignment.huggingface_dataset (transformers format)
    canuint.alignment.embeddings (LanceDB vectors)

Storage:
    - DuckDB: Word/character/phoneme alignment metadata
    - Filesystem: Audio files (MP3 cache, WAV slices)
    - LanceDB: Text embeddings for similarity search
    - R2: Cloud backup of processed audio
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

from ..partitions import dialect_partitions
from ..resources import DuckDBResource, LanceDBResource

# ============================================================================
# Configuration
# ============================================================================

class CanuintAlignmentConfig(Config):
    """Configuration for Canuint alignment pipeline."""

    max_recordings: int = 1000
    min_duration_ms: int = 50
    max_duration_ms: int = 5000
    target_sample_rate: int = 16000
    word_padding_ms: int = 25
    preserve_digraphs: bool = False
    use_espeak: bool = True


# ============================================================================
# Data Extraction Assets
# ============================================================================

@asset(
    key=["canuint", "alignment", "word_alignments"],
    group_name="canuint_alignment",
    description="Word-level forced alignment data from Canuint.ie",
    compute_kind="dlt",
)
def canuint_word_alignments(
    context: AssetExecutionContext,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    config: CanuintAlignmentConfig,
) -> MaterializeResult:
    """
    Extract word-level alignment data from Canuint.ie.

    Output Schema:
        word_id: str (primary key, format: {recording_id}_{word_index})
        recording_id: str
        start_time: float (seconds)
        end_time: float (seconds)
        duration_ms: int
        dialectal_text: str (as spoken)
        standardized_text: str (standard Irish)
        speaker_name: str
        dialect: str (connacht/munster/ulster)
        province: str (Cúige...)
        area_name: str
        year: int
        audio_url: str

    Filters:
        - Duration: 50ms-5000ms (configurable)
        - Has both dialectal and standardized text
    """
    context.log.info(f"Extracting word alignments, max_recordings={config.max_recordings}")

    from dlt_sources.celtic.canuint import canuint_word_alignment_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="canuint_word_alignments",
        destination="duckdb",
        dataset_name="canuint_alignment",
    )

    source = canuint_word_alignment_source(
        max_recordings=config.max_recordings,
        min_duration_ms=config.min_duration_ms,
        max_duration_ms=config.max_duration_ms,
    )

    load_info = pipeline.run(source)

    row_counts = {}
    if pipeline.last_trace and pipeline.last_trace.last_normalize_info:
        row_counts = pipeline.last_trace.last_normalize_info.row_counts

    # Get dialect distribution
    conn = duckdb.get_connection()
    try:
        dialect_stats = conn.execute("""
            SELECT dialect, COUNT(*) as count
            FROM canuint_alignment.word_alignments
            GROUP BY dialect
        """).fetchall()
        dialects = {row[0]: row[1] for row in dialect_stats}
    except Exception:
        dialects = {}

    return MaterializeResult(
        metadata={
            "words_loaded": sum(row_counts.values()),
            "max_recordings": config.max_recordings,
            "duration_filter_ms": f"{config.min_duration_ms}-{config.max_duration_ms}",
            "dialect_distribution": dialects,
        }
    )


@asset(
    key=["canuint", "alignment", "recording_metadata"],
    group_name="canuint_alignment",
    description="Recording-level metadata from Canuint.ie",
    deps=[AssetKey(["canuint", "alignment", "word_alignments"])],
    compute_kind="duckdb",
)
def canuint_recording_metadata(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Aggregate recording-level metadata from word alignments.

    Creates summary table with:
        recording_id, speaker_name, dialect, province, area_name,
        word_count, total_duration_seconds, audio_url
    """
    context.log.info("Aggregating recording metadata")

    conn = duckdb.get_connection()

    conn.execute("""
        CREATE OR REPLACE TABLE canuint_alignment.recording_metadata AS
        SELECT
            recording_id,
            ANY_VALUE(speaker_name) as speaker_name,
            ANY_VALUE(dialect) as dialect,
            ANY_VALUE(province) as province,
            ANY_VALUE(area_name) as area_name,
            ANY_VALUE(year) as year,
            ANY_VALUE(audio_url) as audio_url,
            COUNT(*) as word_count,
            SUM(duration_ms) / 1000.0 as total_duration_seconds,
            MIN(start_time) as first_word_time,
            MAX(end_time) as last_word_time
        FROM canuint_alignment.word_alignments
        GROUP BY recording_id
    """)

    stats = conn.execute("""
        SELECT
            COUNT(*) as total_recordings,
            SUM(word_count) as total_words,
            SUM(total_duration_seconds) as total_hours,
            COUNT(DISTINCT speaker_name) as unique_speakers
        FROM canuint_alignment.recording_metadata
    """).fetchone()

    return MaterializeResult(
        metadata={
            "total_recordings": stats[0],
            "total_words": stats[1],
            "total_duration_hours": round(stats[2] / 3600, 2) if stats[2] else 0,
            "unique_speakers": stats[3],
        }
    )


# ============================================================================
# Alignment Processing Assets
# ============================================================================

@asset(
    key=["canuint", "alignment", "character_alignments"],
    group_name="canuint_alignment",
    description="Character-level timestamp interpolation",
    deps=[AssetKey(["canuint", "alignment", "word_alignments"])],
    compute_kind="python",
)
def canuint_character_alignments(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: CanuintAlignmentConfig,
) -> MaterializeResult:
    """
    Interpolate character-level timestamps from word alignments.

    Handles Irish-specific characters:
    - Fada vowels: á, é, í, ó, ú
    - Digraphs (optional): bh, ch, dh, fh, gh, mh, ph, sh, th

    Output compatible with ElevenLabs transcript format.
    """
    import json

    from alignment.character_interpolator import (
        create_character_alignment,
    )

    context.log.info(f"Generating character alignments, preserve_digraphs={config.preserve_digraphs}")

    conn = duckdb.get_connection()

    # Fetch word alignments
    words = conn.execute("""
        SELECT
            word_id, recording_id, dialectal_text,
            start_time, end_time, dialect
        FROM canuint_alignment.word_alignments
        WHERE dialectal_text IS NOT NULL
    """).fetchall()

    # Process each word
    alignments = []
    for word in words:
        word_id, recording_id, text, start_time, end_time, dialect = word

        alignment = create_character_alignment(
            word_id=word_id,
            recording_id=recording_id,
            text=text,
            start_time=start_time,
            end_time=end_time,
            dialect=dialect or "",
            preserve_digraphs=config.preserve_digraphs,
        )

        alignments.append({
            "word_id": alignment.word_id,
            "recording_id": alignment.recording_id,
            "text": alignment.text,
            "dialect": alignment.dialect,
            "characters": alignment.characters,
            "character_start_times": alignment.character_start_times,
            "character_end_times": alignment.character_end_times,
            "character_count": len(alignment.characters),
        })

    # Store in DuckDB
    if alignments:
        conn.execute("""
            CREATE OR REPLACE TABLE canuint_alignment.character_alignments (
                word_id VARCHAR PRIMARY KEY,
                recording_id VARCHAR,
                text VARCHAR,
                dialect VARCHAR,
                characters JSON,
                character_start_times JSON,
                character_end_times JSON,
                character_count INTEGER
            )
        """)

        conn.executemany("""
            INSERT INTO canuint_alignment.character_alignments VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (a["word_id"], a["recording_id"], a["text"], a["dialect"],
             json.dumps(a["characters"]), json.dumps(a["character_start_times"]),
             json.dumps(a["character_end_times"]), a["character_count"])
            for a in alignments
        ])

    return MaterializeResult(
        metadata={
            "alignments_created": len(alignments),
            "preserve_digraphs": config.preserve_digraphs,
            "total_characters": sum(a["character_count"] for a in alignments),
        }
    )


@asset(
    key=["canuint", "alignment", "phoneme_alignments"],
    group_name="canuint_alignment",
    description="Phoneme-level G2P conversion with dialect awareness",
    deps=[AssetKey(["canuint", "alignment", "word_alignments"])],
    compute_kind="python",
)
def canuint_phoneme_alignments(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: CanuintAlignmentConfig,
) -> MaterializeResult:
    """
    Convert word text to phonemes using espeak-ng or rule-based fallback.

    Dialect-aware processing:
    - Ulster: /ao/ → /eː/, /á/ → /æː/
    - Munster: /ao/ → /eː/, /ia/ → /iːə/
    - Connacht: closest to standard

    Output: IPA phonemes with interpolated timestamps.
    """
    import json

    from alignment.irish_g2p import (
        PhonemeFormat,
        create_phoneme_alignment,
    )

    context.log.info(f"Generating phoneme alignments, use_espeak={config.use_espeak}")

    conn = duckdb.get_connection()

    # Fetch word alignments
    words = conn.execute("""
        SELECT
            word_id, recording_id, dialectal_text,
            start_time, end_time, dialect
        FROM canuint_alignment.word_alignments
        WHERE dialectal_text IS NOT NULL
    """).fetchall()

    # Process each word
    alignments = []
    for word in words:
        word_id, recording_id, text, start_time, end_time, dialect = word

        alignment = create_phoneme_alignment(
            word_id=word_id,
            recording_id=recording_id,
            text=text,
            start_time=start_time,
            end_time=end_time,
            dialect=dialect or "",
            phoneme_format=PhonemeFormat.IPA,
            use_espeak=config.use_espeak,
        )

        alignments.append({
            "word_id": alignment.word_id,
            "recording_id": alignment.recording_id,
            "text": alignment.text,
            "dialect": alignment.dialect,
            "phonemes": alignment.phonemes,
            "phoneme_format": alignment.phoneme_format,
            "phoneme_start_times": alignment.phoneme_start_times,
            "phoneme_end_times": alignment.phoneme_end_times,
            "phoneme_count": len(alignment.phonemes),
        })

    # Store in DuckDB
    if alignments:
        conn.execute("""
            CREATE OR REPLACE TABLE canuint_alignment.phoneme_alignments (
                word_id VARCHAR PRIMARY KEY,
                recording_id VARCHAR,
                text VARCHAR,
                dialect VARCHAR,
                phonemes JSON,
                phoneme_format VARCHAR,
                phoneme_start_times JSON,
                phoneme_end_times JSON,
                phoneme_count INTEGER
            )
        """)

        conn.executemany("""
            INSERT INTO canuint_alignment.phoneme_alignments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (a["word_id"], a["recording_id"], a["text"], a["dialect"],
             json.dumps(a["phonemes"]), a["phoneme_format"],
             json.dumps(a["phoneme_start_times"]), json.dumps(a["phoneme_end_times"]),
             a["phoneme_count"])
            for a in alignments
        ])

    return MaterializeResult(
        metadata={
            "alignments_created": len(alignments),
            "use_espeak": config.use_espeak,
            "total_phonemes": sum(a["phoneme_count"] for a in alignments),
        }
    )


# ============================================================================
# Audio Processing Assets
# ============================================================================

@asset(
    key=["canuint", "alignment", "audio_slices"],
    group_name="canuint_alignment",
    description="Word-level audio clips sliced from recordings",
    deps=[AssetKey(["canuint", "alignment", "word_alignments"])],
    partitions_def=dialect_partitions,
    compute_kind="audio",
)
def canuint_audio_slices(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    config: CanuintAlignmentConfig,
) -> MaterializeResult:
    """
    Download recordings and slice at word boundaries.

    Output:
    - 16kHz mono WAV files
    - Organized by dialect: {output_dir}/{dialect}/{word_id}.wav
    - Cached MP3s for re-processing

    Uses pydub with ffmpeg backend.
    """
    from pipelines.canuint_audio_slicer import CanuintAudioSlicer

    dialect = context.partition_key

    # Map partition to province filter
    province_map = {
        "munster": "Cúige Mumhan",
        "connacht": "Cúige Connacht",
        "ulster": "Cúige Uladh",
        "standard": "Caighdeán Oifigiúil",
    }

    context.log.info(f"Slicing audio for dialect: {dialect}")

    conn = duckdb.get_connection()

    # Get alignments for this dialect
    province = province_map.get(dialect, dialect)
    alignments = conn.execute("""
        SELECT
            word_id, recording_id, dialectal_text, dialect,
            start_time, end_time, audio_url, speaker_name
        FROM canuint_alignment.word_alignments
        WHERE province = ?
        ORDER BY recording_id, start_time
    """, [province]).fetchall()

    if not alignments:
        return MaterializeResult(
            metadata={
                "dialect": dialect,
                "slices_created": 0,
                "error": "No alignments found for dialect",
            }
        )

    # Convert to dict format
    word_alignments = [
        {
            "word_id": a[0],
            "recording_id": a[1],
            "dialectal_text": a[2],
            "dialect": a[3],
            "start_time": a[4],
            "end_time": a[5],
            "audio_url": a[6],
            "speaker_name": a[7],
        }
        for a in alignments
    ]

    # Setup slicer
    output_dir = Path(f"data/canuint_audio/{dialect}")
    cache_dir = Path("data/canuint_cache")

    slicer = CanuintAudioSlicer(
        output_dir=output_dir,
        cache_dir=cache_dir,
        target_sample_rate=config.target_sample_rate,
        word_padding_ms=config.word_padding_ms,
        min_duration_ms=config.min_duration_ms,
        max_duration_ms=config.max_duration_ms,
    )

    # Process all alignments
    slices = list(slicer.process_all_alignments(word_alignments))
    stats = slicer.get_stats()

    # Update DuckDB with audio paths
    if slices:
        for slice_obj in slices:
            conn.execute("""
                UPDATE canuint_alignment.word_alignments
                SET audio_path = ?
                WHERE word_id = ?
            """, [str(slice_obj.audio_path), slice_obj.word_id])

    return MaterializeResult(
        metadata={
            "dialect": dialect,
            "slices_created": stats["total_slices"],
            "recordings_processed": stats["total_recordings"],
            "successful_downloads": stats["successful_downloads"],
            "failed_downloads": stats["failed_downloads"],
            "skipped_too_short": stats["skipped_too_short"],
            "skipped_too_long": stats["skipped_too_long"],
            "total_duration_seconds": round(stats["total_duration_seconds"], 2),
            "output_dir": str(output_dir),
        }
    )


# ============================================================================
# Export Assets
# ============================================================================

@asset(
    key=["canuint", "alignment", "ljspeech_dataset"],
    group_name="canuint_alignment",
    description="LJSpeech-format dataset for TTS training",
    deps=[
        AssetKey(["canuint", "alignment", "word_alignments"]),
        AssetKey(["canuint", "alignment", "audio_slices"]),
    ],
    compute_kind="export",
)
def canuint_ljspeech_dataset(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Export dataset in LJSpeech format for TTS training.

    Output:
    - metadata.csv: filename|raw_text|normalized_text
    - wavs/: Audio files (16kHz mono WAV)

    Compatible with Chatterbox, Tacotron, VITS trainers.
    """
    from alignment.canuint_exporter import export_ljspeech

    context.log.info("Exporting LJSpeech dataset")

    conn = duckdb.get_connection()

    # Get alignments with audio paths
    alignments = conn.execute("""
        SELECT
            word_id, recording_id, dialectal_text as text,
            audio_path, dialect, speaker_name
        FROM canuint_alignment.word_alignments
        WHERE audio_path IS NOT NULL
    """).fetchall()

    alignment_dicts = [
        {
            "word_id": a[0],
            "recording_id": a[1],
            "text": a[2],
            "audio_path": a[3],
            "dialect": a[4],
            "speaker_name": a[5],
        }
        for a in alignments
    ]

    output_dir = Path("data/canuint_ljspeech")
    output_dir.mkdir(parents=True, exist_ok=True)

    count = export_ljspeech(
        alignment_dicts,
        output_dir / "metadata.csv",
        use_relative_paths=True,
        wavs_dir=Path("data/canuint_audio"),
    )

    return MaterializeResult(
        metadata={
            "entries_exported": count,
            "output_path": str(output_dir / "metadata.csv"),
            "format": "filename|raw_text|normalized_text",
        }
    )


@asset(
    key=["canuint", "alignment", "huggingface_dataset"],
    group_name="canuint_alignment",
    description="HuggingFace datasets format export",
    deps=[
        AssetKey(["canuint", "alignment", "word_alignments"]),
        AssetKey(["canuint", "alignment", "character_alignments"]),
        AssetKey(["canuint", "alignment", "phoneme_alignments"]),
        AssetKey(["canuint", "alignment", "audio_slices"]),
    ],
    compute_kind="export",
)
def canuint_huggingface_dataset(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Export complete dataset in HuggingFace format.

    Output:
    - data/train.jsonl, validation.jsonl, test.jsonl
    - dataset_info.json
    - README.md (dataset card)

    Compatible with transformers, datasets library.
    """
    from alignment.canuint_exporter import export_huggingface_dataset

    context.log.info("Exporting HuggingFace dataset")

    conn = duckdb.get_connection()

    # Get complete alignments
    alignments = conn.execute("""
        SELECT
            w.word_id, w.recording_id, w.dialectal_text as text,
            w.audio_path, w.dialect, w.speaker_name,
            w.start_time, w.end_time, w.duration_ms
        FROM canuint_alignment.word_alignments w
        WHERE w.audio_path IS NOT NULL
    """).fetchall()

    alignment_dicts = [
        {
            "word_id": a[0],
            "recording_id": a[1],
            "text": a[2],
            "audio_path": a[3],
            "dialect": a[4],
            "speaker_name": a[5],
            "start_time": a[6],
            "end_time": a[7],
            "duration_ms": a[8],
        }
        for a in alignments
    ]

    output_dir = Path("data/canuint_huggingface")
    stats = export_huggingface_dataset(
        alignment_dicts,
        output_dir,
        dataset_name="canuint_irish_speech",
    )

    return MaterializeResult(
        metadata={
            "total_examples": stats["total"],
            "train_examples": stats["train"],
            "validation_examples": stats["validation"],
            "test_examples": stats["test"],
            "dialect_distribution": stats["dialects"],
            "output_dir": str(output_dir),
        }
    )


@asset(
    key=["canuint", "alignment", "multi_format_export"],
    group_name="canuint_alignment",
    description="Export to all formats (LJSpeech, CTM, TextGrid, HF)",
    deps=[
        AssetKey(["canuint", "alignment", "word_alignments"]),
        AssetKey(["canuint", "alignment", "character_alignments"]),
        AssetKey(["canuint", "alignment", "phoneme_alignments"]),
        AssetKey(["canuint", "alignment", "audio_slices"]),
    ],
    compute_kind="export",
)
def canuint_multi_format_export(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Export all alignment data to multiple formats.

    Formats:
    - LJSpeech: TTS training (Chatterbox, VITS)
    - CTM: ASR training (Kaldi, ESPnet)
    - TextGrid: Acoustic analysis (Praat, MFA)
    - Character JSON: Fine-grained ASR (Whisper)
    - Phoneme JSON: Phonetic research
    - HuggingFace: ML pipeline integration
    """
    import json

    from alignment.canuint_exporter import export_all_formats

    context.log.info("Exporting to all formats")

    conn = duckdb.get_connection()

    # Get word alignments
    word_rows = conn.execute("""
        SELECT * FROM canuint_alignment.word_alignments
    """).fetchall()
    word_cols = [desc[0] for desc in conn.description]
    word_alignments = [dict(zip(word_cols, row)) for row in word_rows]

    # Get character alignments
    try:
        char_rows = conn.execute("""
            SELECT * FROM canuint_alignment.character_alignments
        """).fetchall()
        char_cols = [desc[0] for desc in conn.description]
        character_alignments = []
        for row in char_rows:
            d = dict(zip(char_cols, row))
            # Parse JSON fields
            d["characters"] = json.loads(d["characters"]) if isinstance(d["characters"], str) else d["characters"]
            d["character_start_times"] = json.loads(d["character_start_times"]) if isinstance(d["character_start_times"], str) else d["character_start_times"]
            d["character_end_times"] = json.loads(d["character_end_times"]) if isinstance(d["character_end_times"], str) else d["character_end_times"]
            character_alignments.append(d)
    except Exception:
        character_alignments = []

    # Get phoneme alignments
    try:
        phoneme_rows = conn.execute("""
            SELECT * FROM canuint_alignment.phoneme_alignments
        """).fetchall()
        phoneme_cols = [desc[0] for desc in conn.description]
        phoneme_alignments = []
        for row in phoneme_rows:
            d = dict(zip(phoneme_cols, row))
            d["phonemes"] = json.loads(d["phonemes"]) if isinstance(d["phonemes"], str) else d["phonemes"]
            d["phoneme_start_times"] = json.loads(d["phoneme_start_times"]) if isinstance(d["phoneme_start_times"], str) else d["phoneme_start_times"]
            d["phoneme_end_times"] = json.loads(d["phoneme_end_times"]) if isinstance(d["phoneme_end_times"], str) else d["phoneme_end_times"]
            phoneme_alignments.append(d)
    except Exception:
        phoneme_alignments = []

    output_dir = Path("data/canuint_export")
    stats = export_all_formats(
        word_alignments=word_alignments,
        character_alignments=character_alignments,
        phoneme_alignments=phoneme_alignments,
        output_dir=output_dir,
    )

    return MaterializeResult(
        metadata={
            "total_items": stats.total_items,
            "train_count": stats.train_count,
            "val_count": stats.val_count,
            "test_count": stats.test_count,
            "formats_exported": stats.formats_exported,
            "total_duration_hours": round(stats.total_duration_seconds / 3600, 2),
            "dialect_distribution": stats.dialects,
            "output_dir": str(output_dir),
        }
    )


# ============================================================================
# Embedding Assets
# ============================================================================

@asset(
    key=["canuint", "alignment", "embeddings"],
    group_name="canuint_alignment",
    description="Text embeddings for word alignment search",
    deps=[AssetKey(["canuint", "alignment", "word_alignments"])],
    compute_kind="embedding",
)
def canuint_alignment_embeddings(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Generate embeddings for word alignments.

    Stores in LanceDB table: canuint.word_alignments

    Enables:
    - Semantic search for similar words
    - Pronunciation variant discovery
    - Dialect comparison analysis
    """
    from sentence_transformers import SentenceTransformer

    context.log.info("Generating word alignment embeddings")

    conn = duckdb.get_connection()
    db = lancedb.get_db()
    model = SentenceTransformer(lancedb.embedding_model)

    # Fetch word data
    words = conn.execute("""
        SELECT
            word_id, recording_id, dialectal_text, standardized_text,
            dialect, speaker_name, start_time, end_time
        FROM canuint_alignment.word_alignments
        WHERE dialectal_text IS NOT NULL
        LIMIT 10000
    """).fetchall()

    if not words:
        return MaterializeResult(
            metadata={"embedded": 0, "error": "No words to embed"}
        )

    # Prepare texts combining dialectal and standardized forms
    texts = [
        f"{w[2]} ({w[3]})" if w[3] else w[2]
        for w in words
    ]

    # Batch embed (critical for performance per CLAUDE.md)
    context.log.info(f"Embedding {len(texts)} words in batches of 100")
    embeddings = model.encode(texts, batch_size=100, show_progress_bar=True)

    # Prepare data for LanceDB
    data = [
        {
            "word_id": w[0],
            "recording_id": w[1],
            "dialectal_text": w[2],
            "standardized_text": w[3],
            "dialect": w[4],
            "speaker_name": w[5],
            "start_time": w[6],
            "end_time": w[7],
            "text": texts[i],
            "vector": embeddings[i].tolist(),
        }
        for i, w in enumerate(words)
    ]

    # Store in LanceDB
    table_name = "canuint.word_alignments"
    if table_name in db.table_names():
        # Drop and recreate to avoid HNSW index issues
        db.drop_table(table_name)

    db.create_table(table_name, data)

    return MaterializeResult(
        metadata={
            "words_embedded": len(data),
            "embedding_model": lancedb.embedding_model,
            "table_name": table_name,
            "dialect_counts": {
                d: sum(1 for item in data if item["dialect"] == d)
                for d in set(item["dialect"] for item in data)
            },
        }
    )


# ============================================================================
# Export All Assets
# ============================================================================

canuint_alignment_assets = [
    canuint_word_alignments,
    canuint_recording_metadata,
    canuint_character_alignments,
    canuint_phoneme_alignments,
    canuint_audio_slices,
    canuint_ljspeech_dataset,
    canuint_huggingface_dataset,
    canuint_multi_format_export,
    canuint_alignment_embeddings,
]
