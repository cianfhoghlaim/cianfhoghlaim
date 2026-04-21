"""
Celtic Education Team - Agno Multi-Agent Coordination.

A coordinated team of specialized agents for Irish/Celtic education:
- Curriculum Agent: NCCA/SEC curriculum search and navigation
- Research Agent: Academic and Celtic resource discovery
- Translation Agent: Irish/Welsh/Scottish Gaelic/Manx translation
- Corpus Agent: Folklore (Dúchas) and linguistic corpus search
- Geospatial Agent: Location-based education queries
- Statistics Agent: Education statistics analysis

Uses Agno Team with share_member_interactions for context sharing.
Supports session persistence via SqliteDb.
"""

from __future__ import annotations

import os
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from pydantic import BaseModel, Field

# Session storage configuration
STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Create shared storage instance
team_storage = SqliteDb(
    session_table="education_team_sessions",
    db_file=str(STORAGE_DIR / "education_team.db"),
)

# Import custom tools - with fallback stubs if ADK not available
try:
    from ..tools.corpus_tools import CorpusSearchTools
    from ..tools.curriculum_tools import CurriculumSearchTools
    from ..tools.geospatial_tools import GeospatialTools
    from ..tools.translation_tools import TranslationTools
except ImportError:
    # Stub tools for AgentOS testing without full ADK stack
    class CurriculumSearchTools:
        """Stub curriculum search tools."""
        def search_curriculum(self, query: str) -> dict:
            return {"query": query, "results": [], "message": "Stub: Install ADK for full functionality"}

    class CorpusSearchTools:
        """Stub corpus search tools."""
        def search_corpus(self, query: str) -> dict:
            return {"query": query, "results": [], "message": "Stub: Install ADK for full functionality"}

    class GeospatialTools:
        """Stub geospatial tools."""
        def search_location(self, query: str) -> dict:
            return {"query": query, "results": [], "message": "Stub: Install ADK for full functionality"}

    class TranslationTools:
        """Stub translation tools."""
        def translate(self, text: str, target_lang: str = "ga") -> dict:
            return {"text": text, "translation": text, "message": "Stub: Install ADK for full functionality"}


# =============================================================================
# Structured Output Models
# =============================================================================


class CurriculumSearchResult(BaseModel):
    """Result from curriculum search."""

    query: str
    results: list[dict] = Field(default_factory=list)
    learning_outcomes: list[dict] = Field(default_factory=list)
    subject: str | None = None
    level: str | None = None
    nation: str = "ireland"


class ResearchReport(BaseModel):
    """Research report with sources."""

    topic: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    sources: list[dict] = Field(default_factory=list)
    celtic_resources: list[dict] = Field(default_factory=list)
    related_curriculum: list[str] = Field(default_factory=list)


class TranslationResult(BaseModel):
    """Translation between Celtic languages."""

    source_text: str
    source_language: str
    target_language: str
    translation: str
    terminology_notes: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class CorpusSearchResult(BaseModel):
    """Result from corpus/folklore search."""

    query: str
    source: str  # duchas, canuint, gaois, dil, etc.
    results: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class GeospatialResult(BaseModel):
    """Location-based education data."""

    query: str
    location: str | None = None
    schools: list[dict] = Field(default_factory=list)
    gaeltacht_areas: list[dict] = Field(default_factory=list)
    statistics: dict = Field(default_factory=dict)


class StatisticsResult(BaseModel):
    """Education statistics analysis."""

    query: str
    metrics: dict = Field(default_factory=dict)
    trends: list[dict] = Field(default_factory=list)
    comparisons: list[dict] = Field(default_factory=list)
    visualization_data: dict | None = None


class EducationResponse(BaseModel):
    """Unified response from education team."""

    query: str
    summary: str
    curriculum_info: CurriculumSearchResult | None = None
    research: ResearchReport | None = None
    translation: TranslationResult | None = None
    corpus_data: CorpusSearchResult | None = None
    geospatial_data: GeospatialResult | None = None
    statistics: StatisticsResult | None = None
    follow_up_suggestions: list[str] = Field(default_factory=list)


