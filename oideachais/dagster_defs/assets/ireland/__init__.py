"""
Ireland Education Assets with MultiPartition.

This package contains Dagster assets for Ireland education data,
organized by cycle with MultiPartition.

Curriculum Assets:
    ireland/curriculum/senior_cycle   <- MultiPartition(subject, language)
    ireland/curriculum/junior_cycle   <- MultiPartition(subject, language)
    ireland/curriculum/primary        <- MultiPartition(subject, language)
    ireland/curriculum/early_childhood <- MultiPartition(subject, language)

Exam Materials Assets:
    ireland/exam_materials/leaving_certificate         <- MultiPartition(subject, material_type)
    ireland/exam_materials/junior_cycle                  <- MultiPartition(subject, material_type)
    ireland/exam_materials/leaving_certificate_applied  <- MultiPartition(subject, material_type)

Usage:
    from oideachais.dagster_defs.assets.ireland import curriculum_dlt_assets, exam_materials_assets

    defs = Definitions(assets=[*curriculum_dlt_assets, *exam_materials_assets])
"""
from __future__ import annotations

from .curriculum_dlt_assets import (
    CYCLE_PARTITIONS,
    CYCLE_SUBJECTS,
    CYCLES,
    DLT_DATASET_NAME as CURRICULUM_DATASET_NAME,
    DLT_PIPELINE_NAME as CURRICULUM_PIPELINE_NAME,
    DLT_PIPELINES_DIR as CURRICULUM_PIPELINES_DIR,
    create_all_curriculum_assets,
    create_cycle_asset,
    curriculum_dlt_assets,
)
from .exam_materials_assets import (
    DLT_DATASET_NAME,
    DLT_PIPELINE_NAME,
    DLT_PIPELINES_DIR,
    EXAM_CYCLES,
    EXAM_PARTITIONS,
    EXAM_SUBJECTS,
    MATERIAL_TYPES,
    ExamMaterialsConfig,
    create_all_exam_materials_assets,
    create_exam_asset,
    exam_materials_assets,
)
from .firecrawl_assets import scraped_curriculum_pages

__all__ = [
    # Curriculum
    "curriculum_dlt_assets",
    "scraped_curriculum_pages",
    "create_cycle_asset",
    "create_all_curriculum_assets",
    "CYCLE_PARTITIONS",
    "CYCLES",
    "CYCLE_SUBJECTS",
    "CURRICULUM_PIPELINE_NAME",
    "CURRICULUM_DATASET_NAME",
    "CURRICULUM_PIPELINES_DIR",
    # Exam Materials
    "exam_materials_assets",
    "create_exam_asset",
    "create_all_exam_materials_assets",
    "EXAM_PARTITIONS",
    "EXAM_CYCLES",
    "EXAM_SUBJECTS",
    "MATERIAL_TYPES",
    "ExamMaterialsConfig",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
