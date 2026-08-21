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

from .config import (
    AgentConfig,
    config,
    LANGUAGE_NAMES,
    TRANSLATION_PAIRS,
    CURRICULUM_DOMAINS,
    EDUCATION_LEVELS,
    CURRICULUM_FRAMEWORKS,
    get_language_name,
    get_translation_models,
    get_education_levels,
    get_curriculum_framework,
)

from .translation_agent import (
    TranslationRequest,
    TranslationResult,
    TerminologyLookup,
    translate_text,
    get_supported_pairs,
    validate_language_pair,
    get_language_info,
)

from .corpus_agent import (
    SearchResult,
    CorpusSearchRequest,
    CorpusStats,
    search_corpus,
    get_corpus_stats,
    get_document,
    lookup_dictionary,
)

from .research_agent import (
    SearchQuery,
    ResearchFeedback,
    ResearchReport,
    generate_search_queries,
    execute_research,
    evaluate_research,
    compose_report,
    conduct_research,
)

from .callbacks import (
    # Celtic language callbacks
    collect_celtic_sources_callback,
    citation_replacement_callback,
    enhance_celtic_source_title,
    classify_celtic_source,
    # British Isles education callbacks
    collect_education_sources_callback,
    format_education_citations_callback,
    enhance_education_source_title,
    classify_education_source,
)

from .statistics_agent import (
    StatisticsAnalysis,
    BenchmarkReport,
    statistics_agent,
    trend_analyst,
    benchmarking_analyst,
    data_gap_identifier,
)

from .curriculum_comparison_agent import (
    CurriculumMapping,
    SubjectComparison,
    curriculum_comparison_agent,
    learning_outcome_mapper,
    assessment_comparator,
    bilingual_curriculum_expert,
)

from .enhanced_orchestrator import (
    TaskStatus,
    AgentTask,
    OrchestratorState,
    ClassifiedIntent,
    EnhancedIntentClassifier,
    AGUIEventEmitter,
    EnhancedOrchestrator,
    ValidationWorkflow,
    create_enhanced_orchestrator,
    get_enhanced_orchestrator,
    create_validation_workflow,
    enhance_root_agent,
)

from .geospatial_agent import (
    SpatialAnalysis,
    SchoolAccessAnalysis,
    geospatial_agent,
    deprivation_analyst,
    school_accessibility_analyst,
    regional_comparison_analyst,
)

from .education_research_agent import (
    ResearchQuery,
    ResearchFeedback as EducationResearchFeedback,
    ResearchEscalationChecker,
    education_research_planner,
    education_researcher,
    education_research_evaluator,
    follow_up_researcher,
    education_report_composer,
    education_research_pipeline,
    education_research_agent,
)

from .agui_curriculum_agent import (
    agui_curriculum_agent,
    create_agui_app,
    CurriculumUIState,
    CurriculumSearchResult,
    ComparisonTableRow,
    TranslationRequest as AGUITranslationRequest,
    AGUIEventType,
)

__all__ = [
    # Config
    "AgentConfig",
    "config",
    "LANGUAGE_NAMES",
    "TRANSLATION_PAIRS",
    "CURRICULUM_DOMAINS",
    "EDUCATION_LEVELS",
    "CURRICULUM_FRAMEWORKS",
    "get_language_name",
    "get_translation_models",
    "get_education_levels",
    "get_curriculum_framework",
    # Translation
    "TranslationRequest",
    "TranslationResult",
    "TerminologyLookup",
    "translate_text",
    "get_supported_pairs",
    "validate_language_pair",
    "get_language_info",
    # Corpus
    "SearchResult",
    "CorpusSearchRequest",
    "CorpusStats",
    "search_corpus",
    "get_corpus_stats",
    "get_document",
    "lookup_dictionary",
    # Research
    "SearchQuery",
    "ResearchFeedback",
    "ResearchReport",
    "generate_search_queries",
    "execute_research",
    "evaluate_research",
    "compose_report",
    "conduct_research",
    # Callbacks - Celtic
    "collect_celtic_sources_callback",
    "citation_replacement_callback",
    "enhance_celtic_source_title",
    "classify_celtic_source",
    # Callbacks - British Isles Education
    "collect_education_sources_callback",
    "format_education_citations_callback",
    "enhance_education_source_title",
    "classify_education_source",
    # Statistics
    "StatisticsAnalysis",
    "BenchmarkReport",
    "statistics_agent",
    "trend_analyst",
    "benchmarking_analyst",
    "data_gap_identifier",
    # Curriculum Comparison
    "CurriculumMapping",
    "SubjectComparison",
    "curriculum_comparison_agent",
    "learning_outcome_mapper",
    "assessment_comparator",
    "bilingual_curriculum_expert",
    # Enhanced Orchestrator
    "TaskStatus",
    "AgentTask",
    "OrchestratorState",
    "ClassifiedIntent",
    "EnhancedIntentClassifier",
    "AGUIEventEmitter",
    "EnhancedOrchestrator",
    "ValidationWorkflow",
    "create_enhanced_orchestrator",
    "get_enhanced_orchestrator",
    "create_validation_workflow",
    "enhance_root_agent",
    # Geospatial Agent
    "SpatialAnalysis",
    "SchoolAccessAnalysis",
    "geospatial_agent",
    "deprivation_analyst",
    "school_accessibility_analyst",
    "regional_comparison_analyst",
    # Education Research Agent
    "ResearchQuery",
    "EducationResearchFeedback",
    "ResearchEscalationChecker",
    "education_research_planner",
    "education_researcher",
    "education_research_evaluator",
    "follow_up_researcher",
    "education_report_composer",
    "education_research_pipeline",
    "education_research_agent",
    # AG-UI Curriculum Agent
    "agui_curriculum_agent",
    "create_agui_app",
    "CurriculumUIState",
    "CurriculumSearchResult",
    "ComparisonTableRow",
    "AGUITranslationRequest",
    "AGUIEventType",
]
