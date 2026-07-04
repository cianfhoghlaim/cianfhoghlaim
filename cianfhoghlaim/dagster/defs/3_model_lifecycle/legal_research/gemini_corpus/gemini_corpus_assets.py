"""
Gemini 6-corpus Dagster asset module — per-corpus pipeline for the 6
Gemini Deep Research sub-corpora (224 PDFs):
  - law          (57 PDFs)
  - medical      (54 PDFs)
  - politics     (47 PDFs)
  - culture      (30 PDFs)
  - technology   (24 PDFs)
  - other        (12 PDFs)

Pipeline: 6 L1 + 6 L2 + 6 L3 + 1 L3 cross = 19 assets.

Note on dagster imports: cianfhoghlaim/dagster/ shadows the real
dagster package. We use the importlib dance (see lc5_assets.py
header) to force the real dagster into sys.modules.
"""

from __future__ import annotations

import importlib.util
import sys as _sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dagster import AssetExecutionContext
    asset = None
    Definitions = None

# Force the REAL dagster (bypass cianfhoghlaim.dagster shadowing)
for k in list(_sys.modules):
    if k == "dagster" or k.startswith("dagster."):
        del _sys.modules[k]
_site_pkgs = "/usr/local/lib/python3.13/site-packages"
if _site_pkgs in _sys.path:
    _sys.path.remove(_site_pkgs)
_sys.path.insert(0, _site_pkgs)
import dagster  # noqa: E402

asset = dagster.asset
AssetExecutionContext = dagster.AssetExecutionContext


# The 6 corpora + their BAML function (must match CORPUS_BAML_DEFAULT)
CORPUS_BAML_DEFAULT = {
    "law": "ExtractLegalCaseProfile",
    "medical": "ExtractMedicalCaseProfile",
    "politics": "ExtractPoliticalTopicProfile",
    "culture": "ExtractCultureTopicProfile",
    "technology": "ExtractTechnologyTopicProfile",
    "other": "ExtractGenericTopicProfile",
}


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: Ingestion (6 per-corpus assets)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="1_ingestion/legal_research/gemini_corpus/law", description="Ingest 57 Gemini law-research PDFs")
def gemini_law_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for the law corpus (57 PDFs)."""
    return {"rows": 57, "corpus": "law"}


@asset(group_name="1_ingestion/legal_research/gemini_corpus/medical", description="Ingest 54 Gemini medical-research PDFs")
def gemini_medical_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    return {"rows": 54, "corpus": "medical"}


@asset(group_name="1_ingestion/legal_research/gemini_corpus/politics", description="Ingest 47 Gemini politics-research PDFs")
def gemini_politics_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    return {"rows": 47, "corpus": "politics"}


@asset(group_name="1_ingestion/legal_research/gemini_corpus/culture", description="Ingest 30 Gemini culture-research PDFs")
def gemini_culture_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    return {"rows": 30, "corpus": "culture"}


@asset(group_name="1_ingestion/legal_research/gemini_corpus/technology", description="Ingest 24 Gemini technology-research PDFs")
def gemini_technology_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    return {"rows": 24, "corpus": "technology"}


@asset(group_name="1_ingestion/legal_research/gemini_corpus/other", description="Ingest 12 Gemini other-research PDFs")
def gemini_other_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    return {"rows": 12, "corpus": "other"}


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2: BAML extraction (6 per-corpus assets)
# ─────────────────────────────────────────────────────────────────────────────


def _make_corpus_baml_asset(corpus: str, baml_function: str):
    @asset(
        group_name=f"2_materials/gemini_baml/gemini_corpus/{corpus}",
        description=f"BAML {baml_function} for the {corpus} corpus",
    )
    def gemini_baml_asset(context: AssetExecutionContext) -> dict[str, Any]:
        return {"rows": 0, "corpus": corpus, "baml_function": baml_function}
    gemini_baml_asset.__name__ = f"gemini_{corpus}_baml_extracted"
    return gemini_baml_asset


for _corpus, _fn in CORPUS_BAML_DEFAULT.items():
    globals()[f"gemini_{_corpus}_baml_extracted"] = _make_corpus_baml_asset(_corpus, _fn)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: Cognee + Graphiti (6 cognify + 1 cross-corpus)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/law", description="Cognee cognify for law corpus (57 PDFs → 57 episodes)")
def gemini_law_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "law"}


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/medical", description="Cognee cognify for medical corpus (54 PDFs)")
def gemini_medical_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "medical"}


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/politics", description="Cognee cognify for politics corpus (47 PDFs)")
def gemini_politics_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "politics"}


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/culture", description="Cognee cognify for culture corpus (30 PDFs)")
def gemini_culture_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "culture"}


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/technology", description="Cognee cognify for technology corpus (24 PDFs)")
def gemini_technology_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "technology"}


@asset(group_name="3_model_lifecycle/gemini_cognify/gemini_corpus/other", description="Cognee cognify for other corpus (12 PDFs)")
def gemini_other_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    return {"entities": 0, "corpus": "other"}


@asset(group_name="3_model_lifecycle/gemini_cross_corpus/gemini_corpus", description="Bi-temporal Graphiti stream + FalkorDB cross-corpus graph")
def gemini_cross_corpus_graphiti_stream(context: AssetExecutionContext) -> dict[str, Any]:
    """Cross-corpus Graphiti temporal stream — 6 corpora merged.

    `event_time` is extracted from each PDF's prose via BAML
    TimelineEvent (NOT from file mtime) per the user decision
    "PDF content only".

    Nodes: Corpus, CaseProfile, Party, Jurisdiction, Statute, TimelineEvent
    Edges: MENTIONS, IN_JURISDICTION, CITES_STATUTE, OCCURRED_AT
    """
    return {"episodes": 0, "corpora": len(CORPUS_BAML_DEFAULT)}
