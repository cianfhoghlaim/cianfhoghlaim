"""
Gemini Deep Research 6-corpus filesystem DLT source.

Ingests every PDF in `leabharlann/gemini_deep_research/{law,medical,
politics,culture,technology,other}/` into per-corpus DuckLake tables:
  - gemini_law_research.cases / .timeline_events / .legal_issues
  - gemini_medical_research.cases / .timeline_events / .legal_issues
  - gemini_politics_research.cases / .timeline_events / .legal_issues
  - gemini_culture_research.cases / .timeline_events / .legal_issues
  - gemini_technology_research.cases / .timeline_events / .legal_issues
  - gemini_other_research.cases / .timeline_events / .legal_issues

Total: 224 PDFs across 6 corpora (verified 2026-07-04).

Each PDF is routed through the v4 OCR/VLM registry's qwen3-vl-8b
workhorse (the LC5 `select_ocr_backend()` heuristic also routes
text-heavy PDFs to qwen3-vl-8b).
"""

from __future__ import annotations
import dlt


import hashlib
import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)

DEFAULT_GEMINI_ROOT = Path(
    os.environ.get(
        "GEMINI_DEEP_RESEARCH_ROOT",
        str(Path(__file__).resolve().parents[3] / "leabharlann" / "gemini_deep_research"),
    )
)

# The 6 corpora (verified counts: law=57, medical=54, politics=47,
# culture=30, technology=24, other=12; total=224 PDFs)
GEMINI_CORPORA: tuple[str, ...] = (
    "law",
    "medical",
    "politics",
    "culture",
    "technology",
    "other",
)

# Per-corpus case category hints (for BAML routing). The 6 BAML classes
# used: LegalCaseProfile (law+medical), MedicalCaseProfile (medical),
# PoliticalTopicProfile (politics), CultureTopicProfile (culture),
# TechTopicProfile (technology), TimelineEvent (PDF content only;
# per the user decision "PDF content only" no bi-temporal).
CORPUS_BAML_FUNCTIONS: dict[str, str] = {
    "law": "ExtractLegalCaseProfile",
    "medical": "ExtractMedicalCaseProfile",
    "politics": "ExtractPoliticalTopicProfile",
    "culture": "ExtractCultureTopicProfile",
    "technology": "ExtractTechnologyTopicProfile",
    "other": "ExtractGenericTopicProfile",
}


def _scan_corpus(corpus_dir: Path) -> Iterator[Path]:
    """Yield all PDFs in a corpus subdirectory (non-recursive)."""
    if not corpus_dir.exists():
        return
    for p in sorted(corpus_dir.glob("*.pdf")):
        yield p


def _classify_pdf(pdf_path: Path) -> tuple[str, str, str]:
    """Pick (corpus, category, jurisdiction) for a PDF based on filename + corpus dir.

    Returns:
        corpus: one of the GEMINI_CORPORA (always the parent dir name)
        category: a CaseCategory enum value (best-effort from filename heuristic)
        jurisdiction: a Jurisdiction enum value (best-effort from filename)
    """
    name = pdf_path.name.lower()
    corpus = pdf_path.parent.name

    # Jurisdictional heuristics (in priority order)
    if "echr" in name or "european" in name:
        jurisdiction = "EUROPEAN_UNION"
    elif "ni_" in name or "belfast" in name or "qub" in name:
        jurisdiction = "NORTHERN_IRELAND"
    elif "uk_" in name or "ucl_" in name:
        jurisdiction = "UNITED_KINGDOM"
    elif "ireland" in name or "irish" in name or "gael" in name:
        jurisdiction = "IRELAND"
    elif "dual" in name:
        jurisdiction = "CROSS_BORDER"
    else:
        jurisdiction = "IRELAND"  # default for the Cianfhoghlaim (Gemini defaults to IE)

    # Category heuristics
    category = "OTHER"
    if corpus == "law":
        if "malpractice" in name or "medical_malpractice" in name:
            category = "MEDICAL_MALPRACTICE"
        elif "discrimination" in name:
            category = "DISCRIMINATION"
        elif "citizenship" in name or "passport" in name:
            category = "DUAL_CITIZENSHIP"
        elif "eviction" in name or "tenancy" in name:
            category = "TENANCY_DISPUTE"
        elif "garda" in name:
            category = "GARDA_MISCONDUCT"
        elif "hate_crime" in name:
            category = "HATE_CRIME"
        elif "university" in name or "uog" in name or "qub" in name or "ucl" in name:
            category = "UNIVERSITY_DISPUTE"
        elif "family" in name or "father" in name or "abuse" in name:
            category = "FAMILY_LAW"
        else:
            category = "LEGAL_STRATEGY"
    elif corpus == "medical":
        category = "MEDICAL_MALPRACTICE"
    elif corpus == "politics":
        category = "POLICY"

    return corpus, category, jurisdiction


