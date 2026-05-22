"""
FIBO Educational Asset Generation for Tuath.

Provides Dagster assets and resources for generating educational
visual assets from curriculum concepts using the FIBO framework.

Components:
- schemas: Data models for curriculum concepts and generated assets
- resources: Dagster resources for FIBO generation and validation
- assets: Dagster assets for the generation pipeline
"""

from .schemas import (
    SyllabusPage,
    CurriculumConcept,
    GeneratedAsset,
    VisualRequirement,
    LearningOutcome,
)
from .resources import FiboResource, ValidationResource
from .assets import fibo_json_configs, generated_images

__all__ = [
    # Schemas
    "SyllabusPage",
    "CurriculumConcept",
    "GeneratedAsset",
    "VisualRequirement",
    "LearningOutcome",
    # Resources
    "FiboResource",
    "ValidationResource",
    # Assets
    "fibo_json_configs",
    "generated_images",
]
