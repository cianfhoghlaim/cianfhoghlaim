"""tuatha/asset_generation/fibo/__init__.py — FIBO Educational Asset Generation for Tuath.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Provides Dagster assets and resources for generating educational
visual assets from curriculum concepts using the FIBO framework.

Components:
- schemas: VisualRequirement + LearningOutcome + SyllabusPage +
  CurriculumConcept + GeneratedAsset + FiboConfig (the dataclasses)
- education_fibo: the 8 syllabus-conditioned prompts (one per NCCA
  Leaving Certificate subject)
- resources: FiboResource (FIBO image generation via LiteLLM) +
  ValidationResource (VLM-based validation)
- assets: fibo_json_configs + generated_images + fibo_configs_from_syllabus_diagrams
  (the 3 Dagster assets)

Reference: openspec/changes/2026-10-04-fibo-asset-pipeline-v1/specs/fibo-asset-pipeline/spec.md
"""
from __future__ import annotations

from . import assets
from . import resources
from . import schemas
from .assets import (
    fibo_configs_from_syllabus_diagrams,
    fibo_json_configs,
    generated_images,
)
from .education_fibo import EDUCATION_FIBO_PROMPTS, get_fibo_prompt, list_subjects
from .resources import FiboConfig, FiboResource, ValidationResource
from .schemas import (
    CurriculumConcept,
    GeneratedAsset,
    LearningOutcome,
    SyllabusPage,
    VisualRequirement,
)

__all__ = [
    # Submodules
    "assets",
    "resources",
    "schemas",
    # Dagster assets
    "fibo_configs_from_syllabus_diagrams",
    "fibo_json_configs",
    "generated_images",
    # Dagster resources
    "FiboConfig",
    "FiboResource",
    "ValidationResource",
    # Dataclasses
    "CurriculumConcept",
    "GeneratedAsset",
    "LearningOutcome",
    "SyllabusPage",
    "VisualRequirement",
    # Helpers
    "EDUCATION_FIBO_PROMPTS",
    "get_fibo_prompt",
    "list_subjects",
]
