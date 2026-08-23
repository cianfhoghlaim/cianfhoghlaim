"""
FIBO Educational Asset Generation for Tuath.

Provides Dagster assets and resources for generating educational
visual assets from curriculum concepts using the FIBO framework.

Components:
- schemas: Data models for curriculum concepts and generated assets
- resources: Dagster resources for FIBO generation and validation
- assets: Dagster assets for the generation pipeline
"""

from .assets import (
    fibo_configs_from_syllabus_diagrams,
    fibo_json_configs,
    generated_images,
)
from .resources import FiboResource, ValidationResource
from .schemas import (
    CurriculumConcept,
    GeneratedAsset,
    LearningOutcome,
    SyllabusPage,
    VisualRequirement,
)

__all__ = [
    "CurriculumConcept",
    # Resources
    "FiboResource",
    "GeneratedAsset",
    "LearningOutcome",
    # Schemas
    "SyllabusPage",
    "ValidationResource",
    "VisualRequirement",
    # Assets
    "fibo_json_configs",
    "generated_images",
    "fibo_configs_from_syllabus_diagrams",
]
