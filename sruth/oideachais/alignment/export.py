"""
Dataset Export Utilities for Bilingual Aligned Corpus.

Export formats compatible with meaisínfhoghlaim training pipelines:
- JSONL Chat: For translation/instruction-following fine-tuning
- Parquet: For efficient data storage and processing
- HuggingFace Datasets: Direct upload to HF Hub
- TMX: Translation Memory eXchange for CAT tools

Based on formats from meaisínfhoghlaim/catalog/sources.yaml.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from pathlib import Path

from .aligner import AlignmentResult, ParallelPair

# System prompts for different task types
TRANSLATION_SYSTEM_PROMPT = """You are a bilingual Irish-English translator specializing in educational content.
Translate the following text accurately while preserving educational terminology and context."""

IRISH_SYSTEM_PROMPT = """Is aistritheoir dátheangach Gaeilge-Béarla thú a dhíríonn ar ábhar oideachais.
Aistrigh an téacs seo a leanas go cruinn agus téarmaíocht oideachais á caomhnú."""


def export_to_jsonl(
    pairs: Sequence[ParallelPair],
    output_path: Path | str,
    direction: str = "en2ga",
    include_system_prompt: bool = True,
    format_type: str = "chat",
) -> int:
    """
    Export aligned pairs to JSONL format for LLM training.

    Args:
        pairs: List of ParallelPair objects
        output_path: Output file path
        direction: Translation direction ("en2ga" or "ga2en")
        include_system_prompt: Include system prompt in each example
        format_type: "chat" for messages format, "simple" for input/output

    Returns:
        Number of pairs exported
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for pair in pairs:
            if format_type == "chat":
                record = _to_chat_format(pair, direction, include_system_prompt)
            else:
                record = _to_simple_format(pair, direction)

            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


def export_to_parquet(
    pairs: Sequence[ParallelPair],
    output_path: Path | str,
    partition_by: str | None = None,
) -> int:
    """
    Export aligned pairs to Parquet format.

    Args:
        pairs: List of ParallelPair objects
        output_path: Output file path
        partition_by: Optional column to partition by

    Returns:
        Number of pairs exported
    """
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        raise ImportError("pyarrow required for Parquet export: pip install pyarrow")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to records
    records = []
    for pair in pairs:
        record = {
            "pair_id": pair.pair_id,
            "en": pair.source_text,
            "ga": pair.target_text,
            "alignment_score": pair.alignment_score,
            "source_id": pair.source_id or "",
            "target_id": pair.target_id or "",
            "en_word_count": len(pair.source_text.split()),
            "ga_word_count": len(pair.target_text.split()),
        }
        # Flatten metadata
        for k, v in pair.metadata.items():
            record[f"meta_{k}"] = str(v) if v is not None else ""
        records.append(record)

    if not records:
        return 0

    # Create table
    table = pa.Table.from_pylist(records)

    if partition_by and partition_by in table.column_names:
        pq.write_to_dataset(
            table,
            root_path=str(output_path),
            partition_cols=[partition_by],
        )
    else:
        pq.write_table(table, output_path)

    return len(records)


def export_to_huggingface(
    pairs: Sequence[ParallelPair],
    dataset_name: str,
    push_to_hub: bool = False,
    hub_token: str | None = None,
) -> Dataset:
    """
    Export aligned pairs to HuggingFace Dataset format.

    Args:
        pairs: List of ParallelPair objects
        dataset_name: Name for the dataset
        push_to_hub: Whether to push to HuggingFace Hub
        hub_token: HuggingFace API token

    Returns:
        HuggingFace Dataset object
    """
    try:
        from datasets import Dataset, DatasetDict
    except ImportError:
        raise ImportError("datasets required: pip install datasets")

    # Convert to records
    records = []
    for pair in pairs:
        records.append({
            "id": pair.pair_id,
            "en": pair.source_text,
            "ga": pair.target_text,
            "score": pair.alignment_score,
            "source_doc": pair.source_id or "",
            "target_doc": pair.target_id or "",
        })

    dataset = Dataset.from_list(records)

    # Split into train/val/test (80/10/10)
    if len(records) >= 100:
        dataset = dataset.train_test_split(test_size=0.2, seed=42)
        test_valid = dataset["test"].train_test_split(test_size=0.5, seed=42)
        dataset_dict = DatasetDict({
            "train": dataset["train"],
            "validation": test_valid["train"],
            "test": test_valid["test"],
        })
    else:
        dataset_dict = DatasetDict({"train": dataset})

    if push_to_hub and hub_token:
        dataset_dict.push_to_hub(dataset_name, token=hub_token)

    return dataset_dict


