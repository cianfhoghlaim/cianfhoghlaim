"""
Dagster Assets for Tuath.

Celtic Educational MMO data pipeline orchestration.
"""

from .curriculum_assets import (
    tuath_curriculum_context,
    tuath_curriculum_stats,
    tuath_learning_games,
    tuath_mythology_curriculum_links,
)
from .embedding_assets import (
    curriculum_embeddings,
    embedding_stats,
    mythology_embeddings,
)
from .mythology_assets import (
    celtic_characters,
    celtic_locations,
    celtic_stories,
    mythology_aggregate,
)
from .schedules import (
    daily_curriculum_schedule,
    daily_embedding_schedule,
    weekly_mythology_schedule,
)

# FIBO generation assets are loaded separately in definitions.py
# from tuath.fibo_generation module

__all__ = [
    # Curriculum
    "tuath_curriculum_context",
    "tuath_curriculum_stats",
    "tuath_learning_games",
    "tuath_mythology_curriculum_links",
    # Mythology
    "celtic_characters",
    "celtic_stories",
    "celtic_locations",
    "mythology_aggregate",
    # Embeddings
    "curriculum_embeddings",
    "mythology_embeddings",
    "embedding_stats",
    # Schedules
    "daily_curriculum_schedule",
    "weekly_mythology_schedule",
    "daily_embedding_schedule",
]
