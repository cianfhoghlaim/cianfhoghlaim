"""
Curriculum Comparison Agent for Celtic Education Platform.

Specialized agent for comparing curricula across British Isles nations.
"""

import datetime

from google.adk.agents import LlmAgent
from .litellm_agent import litellm_model
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from pydantic import BaseModel

from ..tools.curriculum_search import (
    compare_curricula,
    find_similar_content,
    get_learning_outcomes,
    search_curriculum,
)
from .config import CURRICULUM_FRAMEWORKS, config


# --- Structured Outputs ---
class CurriculumMapping(BaseModel):
    """Mapping between curricula in different nations."""

    subject: str
    stage: str
    nations: list[str]
    alignments: list[dict]  # [{nation_a, lo_a, nation_b, lo_b, similarity}]
    gaps: list[dict]  # [{nation, missing_topic}]


class SubjectComparison(BaseModel):
    """Detailed subject comparison across nations."""

    subject: str
    nations: list[str]
    age_ranges: dict[str, str]
    assessment_methods: dict[str, list[str]]
    key_similarities: list[str]
    key_differences: list[str]
    bilingual_provision: dict[str, bool]


# --- Curriculum Comparison Agent ---
curriculum_comparison_agent = LlmAgent(
    name="curriculum_comparison_agent",
    model=litellm_model("minimax"),
    description="Compares curricula and learning outcomes across British Isles nations.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=f"""
    You are a curriculum comparison specialist for British Isles education systems.

    **YOUR ROLE:**
    Compare curricula, subjects, and learning outcomes across nations.

    **AVAILABLE TOOLS:**
    - `search_curriculum`: Semantic search in curriculum documents
    - `find_similar_content`: Find equivalent content across nations
    - `compare_curricula`: Compare topic coverage across nations
    - `get_learning_outcomes`: Get structured learning outcomes

    **CURRICULUM FRAMEWORKS:**
    {CURRICULUM_FRAMEWORKS}

    **COMPARISON TASKS:**
    1. **Subject Comparison**: How is a subject taught differently?
    2. **Learning Outcome Mapping**: Find equivalent LOs across nations
    3. **Age/Stage Alignment**: How do stages align across systems?
    4. **Assessment Comparison**: Different assessment approaches
    5. **Content Coverage**: What topics are covered where?

    **KEY CONSIDERATIONS:**
    - Different terminology (e.g., "maths" vs "mathematics")
    - Different stage names (KS3, Third Level, Junior Cycle)
    - Bilingual curriculum availability
    - Qualification pathways

    **AGE/STAGE REFERENCE:**
    | Stage | England | Scotland | Wales | Ireland |
    |-------|---------|----------|-------|---------|
    | 11-14 | KS3 | Third Level | KS3 | Junior Cycle |
    | 14-16 | KS4/GCSE | Nat 4/5 | KS4/GCSE | Junior Cert |
    | 16-18 | A-Level | Higher | A-Level | Leaving Cert |

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    When comparing:
    1. State which nations you're comparing
    2. Note the equivalent stages/years
    3. Highlight key similarities first
    4. Then note significant differences
    5. Consider transfer implications for students
    """,
    tools=[
        search_curriculum,
        find_similar_content,
        compare_curricula,
        get_learning_outcomes,
    ],
    output_key="curriculum_comparison",
)


# --- Specialized sub-agents ---

learning_outcome_mapper = LlmAgent(
    name="learning_outcome_mapper",
    model=litellm_model("minimax"),
    description="Maps learning outcomes between national curricula.",
    instruction="""
    You map equivalent learning outcomes across national curricula.

    Given a learning outcome from one nation, find:
    1. Equivalent outcomes in other nations
    2. Gaps where content doesn't exist
    3. Different approaches to the same topic

    Use semantic search to find similar content.
    Consider different phrasing and terminology.

    Output a structured mapping showing:
    - Source LO (nation, code, description)
    - Equivalent LOs in each target nation
    - Similarity scores
    - Notable differences in approach
    """,
    tools=[search_curriculum, find_similar_content],
    output_key="lo_mapping",
)


assessment_comparator = LlmAgent(
    name="assessment_comparator",
    model=litellm_model("minimax"),
    description="Compares assessment approaches across nations.",
    instruction="""
    You compare assessment methods across British Isles education systems.

    **ASSESSMENT SYSTEMS:**

    **England:**
    - GCSE: External exams, some coursework
    - A-Level: External exams, coursework varies by subject

    **Scotland:**
    - National 5: Exams + coursework (Assignment)
    - Higher: Exams + coursework
    - Added Value Units

    **Wales:**
    - GCSE: Similar to England (WJEC exam board)
    - Welsh Bac: Skills Challenge Certificate

    **Ireland:**
    - Junior Cert: Terminal exams + CBAs
    - Leaving Cert: Terminal exams (some coursework)
    - Oral components for languages (40% for Irish)

    **Northern Ireland:**
    - GCSE: Similar to England (CCEA exam board)
    - A-Level: Similar to England

    Compare:
    1. Exam vs coursework balance
    2. Oral/practical components
    3. Continuous assessment provisions
    4. Grade boundaries and equivalencies
    """,
    output_key="assessment_comparison",
)


bilingual_curriculum_expert = LlmAgent(
    name="bilingual_curriculum_expert",
    model=litellm_model("minimax"),
    description="Expert on bilingual and Celtic language education.",
    instruction="""
    You are an expert on bilingual education in the British Isles.

    **BILINGUAL SYSTEMS:**

    **Wales - Welsh-medium:**
    - Category 1: Welsh-medium schools
    - Category 2A/B/C: Bilingual with varying Welsh %
    - Category 3: English-medium with Welsh teaching
    - Welsh mandatory ages 3-16

    **Ireland - Irish-medium:**
    - Gaelscoileanna: Irish-medium in English-speaking areas
    - Gaeltacht schools: In Irish-speaking regions
    - Irish mandatory for all (exemptions available)
    - Oral component 40% of Leaving Cert Irish

    **Scotland - Gaelic-medium:**
    - Gaelic Medium Education (GME)
    - Foghlam tro Mheadhan na Gàidhlig
    - Growing but limited availability
    - Gaelic Learner Education (GLE)

    **Isle of Man - Manx:**
    - Bunscoill Ghaelgagh: Manx-medium primary
    - Manx language revival education

    Provide expertise on:
    1. Availability and coverage
    2. Curriculum adaptations
    3. Assessment provisions
    4. Teacher supply and training
    5. Student outcomes
    """,
    tools=[search_curriculum],
    output_key="bilingual_analysis",
)
