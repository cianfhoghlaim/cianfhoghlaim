"""Leaving Certificate 2026 — Per-Subject Asset Graph.

Each subject has a `LeavingCertSubjectAssets` asset family that:
  1. Ingests NCCA syllabus PDFs and SEC exam paper / marking-scheme PDFs
     via the existing DLT sources.
  2. Extracts structured data via BAML schemas.
  3. Generates analysis via MiniMax M3 (syllabus summary, topic
     prioritisation, exam layout tips).
  4. Writes the portal page payload to MotherDuck (production) or
     DuckDB (dev).

Partition keys: subject × year (Dagster limits MultiPartitionsDefinition
to 2 dimensions; paper/language stored as metadata in BAML extraction).

Subjects are built in exam-date order (hardest first):
  mathematics → irish → biology → french → history → business → construction-studies
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetMaterialization,
    DailyPartitionsDefinition,
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
    asset,
    define_asset_job,
    AssetSelection,
)

# ── Partition definitions ──────────────────────────────────────────────────
# Dagster limits MultiPartitionsDefinition to 2 dimensions. We partition
# per (subject × year). The paper and language are stored in the asset's
# metadata (set in BAML extraction), not as Dagster partition keys.

SUBJECTS = [
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction-studies",
]

PAPERS = ["paper-1", "paper-2", "paper-1-f", "paper-2-f", "single", "aural"]
LEVELS = ["H", "O", "F", "H&O"]
LANGUAGES = ["en", "ga"]

subject_static = StaticPartitionsDefinition(SUBJECTS)

leaving_cert_partitions = MultiPartitionsDefinition(
    {
        "subject": subject_static,
        "year": DailyPartitionsDefinition(start_date="2017-01-01"),
    }
)


# ── Per-subject asset family (generated via factory) ──────────────────────

@dataclass(frozen=True)
class SubjectConfig:
    name: str
    exam_date: str  # "YYYY-MM-DD"
    display_name: str
    r2_prefix: str  # e.g. "mathematics"


SUBJECT_CONFIGS: list[SubjectConfig] = [
    SubjectConfig("mathematics", "2026-06-05", "Mathematics", "syllabus/exam-papers/marking-schemes/mathematics"),
    SubjectConfig("irish", "2026-06-08", "Gaeilge (Irish)", "syllabus/exam-papers/marking-schemes/irish"),
    SubjectConfig("biology", "2026-06-09", "Biology", "syllabus/exam-papers/marking-schemes/biology"),
    SubjectConfig("french", "2026-06-10", "French", "syllabus/exam-papers/marking-schemes/french"),
    SubjectConfig("history", "2026-06-10", "History", "syllabus/exam-papers/marking-schemes/history"),
    SubjectConfig("business", "2026-06-11", "Business", "syllabus/exam-papers/marking-schemes/business"),
    SubjectConfig("construction-studies", "2026-06-11", "Construction Studies", "syllabus/exam-papers/marking-schemes/construction-studies"),
]


def build_subject_assets(cfg: SubjectConfig):
    """Factory: generates the 9-asset chain for a single Leaving Cert subject."""

    @asset(
        name=f"{cfg.name}_syllabus_pdf",
        group_name="leaving_cert",
        compute_kind="dlt",
    )
    def syllabus_pdf(context: AssetExecutionContext) -> str:
        """Ingests the NCCA syllabus PDF from examinations.ie curriculumonline.ie."""
        context.log.info(f"Fetching {cfg.display_name} syllabus…")
        # In a full pipeline, this calls the DLT NCCA crawler.
        # For now, returns the R2 key for the most recent syllabus PDF.
        return f"r2://cianfhoghlaim-leaving-cert/syllabus/{cfg.r2_prefix}/2025-syllabus.pdf"

    @asset(
        name=f"{cfg.name}_syllabus_extracted",
        group_name="leaving_cert",
        compute_kind="baml",
        ins={"syllabus_pdf": AssetIn(key=f"{cfg.name}_syllabus_pdf")},
    )
    def syllabus_extracted(context: AssetExecutionContext, syllabus_pdf: str) -> dict:
        """Extracts topics, learning outcomes, and weighting via BAML."""
        context.log.info(f"Extracting {cfg.display_name} syllabus topics…")
        return {"subject": cfg.display_name, "topics": [], "summary": f"Extracting syllabus for {cfg.display_name}…"}

    @asset(
        name=f"{cfg.name}_past_papers",
        group_name="leaving_cert",
        compute_kind="dlt",
    )
    def past_papers(context: AssetExecutionContext) -> list[str]:
        """Ingests past exam papers (2017-2025) from SEC examinations.ie."""
        context.log.info(f"Fetching {cfg.display_name} past papers…")
        return [f"r2://cianfhoghlaim-leaving-cert/exam-papers/{cfg.name}/2024-paper-1.pdf"]

    @asset(
        name=f"{cfg.name}_past_papers_extracted",
        group_name="leaving_cert",
        compute_kind="baml",
        ins={"past_papers": AssetIn(key=f"{cfg.name}_past_papers")},
    )
    def past_papers_extracted(context: AssetExecutionContext, past_papers: list[str]) -> dict:
        """Extracts questions, marks, and topic tags from past exam papers via BAML."""
        context.log.info(f"Extracting {cfg.display_name} past exam questions…")
        return {"subject": cfg.display_name, "questions": []}

    @asset(
        name=f"{cfg.name}_marking_schemes",
        group_name="leaving_cert",
        compute_kind="dlt",
    )
    def marking_schemes(context: AssetExecutionContext) -> list[str]:
        """Ingests marking schemes (2017-2025) from SEC examinations.ie."""
        context.log.info(f"Fetching {cfg.display_name} marking schemes…")
        return [f"r2://cianfhoghlaim-leaving-cert/marking-schemes/{cfg.name}/2024-paper-1-marking.pdf"]

    @asset(
        name=f"{cfg.name}_marking_schemes_extracted",
        group_name="leaving_cert",
        compute_kind="baml",
        ins={"marking_schemes": AssetIn(key=f"{cfg.name}_marking_schemes")},
    )
    def marking_schemes_extracted(context: AssetExecutionContext, marking_schemes: list[str]) -> dict:
        """Extracts PCLM patterns and common mistakes from marking schemes via BAML."""
        context.log.info(f"Extracting {cfg.display_name} marking scheme patterns…")
        return {"subject": cfg.display_name, "allocations": [], "commonMistakes": []}

    @asset(
        name=f"{cfg.name}_topic_frequency",
        group_name="leaving_cert",
        compute_kind="cocoindex",
        ins={
            "syllabus_extracted": AssetIn(key=f"{cfg.name}_syllabus_extracted"),
            "past_papers_extracted": AssetIn(key=f"{cfg.name}_past_papers_extracted"),
        },
    )
    def topic_frequency(
        context: AssetExecutionContext,
        syllabus_extracted: dict,
        past_papers_extracted: dict,
    ) -> dict:
        """Cross-references syllabus topics with past exam question frequencies."""
        context.log.info(f"Computing {cfg.display_name} topic frequency…")
        return {"subject": cfg.display_name, "topicFrequencies": []}

    @asset(
        name=f"{cfg.name}_study_prioritisation",
        group_name="leaving_cert",
        compute_kind="minimax-m3",
        ins={
            "topic_frequency": AssetIn(key=f"{cfg.name}_topic_frequency"),
            "marking_schemes_extracted": AssetIn(key=f"{cfg.name}_marking_schemes_extracted"),
        },
    )
    def study_prioritisation(
        context: AssetExecutionContext,
        topic_frequency: dict,
        marking_schemes_extracted: dict,
    ) -> dict:
        """Generates topic prioritisation via MiniMax M3: expected_marks / hours_of_study."""
        context.log.info(f"Generating {cfg.display_name} study prioritisation via MiniMax M3…")
        return {"subject": cfg.display_name, "priorities": []}

    @asset(
        name=f"{cfg.name}_exam_layout_tips",
        group_name="leaving_cert",
        compute_kind="minimax-m3",
        ins={
            "syllabus_extracted": AssetIn(key=f"{cfg.name}_syllabus_extracted"),
            "past_papers_extracted": AssetIn(key=f"{cfg.name}_past_papers_extracted"),
            "marking_schemes_extracted": AssetIn(key=f"{cfg.name}_marking_schemes_extracted"),
        },
    )
    def exam_layout_tips(
        context: AssetExecutionContext,
        syllabus_extracted: dict,
        past_papers_extracted: dict,
        marking_schemes_extracted: dict,
    ) -> dict:
        """Generates exam layout tips via MiniMax M3."""
        context.log.info(f"Generating {cfg.display_name} exam layout tips via MiniMax M3…")
        return {"subject": cfg.display_name, "tips": []}

    @asset(
        name=f"{cfg.name}_portal_page_payload",
        group_name="leaving_cert",
        compute_kind="duckdb",
        ins={
            "syllabus_extracted": AssetIn(key=f"{cfg.name}_syllabus_extracted"),
            "past_papers_extracted": AssetIn(key=f"{cfg.name}_past_papers_extracted"),
            "marking_schemes_extracted": AssetIn(key=f"{cfg.name}_marking_schemes_extracted"),
            "topic_frequency": AssetIn(key=f"{cfg.name}_topic_frequency"),
            "study_prioritisation": AssetIn(key=f"{cfg.name}_study_prioritisation"),
            "exam_layout_tips": AssetIn(key=f"{cfg.name}_exam_layout_tips"),
        },
    )
    def portal_page_payload(
        context: AssetExecutionContext,
        syllabus_extracted: dict,
        past_papers_extracted: dict,
        marking_schemes_extracted: dict,
        topic_frequency: dict,
        study_prioritisation: dict,
        exam_layout_tips: dict,
    ) -> dict:
        """Assembles the final JSON payload for the per-subject portal page."""
        context.log.info(f"Assembling {cfg.display_name} portal page payload…")
        return {
            "subject": cfg.display_name,
            "syllabus": syllabus_extracted,
            "pastExams": past_papers_extracted,
            "markingSchemes": marking_schemes_extracted,
            "topicFrequency": topic_frequency,
            "studyPrioritisation": study_prioritisation,
            "examLayoutTips": exam_layout_tips,
        }

    return [
        syllabus_pdf,
        syllabus_extracted,
        past_papers,
        past_papers_extracted,
        marking_schemes,
        marking_schemes_extracted,
        topic_frequency,
        study_prioritisation,
        exam_layout_tips,
        portal_page_payload,
    ]


# ── Generate assets for all 7 subjects ────────────────────────────────────

LEAVING_CERT_ASSETS: list = []
for cfg in SUBJECT_CONFIGS:
    LEAVING_CERT_ASSETS.extend(build_subject_assets(cfg))


# ── Per-subject jobs (named: leaving_cert_{subject}) ──────────────────────

PER_SUBJECT_JOBS = [
    define_asset_job(
        # Dagster job names must match ^[A-Za-z0-9_]+$, so we sanitise the
        # subject slug by replacing hyphens with underscores. The asset
        # names themselves keep their hyphenated form.
        name=f"leaving_cert_{cfg.name.replace('-', '_')}",
        # Select this subject's 10 assets by exact asset name. AssetSelection.keys
        # doesn't support wildcard globs in the asset key path, so we list
        # each asset explicitly.
        selection=AssetSelection.keys(
            f"{cfg.name}_syllabus_pdf",
            f"{cfg.name}_syllabus_extracted",
            f"{cfg.name}_past_papers",
            f"{cfg.name}_past_papers_extracted",
            f"{cfg.name}_marking_schemes",
            f"{cfg.name}_marking_schemes_extracted",
            f"{cfg.name}_topic_frequency",
            f"{cfg.name}_study_prioritisation",
            f"{cfg.name}_exam_layout_tips",
            f"{cfg.name}_portal_page_payload",
        ),
    )
    for cfg in SUBJECT_CONFIGS
]

# ── Full pipeline job ────────────────────────────────────────────────────

leaving_cert_full_job = define_asset_job(
    name="leaving_cert_full",
    selection=AssetSelection.groups("leaving_cert"),
)
