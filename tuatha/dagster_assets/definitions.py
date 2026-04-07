"""
Dagster Definitions for Tuath.

Orchestrates Celtic curriculum ingestion, mythology data, embedding pipelines,
and FIBO educational asset generation for the Celtic Educational MMO platform.
"""

from dagster import (
    Definitions,
    define_asset_job,
    load_assets_from_modules,
)

from . import curriculum_assets, embedding_assets, mythology_assets
from ..fibo_generation import assets as fibo_assets
from ..fibo_generation.resources import FiboResource, ValidationResource
from .schedules import (
    daily_curriculum_schedule,
    daily_embedding_schedule,
    full_pipeline_schedule,
    game_content_schedule,
    index_rebuild_schedule,
    weekly_exam_papers_schedule,
    weekly_mythology_schedule,
)

# Load all assets from modules
curriculum_asset_list = load_assets_from_modules([curriculum_assets])
mythology_asset_list = load_assets_from_modules([mythology_assets])
embedding_asset_list = load_assets_from_modules([embedding_assets])
fibo_asset_list = load_assets_from_modules([fibo_assets])

# Define jobs
curriculum_sync_job = define_asset_job(
    name="curriculum_sync_job",
    selection=curriculum_asset_list,
    description="Sync Celtic curriculum from NCCA, WJEC, SQA, and other bodies",
    tags={"domain": "curriculum", "pipeline": "tuath"},
)

mythology_sync_job = define_asset_job(
    name="mythology_sync_job",
    selection=mythology_asset_list,
    description="Sync mythology data for NPCs and game content",
    tags={"domain": "mythology", "pipeline": "tuath"},
)

embedding_pipeline_job = define_asset_job(
    name="embedding_pipeline_job",
    selection=embedding_asset_list,
    description="Generate BGE-M3 embeddings for curriculum and mythology",
    tags={"domain": "embeddings", "pipeline": "tuath"},
)

exam_papers_job = define_asset_job(
    name="exam_papers_job",
    selection=["curriculum_exam_papers"],
    description="Fetch historical exam papers from examination bodies",
    tags={"domain": "curriculum", "pipeline": "tuath"},
)

rebuild_indexes_job = define_asset_job(
    name="rebuild_indexes_job",
    selection=["create_vector_indexes"],
    description="Rebuild LanceDB vector indexes",
    tags={"domain": "embeddings", "pipeline": "tuath"},
)

# Game content refresh job (subset of assets)
game_content_refresh_job = define_asset_job(
    name="game_content_refresh_job",
    selection=["mythology_aggregate", "curriculum_aggregate_stats"],
    description="Refresh game content caches",
    tags={"domain": "game", "pipeline": "tuath"},
)

# FIBO educational asset generation job
fibo_generation_job = define_asset_job(
    name="fibo_generation_job",
    selection=fibo_asset_list,
    description="Generate educational visual assets using FIBO framework",
    tags={"domain": "fibo", "pipeline": "tuath"},
)

# Full pipeline job (excludes FIBO which requires LiteLLM)
full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=curriculum_asset_list + mythology_asset_list + embedding_asset_list,
    description="Run the complete Tuath data pipeline",
    tags={"pipeline": "tuath", "type": "full"},
)

# Complete pipeline including FIBO generation
complete_pipeline_job = define_asset_job(
    name="complete_pipeline_job",
    selection=curriculum_asset_list + mythology_asset_list + embedding_asset_list + fibo_asset_list,
    description="Run complete Tuath pipeline including FIBO asset generation",
    tags={"pipeline": "tuath", "type": "complete"},
)

# Combine all definitions
defs = Definitions(
    assets=curriculum_asset_list + mythology_asset_list + embedding_asset_list + fibo_asset_list,
    jobs=[
        curriculum_sync_job,
        mythology_sync_job,
        embedding_pipeline_job,
        exam_papers_job,
        rebuild_indexes_job,
        game_content_refresh_job,
        full_pipeline_job,
        fibo_generation_job,
        complete_pipeline_job,
    ],
    schedules=[
        daily_curriculum_schedule,
        weekly_mythology_schedule,
        daily_embedding_schedule,
        weekly_exam_papers_schedule,
        full_pipeline_schedule,
        index_rebuild_schedule,
        game_content_schedule,
    ],
    resources={
        "fibo_resource": FiboResource(
            litellm_api_base="http://localhost:4000",
            model="flux-schnell",
        ),
        "validation_resource": ValidationResource(
            validation_threshold=0.7,
            max_refinement_iterations=3,
            vlm_model="gpt-4-vision-preview",
            litellm_api_base="http://localhost:4000",
        ),
    },
)