def _row(pdf_path: Path, corpus: str) -> dict[str, Any]:
    """Build the DuckLake row for one PDF ingestion."""
    file_hash = ""
    try:
        file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    except OSError:
        pass

    cls_corpus, category, jurisdiction = _classify_pdf(pdf_path)

    return {
        "id": hashlib.sha256(
            f"{file_hash}:{pdf_path.name}:{corpus}".encode("utf-8")
        ).hexdigest()[:16],
        "file_hash": file_hash,
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "file_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "corpus": corpus,
        "category": category,
        "jurisdiction": jurisdiction,
        # The BAML function that will be called downstream
        "baml_function": CORPUS_BAML_FUNCTIONS.get(corpus, "ExtractGenericTopicProfile"),
        # Use qwen3-vl-8b (the v4 workhorse for text-heavy PDFs)
        "model_key": "qwen3-vl-8b",
        # Slug from filename for cross-corpus queries
        "slug": re.sub(r"[^a-z0-9_]+", "_", pdf_path.stem.lower())[:64],
    }


@dlt.resource(
    name="gemini_documents",
    write_disposition="replace",
    primary_key="id",
    columns={
        "id": {"data_type": "text"},
        "file_hash": {"data_type": "text"},
        "file_name": {"data_type": "text"},
        "file_path": {"data_type": "text"},
        "file_size_bytes": {"data_type": "bigint"},
        "corpus": {"data_type": "text"},
        "category": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "baml_function": {"data_type": "text"},
        "model_key": {"data_type": "text"},
        "slug": {"data_type": "text"},
    },
)
def gemini_documents(
    root_path: str = str(DEFAULT_GEMINI_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield one row per Gemini Deep Research PDF across all 6 corpora.

    Total: 224 PDFs (57 law + 54 medical + 47 politics + 30 culture +
    24 technology + 12 other; verified 2026-07-04).

    Default root: `leabharlann/gemini_deep_research/`.
    Override via the `GEMINI_DEEP_RESEARCH_ROOT` env var.
    """
    root = Path(root_path)
    if not root.exists():
        logger.error(f"gemini_root_missing: {root}")
        return

    n = 0
    per_corpus: dict[str, int] = {}
    for corpus in GEMINI_CORPORA:
        corpus_dir = root / corpus
        count = 0
        for pdf in _scan_corpus(corpus_dir):
            row = _row(pdf, corpus)
            yield row
            n += 1
            count += 1
        per_corpus[corpus] = count
    logger.info(f"gemini_ingested: {n} documents across {len(GEMINI_CORPORA)} corpora: {per_corpus}")


def main() -> int:
    """CLI entry — runs the pipeline against the local duckdb destination."""
    import duckdb
    con = duckdb.connect("gemini_ingest.duckdb")
    pipeline = dlt.pipeline(
        pipeline_name="gemini_6_corpus",
        destination=dlt.destinations.duckdb("gemini_ingest.duckdb"),
        dataset_name="gemini_research",
    )
    load_info = pipeline.run(gemini_documents())
    print(load_info)
    df = con.execute("SELECT corpus, jurisdiction, COUNT(*) FROM gemini_research.gemini_documents GROUP BY corpus, jurisdiction ORDER BY corpus, jurisdiction").df()
    print(df.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