# =============================================================================
# Agent Definitions
# =============================================================================

# Default model configuration
DEFAULT_MODEL = os.getenv("AGNO_DEFAULT_MODEL", "gpt-4o")
GEMINI_MODEL = os.getenv("AGNO_GEMINI_MODEL", "gemini-2.0-flash")
CLAUDE_MODEL = os.getenv("AGNO_CLAUDE_MODEL", "claude-sonnet-4-20250514")


def get_model(model_type: str = "default"):
    """Get the appropriate model based on configuration."""
    if model_type == "gemini":
        return Gemini(id=GEMINI_MODEL)
    elif model_type == "claude":
        return Claude(id=CLAUDE_MODEL)
    else:
        return OpenAIChat(id=DEFAULT_MODEL)


# Curriculum Agent - Searches NCCA/SEC curriculum content
curriculum_agent = Agent(
    name="Curriculum Agent",
    model=get_model("default"),
    role="Searches Irish and Celtic curriculum content, including NCCA syllabi, "
    "SEC exam papers, learning outcomes, and cross-curricular connections. "
    "Specializes in primary, junior cycle, senior cycle, and Leaving Cert content.",
    tools=[CurriculumSearchTools()],
    instructions=[
        "Search curriculum using hybrid search (vector + keyword) for best results.",
        "Always include the education level and subject when available.",
        "Provide learning outcome codes (e.g., JC-MA-01) when referencing outcomes.",
        "Include bilingual (English/Irish) descriptions when available.",
        "Link to related strands and strand units within subjects.",
        "Consider cross-curricular connections to other subjects.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)

# Research Agent - Discovers academic and Celtic resources
research_agent = Agent(
    name="Research Agent",
    model=get_model("gemini"),  # Use Gemini for grounding
    role="Discovers and synthesizes research from academic sources and Celtic "
    "language resources. Searches GAOIS, arXiv, ACL Anthology, and Celtic "
    "digital humanities collections.",
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    instructions=[
        "Search for peer-reviewed research and authoritative Celtic sources.",
        "Prioritize Irish-language and Celtic-focused resources:",
        "  - GAOIS (gaois.ie) for terminology and language resources",
        "  - eDIL (dil.ie) for historical Irish dictionary",
        "  - DASG (dasg.ac.uk) for Scottish Gaelic",
        "  - Universal Dependencies for treebank data",
        "Include arXiv and ACL Anthology for NLP research on Celtic languages.",
        "Always cite sources with URLs and publication dates.",
        "Synthesize findings into actionable insights for educators.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)

# Translation Agent - Translates between Celtic languages
translation_agent = Agent(
    name="Translation Agent",
    model=get_model("claude"),  # Claude for nuanced translation
    role="Translates educational content between Celtic languages and English. "
    "Handles Irish (ga), Welsh (cy), Scottish Gaelic (gd), Manx (gv), "
    "Cornish (kw), and Breton (br). Preserves educational terminology.",
    tools=[TranslationTools()],
    instructions=[
        "Preserve educational terminology during translation.",
        "Use standardized (caighdeán) Irish unless dialect is specified.",
        "For technical terms, provide both the translation and original term.",
        "Note dialect variations when relevant (Connacht, Munster, Ulster).",
        "Include IPA pronunciation for key terms when helpful.",
        "Reference tearma.ie for official terminology.",
        "Maintain formatting (headings, lists, etc.) in translations.",
    ],
    markdown=True,
)

# Corpus Agent - Searches folklore and linguistic corpora
corpus_agent = Agent(
    name="Corpus Agent",
    model=get_model("default"),
    role="Searches Irish folklore and linguistic corpora including Dúchas.ie "
    "(National Folklore Collection), Canuint.ie (dialect recordings), "
    "Corpas na Gaeilge, and eDIL (Dictionary of Irish).",
    tools=[CorpusSearchTools()],
    instructions=[
        "Search Dúchas.ie for folklore, oral history, and traditional knowledge.",
        "Use Canuint.ie for dialect examples and pronunciation.",
        "Reference Corpas na Gaeilge for contemporary usage patterns.",
        "Include eDIL citations for historical/medieval Irish.",
        "Provide context about sources (collector, date, location).",
        "Link to primary source materials when available.",
        "Note oral tradition vs. written sources distinction.",
    ],
    markdown=True,
)

# Geospatial Agent - Location-based education queries
geospatial_agent = Agent(
    name="Geospatial Agent",
    model=get_model("default"),
    role="Handles location-based education queries including school locations, "
    "Gaeltacht areas, regional statistics, and geographic analysis of "
    "Irish-medium education.",
    tools=[GeospatialTools()],
    instructions=[
        "Use GeoParquet indexes for efficient spatial queries.",
        "Include Gaeltacht status for relevant locations.",
        "Provide distance calculations in kilometers.",
        "Reference CSO (Central Statistics Office) for population data.",
        "Include school roll numbers for precise identification.",
        "Note urban/rural classification for schools.",
        "Consider catchment areas for school analysis.",
    ],
    markdown=True,
)

# Statistics Agent - Education statistics analysis
statistics_agent = Agent(
    name="Statistics Agent",
    model=get_model("default"),
    role="Analyzes Irish education statistics from Department of Education, "
    "CSO, NCCA, and SEC. Provides trends, comparisons, and visualizations "
    "for metrics like enrollment, attainment, and Irish language uptake.",
    tools=[DuckDuckGoTools()],  # Placeholder - will use stats tools
    instructions=[
        "Reference official sources (gov.ie, cso.ie, ncca.ie, examinations.ie).",
        "Provide year-over-year trend analysis when available.",
        "Include confidence intervals for statistical estimates.",
        "Compare across nations (Ireland, UK nations) when relevant.",
        "Note data collection methodology and limitations.",
        "Format statistics clearly with units and periods.",
        "Suggest appropriate visualizations for the data.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# =============================================================================
# Education Team
# =============================================================================

education_team = Team(
    name="Celtic Education Team",
    model=get_model("default"),
    members=[
        curriculum_agent,
        research_agent,
        translation_agent,
        corpus_agent,
        geospatial_agent,
        statistics_agent,
    ],
    db=team_storage,  # Enable session persistence
    description=(
        "A coordinated team of AI agents specialized in Celtic education, "
        "Irish language learning, and pan-Celtic curriculum resources. "
        "Routes queries to the appropriate specialist agent(s) and "
        "synthesizes comprehensive responses."
    ),
    instructions=[
        # Query routing
        "Analyze the user's query to identify which agents are needed.",
        "For curriculum questions → Curriculum Agent",
        "For research/discovery → Research Agent",
        "For translation → Translation Agent",
        "For folklore/corpus → Corpus Agent",
        "For location-based queries → Geospatial Agent",
        "For statistics/trends → Statistics Agent",
        "",
        # Multi-agent coordination
        "Complex queries may require multiple agents working together:",
        "  - 'Translate this curriculum section' → Curriculum + Translation",
        "  - 'Find folklore about this topic in my area' → Corpus + Geospatial",
        "  - 'Compare Irish uptake across regions' → Statistics + Geospatial",
        "",
        # Response format
        "Always provide bilingual responses when the query involves Irish.",
        "Include source citations with URLs.",
        "Suggest follow-up questions to deepen exploration.",
        "Format responses for readability with headers and bullet points.",
        "",
        # Celtic language priority
        "Prioritize Irish (Gaeilge) content but include other Celtic languages:",
        "  - Welsh (Cymraeg) - especially for curriculum comparisons",
        "  - Scottish Gaelic (Gàidhlig) - DASG resources",
        "  - Manx (Gaelg) - revitalization context",
        "",
        # Education context
        "Consider the Irish education system structure:",
        "  - Primary (ages 4-12): Junior/Senior Infants through 6th Class",
        "  - Junior Cycle (ages 12-15): 1st-3rd Year",
        "  - Senior Cycle (ages 15-18): Transition Year, 5th-6th Year",
        "  - Leaving Certificate: Terminal examination",
    ],
    output_schema=EducationResponse,
    share_member_interactions=True,  # Key: enables context sharing between agents
    markdown=True,
    debug_mode=os.getenv("AGNO_DEBUG", "false").lower() == "true",
    show_members_responses=True,
)


# =============================================================================
# Convenience Functions
# =============================================================================


def ask_education_team(
    query: str,
    stream: bool = True,
    language: str = "en",
    session_id: str | None = None,
) -> EducationResponse:
    """
    Query the Celtic Education Team.

    Args:
        query: The user's question or request.
        stream: Whether to stream the response.
        language: Preferred response language ('en', 'ga', 'cy', 'gd').
        session_id: Optional session ID for conversation continuity.

    Returns:
        Structured EducationResponse with data from relevant agents.
    """
    # Add language hint to query if not English
    if language != "en":
        lang_names = {"ga": "Irish", "cy": "Welsh", "gd": "Scottish Gaelic", "gv": "Manx"}
        lang_hint = f"[Respond primarily in {lang_names.get(language, language)}] "
        query = lang_hint + query

    # Run with session ID for persistence
    run_kwargs = {"stream": stream}
    if session_id:
        run_kwargs["session_id"] = session_id

    return education_team.run(query, **run_kwargs)


def search_curriculum(
    query: str,
    level: str | None = None,
    subject: str | None = None,
    nation: str = "ireland",
) -> CurriculumSearchResult:
    """
    Direct curriculum search without full team coordination.

    Args:
        query: Search query.
        level: Education level (primary, junior_cycle, senior_cycle, leaving_cert).
        subject: Subject code (e.g., mathematics, irish, geography).
        nation: Nation (ireland, scotland, wales, england, northern_ireland).

    Returns:
        CurriculumSearchResult with matching content.
    """
    search_query = query
    if level:
        search_query += f" level:{level}"
    if subject:
        search_query += f" subject:{subject}"
    if nation != "ireland":
        search_query += f" nation:{nation}"

    return curriculum_agent.run(search_query)


def translate_content(
    text: str,
    source_language: str = "en",
    target_language: str = "ga",
    preserve_terminology: bool = True,
) -> TranslationResult:
    """
    Translate educational content between Celtic languages.

    Args:
        text: Text to translate.
        source_language: Source language code (en, ga, cy, gd, gv, kw, br).
        target_language: Target language code.
        preserve_terminology: Whether to preserve educational terms.

    Returns:
        TranslationResult with translation and notes.
    """
    query = f"Translate from {source_language} to {target_language}"
    if preserve_terminology:
        query += " (preserve educational terminology)"
    query += f": {text}"

    return translation_agent.run(query)


def search_corpus(
    query: str,
    source: str | None = None,
) -> CorpusSearchResult:
    """
    Search folklore and linguistic corpora.

    Args:
        query: Search query.
        source: Specific corpus (duchas, canuint, gaois, dil, corpas).

    Returns:
        CorpusSearchResult with matching items.
    """
    search_query = query
    if source:
        search_query = f"[Search {source}] {query}"

    return corpus_agent.run(search_query)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Celtic Education Team - Interactive Mode")
    print("=" * 50)
    print("Ask questions about Irish/Celtic education, curriculum,")
    print("translation, folklore, or education statistics.")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            query = input("\nYou: ").strip()
            if query.lower() in ("exit", "quit", "q"):
                print("Slán go fóill! (Goodbye!)")
                break
            if not query:
                continue

            print("\nEducation Team:")
            education_team.print_response(query, stream=True)

        except KeyboardInterrupt:
            print("\nSlán go fóill! (Goodbye!)")
            break
        except Exception as e:
            print(f"Error: {e}")
