"""
Celtic Education Research Agent - Deep research with citations.

Provides multi-step research workflow using Google ADK:
1. Planner: Generates search queries (LlmAgent)
2. Researcher: Executes searches and gathers information (LlmAgent + google_search)
3. Evaluator: Grades research quality (LlmAgent)
4. Composer: Creates cited research report (LlmAgent)

The agents are orchestrated via:
- LoopAgent: For researcher + evaluator iteration
- SequentialAgent: For full pipeline (planner → loop → composer)
"""
from __future__ import annotations

from typing import Literal

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from .callbacks.citation_callbacks import (
    citation_replacement_callback,
    collect_celtic_sources_callback,
)
from .config import config


# Structured output models
class SearchQuery(BaseModel):
    """A specific search query for Celtic education research."""

    search_query: str = Field(
        description="A specific, targeted query for Celtic education research."
    )


class ResearchFeedback(BaseModel):
    """Evaluation feedback on Celtic education research quality."""

    grade: Literal["pass", "fail"] = Field(
        description="'pass' if research is comprehensive, 'fail' if gaps remain."
    )
    comment: str = Field(
        description="Detailed evaluation with strengths and weaknesses."
    )
    follow_up_queries: list[SearchQuery] | None = Field(
        default=None,
        description="Follow-up queries to fill research gaps. Null if grade is 'pass'.",
    )


# Research planner agent
research_planner = LlmAgent(
    name="celtic_education_research_planner",
    model=config.model_name,
    description="Plans Celtic education research by generating targeted search queries.",
    instruction="""You are a Celtic education research planner.

Given a research topic, generate 3-5 specific search queries to gather comprehensive information.

Focus on:
1. Celtic education systems (Ireland, Scotland, Wales, Northern Ireland)
2. Curriculum frameworks (NCCA, SQA, Qualifications Wales)
3. Celtic language education (Irish, Scottish Gaelic, Welsh, Manx, Cornish)
4. Folklore and cultural resources (Dúchas.ie, NFC)
5. Academic sources on Celtic philology and education
6. Language technology and NLP resources

Generate queries that will find:
- Curriculum specifications and learning outcomes
- Official education resources (NCCA, examinations.ie, SEC)
- Academic papers on Celtic education
- Language resources (GAOIS, Teanglann, etc.)
- Folklore collections and transcriptions

Output your queries as a structured list.""",
    output_schema=list[SearchQuery],
)


# Research executor agent
researcher = LlmAgent(
    name="celtic_education_researcher",
    model=config.model_name,
    description="Executes Celtic education research using web search.",
    instruction="""You are a Celtic education researcher with expertise in:
- Irish education system (Primary, Junior Cycle, Senior Cycle, Leaving Certificate)
- Scottish education (CfE, National Qualifications, Highers)
- Welsh education (Foundation Phase, Key Stages)
- Irish (Gaeilge), Scottish Gaelic (Gàidhlig), Welsh (Cymraeg)
- Celtic linguistics and philology
- Irish folklore and cultural studies

Use the provided search tool to gather information on the research topic.
Synthesize findings from multiple sources.
Note any gaps or areas needing further research.

Key resources to look for:
- NCCA.ie (Irish curriculum)
- examinations.ie (SEC exam papers)
- curriculumonline.ie (Irish curriculum resources)
- GAOIS.ie (Logainm, Téarma, Ainm)
- Dúchas.ie (National Folklore Collection)
- Teanglann.ie (Dictionary)
- Universal Dependencies Celtic treebanks
- Celtic NLP academic papers

Provide detailed research notes with source attributions.""",
    tools=[google_search],
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(
            include_thoughts=True,
        )
    ),
    output_key="research_notes",
)


# Research evaluator agent
evaluator = LlmAgent(
    name="celtic_education_research_evaluator",
    model=config.model_name,
    description="Evaluates Celtic education research quality.",
    instruction="""You are a Celtic education research evaluator.

Assess the research notes for:
1. Comprehensiveness - Are all aspects of the topic covered?
2. Accuracy - Is the curriculum/linguistic information correct?
3. Source quality - Are sources authoritative (official curriculum, academic)?
4. Language coverage - Are relevant Celtic languages addressed?
5. Education level coverage - Are appropriate levels addressed?

Grade as 'pass' if research is sufficient for the user's needs.
Grade as 'fail' if significant gaps remain.

For failing grades, provide specific follow-up queries to fill gaps.

Consider Celtic education-specific aspects:
- Curriculum framework coverage?
- Learning outcomes documented?
- Assessment criteria noted?
- Initial mutations covered (for language topics)?
- Dialect variations noted?
- Historical/etymological context?
- Cross-nation curriculum comparisons where relevant?""",
    output_schema=ResearchFeedback,
    output_key="evaluation",
)


# Research composer agent
composer = LlmAgent(
    name="celtic_education_research_composer",
    model=config.model_name,
    description="Composes final Celtic education research report with citations.",
    instruction="""You are a Celtic education research composer.

Create a comprehensive, well-structured research report from the gathered notes.

Format guidelines:
1. Start with a summary of key findings
2. Organize by topic/education level/nation as appropriate
3. Include inline citations using <cite source="src-N"/> tags
4. Add a references section at the end
5. Use Irish/Celtic terminology with English glosses

Report structure:
- Executive Summary
- Main Findings
- Curriculum/Education Notes (if applicable)
- Language-Specific Notes (if applicable)
- Linguistic Analysis
- Cultural Context (for folklore topics)
- Sources and References

Ensure all claims are attributed to sources.""",
    output_key="final_cited_report",
)


# Research loop with evaluation
research_loop = LoopAgent(
    name="celtic_education_research_loop",
    max_iterations=config.max_research_iterations,
    sub_agents=[researcher, evaluator],
    after_agent_callback=collect_celtic_sources_callback,
)


# Full research agent pipeline
research_agent = SequentialAgent(
    name="celtic_education_research_agent",
    description="Comprehensive Celtic education research agent with citations.",
    sub_agents=[research_planner, research_loop, composer],
    after_agent_callback=citation_replacement_callback,
)


# Export the main agent for use
__all__ = [
    "ResearchFeedback",
    "SearchQuery",
    "composer",
    "evaluator",
    "research_agent",
    "research_loop",
    "research_planner",
    "researcher",
]
