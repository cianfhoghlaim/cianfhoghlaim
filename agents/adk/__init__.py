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
- Image Generation Agent: consumes the 5 ``image_gen`` MODEL_REGISTRY
  entries for 2D assets + Babylon.js textures (per
  2026-08-13-web-monorepo-consolidation-and-agent-integration-v1, Phase L)
"""
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

# Stage agents (4-stage plane per the 2026-08-26-mega-3a-baml-and-adk-v1
# change). Each agent is auto-generated from the corresponding BAML
# stage template + uses `BAMLFunctionTool` to wire the per-stage
# extraction functions.
from .lc_subject_agent import lc_subject_agent, LC_SUBJECT_FUNCTIONS
from .jc_subject_agent import jc_subject_agent, JC_SUBJECT_FUNCTIONS
from .alevel_subject_agent import alevel_subject_agent, ALEVEL_FUNCTIONS
from .gcse_subject_agent import gcse_subject_agent, GCSE_FUNCTIONS

__all__ = [
    "lc_subject_agent",
    "LC_SUBJECT_FUNCTIONS",
    "jc_subject_agent",
    "JC_SUBJECT_FUNCTIONS",
    "alevel_subject_agent",
    "ALEVEL_FUNCTIONS",
    "gcse_subject_agent",
    "GCSE_FUNCTIONS",
]
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
from .celtic_tutor_agent import celtic_tutor_agent
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
from .email_triage_agent import (
    EmailClassificationResult,
    EmailThreadSummary,
    ResearchLink,
    ThreadSummary,
    classify_email_thread,
    email_triage_agent,
    find_loose_threads,
    link_thread_to_research,
    summarise_thread,
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
from .image_generation_agent import (
    image_generation_agent,
    wire_image_generation_agent,
)
from .mythology_narrator_agent import mythology_narrator_agent
from .quest_guide_agent import quest_guide_agent
from .research_agent import (
    ResearchFeedback,
    SearchQuery,
)
from .research_assistant_agent import research_assistant_agent
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
from .tuatha_root_agent import root_agent as tuatha_root_agent

__all__ = [
    "CURRICULUM_DOMAINS",
    "CURRICULUM_FRAMEWORKS",
    "EDUCATION_LEVELS",
    "LANGUAGE_NAMES",
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
    # Email Triage Agent (10th ADK agent, leabharlann-email-inbox-pipeline)
    "EmailClassificationResult",
    "EmailThreadSummary",
    "EnhancedIntentClassifier",
    "EnhancedOrchestrator",
    "OrchestratorState",
    "ResearchEscalationChecker",
    "ResearchFeedback",
    # Education Research Agent
    "ResearchQuery",
    "ResearchReport",
    "ResearchLink",
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
    # Thread summary (email_triage)
    "ThreadSummary",
    # Translation
    "TranslationRequest",
    "TranslationResult",
    "ValidationWorkflow",
    # AG-UI Curriculum Agent
    "agui_curriculum_agent",
    "assessment_comparator",
    "benchmarking_analyst",
    "bilingual_curriculum_expert",
    # Tuatha MMO agents (round 7 phase 5; thin re-exports live in
    # `tuatha.agents.adk.*`). Each module is the canonical
    # implementation; the tuatha files are 10-30 line re-exports.
    "celtic_tutor_agent",
    "citation_replacement_callback",
    "classify_celtic_source",
    "classify_email_thread",
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
    "email_triage_agent",
    "enhance_celtic_source_title",
    "enhance_education_source_title",
    "enhance_root_agent",
    "evaluate_research",
    "execute_research",
    "find_loose_threads",
    "follow_up_researcher",
    "format_education_citations_callback",
    "generate_search_queries",
    "geospatial_agent",
    "get_corpus_stats",
    # Image Generation (Phase L)
    "image_generation_agent",
    "wire_image_generation_agent",
    "get_curriculum_framework",
    "get_document",
    "get_education_levels",
    "get_enhanced_orchestrator",
    "get_language_info",
    "get_language_name",
    "get_supported_pairs",
    "get_translation_models",
    "learning_outcome_mapper",
    "link_thread_to_research",
    "lookup_dictionary",
    "mythology_narrator_agent",
    "quest_guide_agent",
    "regional_comparison_analyst",
    "research_assistant_agent",
    "school_accessibility_analyst",
    "search_corpus",
    "statistics_agent",
    "summarise_thread",
    "translate_text",
    "trend_analyst",
    "tuatha_root_agent",
    "validate_language_pair",
]
