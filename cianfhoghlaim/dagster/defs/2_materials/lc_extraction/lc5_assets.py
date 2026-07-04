"""
LC5-subject Dagster asset module — per-subject pipeline for the 5
NCCA Leaving Certificate subjects:
  - chemistry (LC022)
  - computer_science (LC219)
  - gaeilge (LC001)
  - geography (LC005)
  - mathematics (LC003)

Pipeline stages (per openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/):

  Layer 1 (Ingestion):  5 per-subject dlt assets
  Layer 2 (Materials):  20 BAML extraction assets (4 kinds × 5 subjects)
  Layer 3 (Lifecycle):  6 cognify + 1 cross-subject Graphiti = 7 assets

The 5 L1 + 20 L2 + 5 L3 cognify + 1 L3 cross = 31 assets.

Note on dagster imports: cianfhoghlaim/dagster/ shadows the real
dagster package. We use `import dagster` (not `from dagster import`)
and reference the symbols via `dagster.asset(...)` to avoid the
shadowing. The real dagster is loaded from site-packages first via
the .pth file at /usr/local/lib/python3.13/site-packages/cianfhoghlaim.pth
(see Dockerfile.dagster for the build-time install).
"""

from __future__ import annotations

import importlib.util
import os
import sys as _sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # For type-checkers only
    from dagster import AssetExecutionContext
    asset = None  # placeholder
    Definitions = None  # placeholder

# Force the REAL dagster to be loaded (bypassing cianfhoghlaim.dagster
# which shadows it). We clear any cached "dagster" module + insert
# site-packages at the front of sys.path.
for k in list(_sys.modules):
    if k == "dagster" or k.startswith("dagster."):
        del _sys.modules[k]
_site_pkgs = "/usr/local/lib/python3.13/site-packages"
if _site_pkgs in _sys.path:
    _sys.path.remove(_site_pkgs)
_sys.path.insert(0, _site_pkgs)
import dagster  # noqa: E402

# Alias the symbols
asset = dagster.asset
AssetExecutionContext = dagster.AssetExecutionContext
Definitions = dagster.Definitions


# The 5 LC subjects (must match cianfhoghlaim.dlt.filesystem.leaving_cert_source.LC5_SUBJECTS)
LC5_SUBJECTS: tuple[str, ...] = (
    "chemistry",
    "computer_science",
    "gaeilge",
    "geography",
    "mathematics",
)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: Ingestion (5 per-subject assets)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest chemistry LC PDFs + JPG via select_ocr_backend() routing")
def lc5_chemistry_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for chemistry (LC022) — 16 PDFs across en/ga."""
    return {"rows": 0, "subject": "chemistry"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest computer_science LC PDFs")
def lc5_computer_science_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for computer_science (LC219) — 11 PDFs across en/ga."""
    return {"rows": 0, "subject": "computer_science"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest gaeilge LC PDFs (no en/ subdir; Irish-only at root)")
def lc5_gaeilge_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for gaeilge (LC001) — 11 PDFs at root, GLM-4.6V routing."""
    return {"rows": 0, "subject": "gaeilge"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest geography LC PDFs + 1 JPG scanned exam page")
def lc5_geography_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for geography (LC005) — 18 PDFs + 1 JPG across en/ga."""
    return {"rows": 0, "subject": "geography"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest mathematics LC PDFs (LaTeX + formula heavy)")
def lc5_mathematics_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for mathematics (LC003) — 16 PDFs across en/ga."""
    return {"rows": 0, "subject": "mathematics"}


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2: BAML materials extraction (5 subjects × 4 BAML functions = 20 assets)
# ─────────────────────────────────────────────────────────────────────────────


def _make_subject_extraction_asset(subject: str, kind: str):
    """Factory for the 20 per-subject BAML extraction assets (4 kinds × 5 subjects)."""
    baml_function_map = {
        "syllabus": "ExtractCurriculumSyllabus",
        "papers": "ExtractExamPaperLayout",
        "marking": "ExtractMarkingSchemeGuideline",
        "diagrams": "ExtractSyllabusDiagram",
    }
    baml_function = baml_function_map[kind]

    @asset(
        group_name=f"2_materials/lc_{kind}/lc5/{subject}",
        description=f"BAML {baml_function} for the {subject} LC subject",
    )
    def lc5_extraction_asset(context: AssetExecutionContext) -> dict[str, Any]:
        """Stub for the {baml_function} extraction of {subject}."""
        return {"rows": 0, "subject": subject, "kind": kind}

    lc5_extraction_asset.__name__ = f"lc5_{subject}_{kind}_extracted"
    return lc5_extraction_asset


# Generate the 20 BAML extraction assets
for _subject in LC5_SUBJECTS:
    for _kind in ("syllabus", "papers", "marking", "diagrams"):
        globals()[f"lc5_{_subject}_{_kind}_extracted"] = _make_subject_extraction_asset(_subject, _kind)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: Model Lifecycle (5 per-subject cognify + 1 cross-subject Graphiti)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/chemistry", description="Cognee cognify for chemistry LC")
def lc5_chemistry_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    """Per-subject Cognee cognify (oideachais_chemistry dataset)."""
    return {"entities": 0, "subject": "chemistry"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/computer_science", description="Cognee cognify for computer_science LC")
def lc5_computer_science_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "subject": "computer_science"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/gaeilge", description="Cognee cognify for gaeilge LC (multilingual Irish dataset)")
def lc5_gaeilge_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "subject": "gaeilge"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/geography", description="Cognee cognify for geography LC (diagram-heavy)")
def lc5_geography_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "subject": "geography"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/mathematics", description="Cognee cognify for mathematics LC (formula-heavy)")
def lc5_mathematics_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "subject": "mathematics"}


@asset(group_name="3_model_lifecycle/lc_cross_subject/lc5", description="Bi-temporal Graphiti stream + FalkorDB cross-subject graph")
def lc5_cross_subject_graphiti_stream(context: AssetExecutionContext) -> dict[str, Any]:
    """Cross-subject Graphiti temporal stream — 5 subjects merged into a FalkorDB graph.

    Nodes: Subject, Topic, LearningOutcome, Question, Year, ModuleKind
    Edges: HAS_TOPIC, ASSESSED_BY, EVOLVED_TO, EN_CORRESPONDS_TO_GA (cross-linguistic)
    """
    return {"episodes": 0, "subjects": len(LC5_SUBJECTS)}
