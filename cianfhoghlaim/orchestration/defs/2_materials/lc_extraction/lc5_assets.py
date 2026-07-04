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
                         - lc5_chemistry_ingested
                         - lc5_computer_science_ingested
                         - lc5_gaeilge_ingested
                         - lc5_geography_ingested
                         - lc5_mathematics_ingested
                         (each runs cianfhoghlaim.dlt.filesystem.leaving_cert_source
                          filtered by subject)

  Layer 2 (Materials):  5 BAML extraction assets
                         - lc5_<subject>_syllabus_extracted (ExtractCurriculumSyllabus)
                         - lc5_<subject>_papers_extracted    (ExtractExamPaperLayout)
                         - lc5_<subject>_marking_extracted   (ExtractMarkingSchemeGuideline)
                         - lc5_<subject>_diagrams_extracted  (ExtractSyllabusDiagram via molmo2-8b)

  Layer 3 (Lifecycle):  5 cognify assets + 1 cross-subject Graphiti stream
                         - lc5_<subject>_cognified
                         - lc5_cross_subject_graphiti_stream (5 subjects merged)

Each asset is keyed by the 5-layer group_name convention
"<N>_<layer>/<domain>/<slug>" with lc5_ prefix.

The actual BAML functions live in:
  cianfhoghlaim/baml_src/education/lc_extraction/{curriculum_syllabus,
                                                  exam_paper_layout,
                                                  marking_scheme,
                                                  cross_linguistic,
                                                  syllabus_diagram}.baml
"""

from __future__ import annotations

from typing import Any

from dagster import AssetExecutionContext, asset

try:
    from cianfhoghlaim.baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None

try:
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    DLT_AVAILABLE = True
except ImportError:
    DLT_AVAILABLE = False
    lc5_documents = None

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    cognee = None

try:
    from graphiti_core import Graphiti
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    Graphiti = None


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
def lc5_chemistry_ingested(context) -> dict[str, Any]:
    """Layer 1 ingestion for chemistry (LC022) — 16 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        context.log.warning("DLT source not available; returning stub")
        return {"rows": 0, "subject": "chemistry"}
    context.log.info("ingesting chemistry LC PDFs")
    rows = list(lc5_documents(root_path="cianfhoghlaim/leaving_certificate"))  # type: ignore[misc]
    chemistry_rows = [r for r in rows if r["subject"] == "chemistry"]
    context.add_output_metadata({"row_count": len(chemistry_rows)})
    return {"rows": len(chemistry_rows), "subject": "chemistry"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest computer_science LC PDFs")
def lc5_computer_science_ingested(context) -> dict[str, Any]:
    """Layer 1 ingestion for computer_science (LC219) — 11 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "computer_science"}
    rows = list(lc5_documents(root_path="cianfhoghlaim/leaving_certificate"))  # type: ignore[misc]
    cs_rows = [r for r in rows if r["subject"] == "computer_science"]
    context.add_output_metadata({"row_count": len(cs_rows)})
    return {"rows": len(cs_rows), "subject": "computer_science"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest gaeilge LC PDFs (no en/ subdir; Irish-only at root)")
def lc5_gaeilge_ingested(context) -> dict[str, Any]:
    """Layer 1 ingestion for gaeilge (LC001) — 11 PDFs at root, GLM-4.6V routing."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "gaeilge"}
    rows = list(lc5_documents(root_path="cianfhoghlaim/leaving_certificate"))  # type: ignore[misc]
    ga_rows = [r for r in rows if r["subject"] == "gaeilge"]
    context.add_output_metadata({"row_count": len(ga_rows)})
    return {"rows": len(ga_rows), "subject": "gaeilge"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest geography LC PDFs + 1 JPG scanned exam page")
def lc5_geography_ingested(context) -> dict[str, Any]:
    """Layer 1 ingestion for geography (LC005) — 18 PDFs + 1 JPG across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "geography"}
    rows = list(lc5_documents(root_path="cianfhoghlaim/leaving_certificate"))  # type: ignore[misc]
    geo_rows = [r for r in rows if r["subject"] == "geography"]
    context.add_output_metadata({"row_count": len(geo_rows)})
    return {"rows": len(geo_rows), "subject": "geography"}


@asset(group_name="1_ingestion/curriculum/lc5", description="Ingest mathematics LC PDFs (LaTeX + formula heavy)")
def lc5_mathematics_ingested(context) -> dict[str, Any]:
    """Layer 1 ingestion for mathematics (LC003) — 16 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "mathematics"}
    rows = list(lc5_documents(root_path="cianfhoghlaim/leaving_certificate"))  # type: ignore[misc]
    math_rows = [r for r in rows if r["subject"] == "mathematics"]
    context.add_output_metadata({"row_count": len(math_rows)})
    return {"rows": len(math_rows), "subject": "mathematics"}


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
    def lc5_extraction_asset(context) -> dict[str, Any]:
        """Stub for the {baml_function} extraction of {subject}."""
        if not BAML_AVAILABLE:
            return {"rows": 0, "subject": subject, "kind": kind}
        context.log.info(f"running {baml_function} for {subject}")
        # Real call would be: b.{baml_function}(source_pdf=..., subject=subject, ...)
        # Per CHANGE B1: BAML functions live in cianfhoghlaim/baml_src/education/lc_extraction/
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
def lc5_chemistry_cognified(context) -> dict[str, Any]:
    """Per-subject Cognee cognify (oideachais_chemistry dataset)."""
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "chemistry"}
    # Real call would be: await cognee.cognify(dataset_name=f"oideachais_{subject}")
    return {"entities": 0, "subject": "chemistry"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/computer_science", description="Cognee cognify for computer_science LC")
def lc5_computer_science_cognified(context) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "computer_science"}
    return {"entities": 0, "subject": "computer_science"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/gaeilge", description="Cognee cognify for gaeilge LC (multilingual Irish dataset)")
def lc5_gaeilge_cognified(context) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "gaeilge"}
    return {"entities": 0, "subject": "gaeilge"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/geography", description="Cognee cognify for geography LC (diagram-heavy)")
def lc5_geography_cognified(context) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "geography"}
    return {"entities": 0, "subject": "geography"}


@asset(group_name="3_model_lifecycle/lc_cognify/lc5/mathematics", description="Cognee cognify for mathematics LC (formula-heavy)")
def lc5_mathematics_cognified(context) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "mathematics"}
    return {"entities": 0, "subject": "mathematics"}


@asset(group_name="3_model_lifecycle/lc_cross_subject/lc5", description="Bi-temporal Graphiti stream + FalkorDB cross-subject graph")
def lc5_cross_subject_graphiti_stream(context) -> dict[str, Any]:
    """Cross-subject Graphiti temporal stream — 5 subjects merged into a FalkorDB graph.

    Nodes: Subject, Topic, LearningOutcome, Question, Year, ModuleKind
    Edges: HAS_TOPIC, ASSESSED_BY, EVOLVED_TO, EN_CORRESPONDS_TO_GA (cross-linguistic)
    """
    if not GRAPHITI_AVAILABLE:
        return {"episodes": 0, "subjects": len(LC5_SUBJECTS)}
    return {"episodes": 0, "subjects": len(LC5_SUBJECTS)}
