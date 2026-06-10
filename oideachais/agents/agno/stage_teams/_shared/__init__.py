"""Shared sub-agents package — Cianfhoghlaim Oideachais stage teams."""
from .curriculum_scout import CurriculumScout
from .translation_agent import TranslationAgent
from .cognee_graph_query import CogneeGraphQuery
from .source_citer import SourceCiter

__all__ = [
    "CurriculumScout",
    "TranslationAgent",
    "CogneeGraphQuery",
    "SourceCiter",
]
