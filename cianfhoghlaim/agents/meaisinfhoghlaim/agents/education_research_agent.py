"""
Education Research Agent for British Isles Education Platform.

Deep research agent for cross-nation education policy and practice.
Uses iterative search and evaluation to produce cited research reports.

Covers: England, Scotland, Wales, Northern Ireland, Ireland
"""

import datetime
import logging
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from .callbacks.citation_callbacks import (
    collect_education_sources_callback,
    format_education_citations_callback,
)
from .config import config


# --- Structured Output Models ---
class ResearchQuery(BaseModel):
    """A specific research query."""

    query: str = Field(description="Targeted search query for education research")
    focus_nations: list[str] | None = Field(
        default=None, description="Nations to focus on"
    )


class ResearchFeedback(BaseModel):
    """Evaluation feedback on research quality."""

    grade: str = Field(description="'pass' if sufficient, 'fail' if needs revision")
    comment: str = Field(description="Detailed evaluation explanation")
    follow_up_queries: list[ResearchQuery] | None = Field(
        default=None, description="Follow-up queries if grade is fail"
    )


# --- Loop Control ---
class ResearchEscalationChecker(BaseAgent):
    """Check if research evaluation passed and escalate to stop loop."""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event]:
        evaluation = ctx.session.state.get("research_evaluation")
        if evaluation and evaluation.get("grade") == "pass":
            logging.info(f"[{self.name}] Research passed. Stopping loop.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(f"[{self.name}] Research needs improvement. Continuing.")
            yield Event(author=self.name)


# --- Agent Definitions ---

# Research planner
education_research_planner = LlmAgent(
    model=config.model_name,
    name="education_research_planner",
    description="Plans education research across British Isles nations.",
    instruction=f"""
    You are an education research strategist specializing in British Isles education systems.

    Your job is to create a research plan for the given education topic. The plan should:

    1. Identify which nations are relevant (England, Scotland, Wales, Northern Ireland, Ireland)
    2. List 5-7 specific research questions or goals
    3. Consider comparative aspects across nations
    4. Note any bilingual/language considerations (Welsh, Irish, Gaelic)

    **CLASSIFICATION:**
    - `[RESEARCH]`: Information gathering tasks
    - `[COMPARISON]`: Cross-nation comparison tasks
    - `[DELIVERABLE]`: Synthesis and output tasks

    **KEY EDUCATION SOURCES:**
    - England: DfE, Ofsted, gov.uk education
    - Scotland: Scottish Government, Education Scotland, SQA
    - Wales: Welsh Government, Estyn, Qualifications Wales
    - Northern Ireland: NISRA, ETI, DE NI
    - Ireland: gov.ie, CSO, NCCA, Tusla

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Only use search if topic clarification is absolutely necessary.
    """,
    tools=[google_search],
    output_key="research_plan",
)

# Main researcher
education_researcher = LlmAgent(
    model=config.model_name,
    name="education_researcher",
    description="Executes education research plan with web search.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are an expert education researcher for British Isles education systems.

    Execute the research plan in `research_plan` state key.

    **PHASE 1: Research**
    For each `[RESEARCH]` or `[COMPARISON]` task:
    1. Generate 4-5 targeted search queries
    2. Execute ALL queries using google_search
    3. Focus on official government and education body sources
    4. Note differences between nations where relevant

    **PHASE 2: Synthesis**
    For each `[DELIVERABLE]` task:
    1. Use ONLY gathered research (no new searches)
    2. Create the specified output artifact
    3. Include cross-nation comparisons where relevant

    **IMPORTANT CONSIDERATIONS:**
    - Different qualification systems (GCSE, National 5, Junior Cert, etc.)
    - Different inspection bodies (Ofsted, Estyn, ETI, Education Scotland)
    - Bilingual education (Welsh-medium, Gaelscoil, GME)
    - Different curriculum frameworks
    - COVID-19 impacts varied by nation

    Output all research findings and deliverables clearly.
    """,
    tools=[google_search],
    output_key="research_findings",
    after_agent_callback=collect_education_sources_callback,
)

# Research evaluator
education_research_evaluator = LlmAgent(
    model=config.model_name,
    name="research_evaluator",
    description="Evaluates education research quality.",
    instruction=f"""
    You are a quality assurance analyst for education research.

    Evaluate the research in 'research_findings' state key.

    **EVALUATION CRITERIA:**
    1. Coverage of all relevant nations
    2. Use of authoritative sources (government, education bodies)
    3. Accuracy of cross-nation comparisons
    4. Depth of analysis
    5. Currency of information (recent data preferred)

    **SPECIFIC CHECKS:**
    - Are qualification equivalencies correctly stated?
    - Are inspection frameworks accurately described?
    - Are curriculum differences properly noted?
    - Is bilingual education addressed where relevant?

    If significant gaps exist, grade 'fail' and provide specific follow-up queries.
    If comprehensive, grade 'pass'.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Output must be JSON matching ResearchFeedback schema.
    """,
    output_schema=ResearchFeedback,
    output_key="research_evaluation",
)

# Follow-up researcher
follow_up_researcher = LlmAgent(
    model=config.model_name,
    name="follow_up_researcher",
    description="Executes follow-up research queries.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are executing follow-up research to address identified gaps.

    1. Review 'research_evaluation' for feedback and follow-up queries
    2. Execute EVERY follow-up query using google_search
    3. Synthesize new findings with existing 'research_findings'
    4. Output the complete, improved research findings
    """,
    tools=[google_search],
    output_key="research_findings",
    after_agent_callback=collect_education_sources_callback,
)

# Report composer
education_report_composer = LlmAgent(
    model=config.model_name,
    name="education_report_composer",
    include_contents="none",
    description="Composes final cited education research report.",
    instruction="""
    Transform research into a professional education report.

    **INPUT:**
    - Research Plan: `{research_plan}`
    - Research Findings: `{research_findings}`
    - Citation Sources: `{sources}`

    **REPORT STRUCTURE:**
    1. Executive Summary
    2. Introduction and Context
    3. Findings by Nation (where relevant)
    4. Cross-Nation Comparison
    5. Key Insights and Implications
    6. Conclusion

    **CITATION FORMAT:**
    Use `<cite source="src-ID" />` immediately after each claim.

    **STYLE:**
    - Professional academic tone
    - Clear headings and structure
    - Balanced coverage of all relevant nations
    - Note where data is unavailable or incomparable
    """,
    output_key="final_report",
    after_agent_callback=format_education_citations_callback,
)

# Full research pipeline
education_research_pipeline = SequentialAgent(
    name="education_research_pipeline",
    description="Complete education research pipeline with iteration.",
    sub_agents=[
        education_researcher,
        LoopAgent(
            name="research_refinement_loop",
            max_iterations=config.max_research_iterations,
            sub_agents=[
                education_research_evaluator,
                ResearchEscalationChecker(name="research_checker"),
                follow_up_researcher,
            ],
        ),
        education_report_composer,
    ],
)

# Main interactive agent
education_research_agent = LlmAgent(
    name="education_research_agent",
    model=config.model_name,
    description="Interactive education research assistant for British Isles.",
    instruction=f"""
    You are an education research assistant specializing in British Isles education systems.

    **YOUR WORKFLOW:**
    1. **Plan:** Use `education_research_planner` to create a research plan
    2. **Refine:** Incorporate user feedback on the plan
    3. **Execute:** When user approves, delegate to `education_research_pipeline`

    **COVERAGE:**
    - England, Scotland, Wales, Northern Ireland, Ireland
    - Crown Dependencies (Isle of Man, Jersey, Guernsey) when relevant

    **EXPERTISE AREAS:**
    - Education policy comparison
    - Curriculum frameworks
    - Qualification systems
    - School inspection regimes
    - Education statistics
    - Language-medium education (Welsh, Irish, Gaelic)

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Always clarify which nations the user wants to focus on.
    Never answer directly - always plan then execute.
    """,
    sub_agents=[education_research_pipeline],
    tools=[AgentTool(education_research_planner)],
    output_key="research_plan",
)


__all__ = [
    # Loop control
    "ResearchEscalationChecker",
    "ResearchFeedback",
    # Models
    "ResearchQuery",
    "education_report_composer",
    "education_research_agent",
    "education_research_evaluator",
    "education_research_pipeline",
    # Agents
    "education_research_planner",
    "education_researcher",
    "follow_up_researcher",
]
