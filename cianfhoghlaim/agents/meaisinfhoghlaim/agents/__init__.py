"""
Celtic Education ADK Agents.

Provides AI agents for the Celtic Education Platform:
- Root Agent: Main orchestrator for education queries
- Curriculum Agent: NCCA/SEC curriculum expertise
- Translation Agent: Celtic language translation
- Corpus Agent: Celtic corpus search and analysis
- Research Agent: Deep research with citations (Celtic focus)
- Education Research Agent: Cross-nation education policy research
- Geospatial Agent: LSOA/Data Zone spatial analysis
- Statistics Agent: Education metrics and benchmarking
- Curriculum Comparison Agent: Cross-nation curriculum mapping
"""
from __future__ import annotations

# Canonical model-layer agent registry (1 root + 12 specialists = 13 modules).
# This tuple is the single source of truth for the model-layer agent
# inventory; the OpenCode sruth-subagents in `opencode.json` dispatch to
# these modules via their prompts. The 13 names mirror the actual
# `.py` modules in this directory; do not list a name that does not
# have a corresponding module.
MODEL_LAYER_AGENTS: tuple[str, ...] = (
    "root_agent",
    "curriculum_agent",
    "translation_agent",
    "corpus_agent",
    "research_agent",
    "education_research_agent",
    "bunchloch_research_agent",
    "geospatial_agent",
    "statistics_agent",
    "curriculum_comparison_agent",
    "agui_curriculum_agent",
    "mcp_curriculum_agent",
    "voice_agent",
)

from .agui_curriculum_agent import (
    AGUIEventType,
    ComparisonTableRow,
    CurriculumSearchResult,
    CurriculumUIState,
    agui_curriculum_agent,
    create_agui_app,
)
from .agui_curriculum_agent import (
    TranslationRequest as AGUITranslationRequest,
)
from .callbacks import (
    citation_replacement_callback,
    classify_celtic_source,
    classify_education_source,
    # Celtic language callbacks
    collect_celtic_sources_callback,
    # British Isles education callbacks
    collect_education_sources_callback,
    enhance_celtic_source_title,
    enhance_education_source_title,
    format_education_citations_callback,
)
from .config import (
    CURRICULUM_DOMAINS,
    CURRICULUM_FRAMEWORKS,
    EDUCATION_LEVELS,
    LANGUAGE_NAMES,
    TRANSLATION_PAIRS,
    AgentConfig,
    config,
    get_curriculum_framework,
    get_education_levels,
    get_language_name,
    get_translation_models,
)
from .corpus_agent import (
    CorpusSearchRequest,
    CorpusStats,
    SearchResult,
    get_corpus_stats,
    get_document,
    lookup_dictionary,
    search_corpus,
)
from .curriculum_comparison_agent import (
    CurriculumMapping,
    SubjectComparison,
    assessment_comparator,
    bilingual_curriculum_expert,
    curriculum_comparison_agent,
    learning_outcome_mapper,
)
from .education_research_agent import (
    ResearchEscalationChecker,
    ResearchQuery,
    education_report_composer,
    education_research_agent,
    education_research_evaluator,
    education_research_pipeline,
    education_research_planner,
    education_researcher,
    follow_up_researcher,
)
from .education_research_agent import (
    ResearchFeedback as EducationResearchFeedback,
)
from .enhanced_orchestrator import (
    AgentTask,
    AGUIEventEmitter,
    ClassifiedIntent,
    EnhancedIntentClassifier,
    EnhancedOrchestrator,
    OrchestratorState,
    TaskStatus,
    ValidationWorkflow,
    create_enhanced_orchestrator,
    create_validation_workflow,
    enhance_root_agent,
    get_enhanced_orchestrator,
)
from .geospatial_agent import (
    SchoolAccessAnalysis,
    SpatialAnalysis,
    deprivation_analyst,
    geospatial_agent,
    regional_comparison_analyst,
    school_accessibility_analyst,
)
from .research_agent import (
    ResearchFeedback,
    ResearchReport,
    SearchQuery,
    compose_report,
    conduct_research,
    evaluate_research,
    execute_research,
    generate_search_queries,
)
from .statistics_agent import (
    BenchmarkReport,
    StatisticsAnalysis,
    benchmarking_analyst,
    data_gap_identifier,
    statistics_agent,
    trend_analyst,
)
from .translation_agent import (
    TerminologyLookup,
    TranslationRequest,
    TranslationResult,
    get_language_info,
    get_supported_pairs,
    translate_text,
    validate_language_pair,
)

__all__ = [
    "CURRICULUM_DOMAINS",
    "CURRICULUM_FRAMEWORKS",
    "EDUCATION_LEVELS",
    "LANGUAGE_NAMES",
    # Canonical model-layer agent registry
    "MODEL_LAYER_AGENTS",
    "TRANSLATION_PAIRS",
    "AGUIEventEmitter",
    "AGUIEventType",
    "AGUITranslationRequest",
    # Config
    "AgentConfig",
    "AgentTask",
    "BenchmarkReport",
    "ClassifiedIntent",
    "ComparisonTableRow",
    "CorpusSearchRequest",
    "CorpusStats",
    # Curriculum Comparison
    "CurriculumMapping",
    "CurriculumSearchResult",
    "CurriculumUIState",
    "EducationResearchFeedback",
    "EnhancedIntentClassifier",
    "EnhancedOrchestrator",
    "OrchestratorState",
    "ResearchEscalationChecker",
    "ResearchFeedback",
    # Education Research Agent
    "ResearchQuery",
    "ResearchReport",
    "SchoolAccessAnalysis",
    # Research
    "SearchQuery",
    # Corpus
    "SearchResult",
    # Geospatial Agent
    "SpatialAnalysis",
    # Statistics
    "StatisticsAnalysis",
    "SubjectComparison",
    # Enhanced Orchestrator
    "TaskStatus",
    "TerminologyLookup",
    # Translation
    "TranslationRequest",
    "TranslationResult",
    "ValidationWorkflow",
    # AG-UI Curriculum Agent
    "agui_curriculum_agent",
    "assessment_comparator",
    "benchmarking_analyst",
    "bilingual_curriculum_expert",
    "citation_replacement_callback",
    "classify_celtic_source",
    "classify_education_source",
    # Callbacks - Celtic
    "collect_celtic_sources_callback",
    # Callbacks - British Isles Education
    "collect_education_sources_callback",
    "compose_report",
    "conduct_research",
    "config",
    "create_agui_app",
    "create_enhanced_orchestrator",
    "create_validation_workflow",
    "curriculum_comparison_agent",
    "data_gap_identifier",
    "deprivation_analyst",
    "education_report_composer",
    "education_research_agent",
    "education_research_evaluator",
    "education_research_pipeline",
    "education_research_planner",
    "education_researcher",
    "enhance_celtic_source_title",
    "enhance_education_source_title",
    "enhance_root_agent",
    "evaluate_research",
    "execute_research",
    "follow_up_researcher",
    "format_education_citations_callback",
    "generate_search_queries",
    "geospatial_agent",
    "get_corpus_stats",
    "get_curriculum_framework",
    "get_document",
    "get_education_levels",
    "get_enhanced_orchestrator",
    "get_language_info",
    "get_language_name",
    "get_supported_pairs",
    "get_translation_models",
    "learning_outcome_mapper",
    "lookup_dictionary",
    "regional_comparison_analyst",
    "school_accessibility_analyst",
    "search_corpus",
    "statistics_agent",
    "translate_text",
    "trend_analyst",
    "validate_language_pair",
]