def export_to_tmx(
    pairs: Sequence[ParallelPair],
    output_path: Path | str,
    source_lang: str = "en",
    target_lang: str = "ga-IE",
) -> int:
    """
    Export aligned pairs to TMX (Translation Memory eXchange) format.

    Args:
        pairs: List of ParallelPair objects
        output_path: Output file path
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Number of pairs exported
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # TMX header
    tmx_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header
    creationtool="cianfhoghlaim-alignment"
    creationtoolversion="1.0"
    datatype="plaintext"
    segtype="sentence"
    adminlang="en"
    srclang="{source_lang}"
    o-tmf="plaintext">
  </header>
  <body>
'''

    tmx_footer = '''  </body>
</tmx>
'''

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tmx_header)

        for pair in pairs:
            tu = _to_tmx_unit(pair, source_lang, target_lang)
            f.write(tu)
            count += 1

        f.write(tmx_footer)

    return count


def export_for_training(
    results: Sequence[AlignmentResult],
    output_dir: Path | str,
    min_score: float = 0.7,
    formats: list[str] | None = None,
) -> dict[str, int]:
    """
    Export alignment results in multiple formats for training.

    Args:
        results: List of AlignmentResult objects
        output_dir: Output directory
        min_score: Minimum alignment score to include
        formats: List of formats to export ("jsonl", "parquet", "tmx")

    Returns:
        Dictionary of format -> count exported
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if formats is None:
        formats = ["jsonl", "parquet", "tmx"]

    # Collect all pairs above threshold
    all_pairs = []
    for result in results:
        for pair in result.pairs:
            if pair.alignment_score >= min_score:
                all_pairs.append(pair)

    counts = {}

    if "jsonl" in formats:
        # Export both directions
        counts["jsonl_en2ga"] = export_to_jsonl(
            all_pairs,
            output_dir / "irish_english_en2ga.jsonl",
            direction="en2ga",
        )
        counts["jsonl_ga2en"] = export_to_jsonl(
            all_pairs,
            output_dir / "irish_english_ga2en.jsonl",
            direction="ga2en",
        )

    if "parquet" in formats:
        counts["parquet"] = export_to_parquet(
            all_pairs,
            output_dir / "irish_english_parallel.parquet",
        )

    if "tmx" in formats:
        counts["tmx"] = export_to_tmx(
            all_pairs,
            output_dir / "irish_english_parallel.tmx",
        )

    return counts


def stream_to_jsonl(
    pairs: Iterator[ParallelPair],
    output_path: Path | str,
    direction: str = "en2ga",
    batch_size: int = 1000,
) -> int:
    """
    Stream aligned pairs to JSONL file in batches.

    Useful for large datasets that don't fit in memory.

    Args:
        pairs: Iterator of ParallelPair objects
        output_path: Output file path
        direction: Translation direction
        batch_size: Flush to disk every N records

    Returns:
        Total number of pairs exported
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    buffer = []

    with open(output_path, "w", encoding="utf-8") as f:
        for pair in pairs:
            record = _to_chat_format(pair, direction, include_system_prompt=True)
            buffer.append(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

            if len(buffer) >= batch_size:
                f.writelines(buffer)
                buffer.clear()

        # Write remaining
        if buffer:
            f.writelines(buffer)

    return count


# Helper functions

def _to_chat_format(
    pair: ParallelPair,
    direction: str,
    include_system_prompt: bool,
) -> dict:
    """Convert pair to chat format for LLM training."""
    messages = []

    if include_system_prompt:
        if direction == "en2ga":
            messages.append({"role": "system", "content": TRANSLATION_SYSTEM_PROMPT})
        else:
            messages.append({"role": "system", "content": IRISH_SYSTEM_PROMPT})

    if direction == "en2ga":
        messages.append({"role": "user", "content": pair.source_text})
        messages.append({"role": "assistant", "content": pair.target_text})
    else:
        messages.append({"role": "user", "content": pair.target_text})
        messages.append({"role": "assistant", "content": pair.source_text})

    return {
        "messages": messages,
        "metadata": {
            "pair_id": pair.pair_id,
            "alignment_score": pair.alignment_score,
            "direction": direction,
        },
    }


def _to_simple_format(pair: ParallelPair, direction: str) -> dict:
    """Convert pair to simple input/output format."""
    if direction == "en2ga":
        return {
            "input": pair.source_text,
            "output": pair.target_text,
            "source_lang": "en",
            "target_lang": "ga",
        }
    else:
        return {
            "input": pair.target_text,
            "output": pair.source_text,
            "source_lang": "ga",
            "target_lang": "en",
        }


def _escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _to_tmx_unit(
    pair: ParallelPair,
    source_lang: str,
    target_lang: str,
) -> str:
    """Convert pair to TMX translation unit."""
    source_text = _escape_xml(pair.source_text)
    target_text = _escape_xml(pair.target_text)

    return f'''    <tu tuid="{pair.pair_id}">
      <prop type="score">{pair.alignment_score:.3f}</prop>
      <tuv xml:lang="{source_lang}">
        <seg>{source_text}</seg>
      </tuv>
      <tuv xml:lang="{target_lang}">
        <seg>{target_text}</seg>
      </tuv>
    </tu>
'''
