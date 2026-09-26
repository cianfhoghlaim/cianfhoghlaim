"""tuatha/asset_generation/fibo/schemas.py — Database schemas for FIBO educational asset generation.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Defines dataclasses for:
- VisualRequirement: a visual requirement extracted from a curriculum concept
- LearningOutcome: an NCCA learning outcome (with bilingual EN/GA fields)
- SyllabusPage: an indexed curriculum page with ColPali embeddings
- CurriculumConcept: an extracted educational concept
- GeneratedAsset: a FIBO-generated image
- FiboConfig: the canonical FIBO JSON configuration (per the FIBO 2D spec)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any


@dataclass
class VisualRequirement:
    """A visual requirement extracted from a curriculum concept.

    Carries the iconography / diagram hints that the FIBO prompt
    generator uses to compose the asset prompt.
    """
    concept_id: str
    required_elements: list[str]
    iconography_hints: list[str]
    palette_constraints: list[str] = field(default_factory=list)
    motion_requirements: dict[str, Any] | None = None


@dataclass
class LearningOutcome:
    """An NCCA learning outcome with bilingual EN + GA fields.

    Populated from the NCCA syllabus PDFs via BAML extraction.
    """
    code: str  # e.g. "LC-MATH-LO-3.1.1"
    description_en: str
    description_ga: str
    stage: str  # aistear / primary / jc / sc / tertiary
    subject: str
    strand: str | None = None
    syllabus_pdf: str | None = None
    page: int | None = None
    visual_requirement: VisualRequirement | None = None


@dataclass
class SyllabusPage:
    """An indexed curriculum page with ColPali embeddings.

    Populated by the syllabus PDF ingestion pipeline. Each row carries
    the ColPali embedding (768-dim) + the page metadata + the learning
    outcomes that mention this page.
    """
    pdf_path: str
    page_number: int
    subject: str
    stage: str
    language: str  # en | ga | both
    raw_text: str
    colpali_embedding: list[float]  # 768-dim
    figures: list[dict[str, Any]] = field(default_factory=list)
    learning_outcomes: list[str] = field(default_factory=list)  # codes
    indexed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CurriculumConcept:
    """An extracted educational concept (the output of ExtractCurriculumConcept).

    The FIBO asset generator uses this to seed the FIBO prompt
    template + the JSON config.
    """
    concept_id: str
    title_en: str
    title_ga: str | None = None
    description: str = ""
    related_outcome_codes: list[str] = field(default_factory=list)
    visual_requirement: VisualRequirement | None = None
    source_pdf: str | None = None
    source_page: int | None = None
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class GeneratedAsset:
    """A FIBO-generated image asset (the output of FiboResource.render).

    Each asset carries the FIBO config that produced it + the iteration
    history (so we can trace back to the validation score + the prompt
    that scored highest).
    """
    asset_id: str
    concept_id: str
    subject: str
    language: str
    path: str  # local file path
    url: str   # canonical URL (local for now)
    sha256: str
    width: int
    height: int
    palette_hex: list[str]
    iteration: int  # the iteration index that produced this asset (1-indexed)
    validation_score: float  # 0-1, the VLM-based validation score
    fibo_config_id: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FiboConfig:
    """The canonical FIBO JSON configuration.

    A FIBO config is the typed payload that drives the FIBO renderer.
    It carries the per-element visual requirements (iconography +
    palette + motion) + the validation criteria (the prompts the
    ValidationResource uses to score the generated asset).
    """
    config_id: str
    concept_id: str
    language: str  # en | ga | both
    prompt: str
    palette_hex: list[str]
    iconography: list[str]
    width: int = 1024
    height: int = 1024
    validation_criteria: list[str] = field(default_factory=list)
    max_refinement_iterations: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


__all__ = [
    "VisualRequirement",
    "LearningOutcome",
    "SyllabusPage",
    "CurriculumConcept",
    "GeneratedAsset",
    "FiboConfig",
]
