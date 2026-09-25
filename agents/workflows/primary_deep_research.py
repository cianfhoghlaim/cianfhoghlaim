"""primary_deep_research — ADK 2 Pillar 3 dynamic deep-research pipeline for Primary (ages 4-12).

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors aistear_deep_research. The 12 canonical NCCA primary curriculum
areas drive the sub-question generation:

    START ─► decompose ─► research_topic (parallel_worker, primary areas)
                                 │  │  │
                                 └──┴──┴─ (flat: no recursion)
                                          ▼
                                       synthesize

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import asyncio
import json
import sys

from google.adk import Agent, Event, Runner, Workflow
from ._render_assets_node import render_assets
from google.adk.workflow import RetryConfig, START, node
from google.adk.sessions import InMemorySessionService
from google.genai import types as gtypes

from agents.meaisinfhoghlaim._shared import (
    DeepResearchBriefing,
    DecomposerOutput,
    ResearchFinding,
)


# The 12 canonical NCCA primary curriculum areas (per dlt_sources/.../primary.py)
PRIMARY_AREAS = [
    "Primary Language (English)", "Primary Language (Irish) / Gaeilge",
    "Primary Mathematics", "SESE Science", "SESE History", "SESE Geography",
    "Visual Arts", "Music", "Drama", "Physical Education",
    "SPHE (Social Personal and Health Education)", "Religion",
]


MODEL = "gemini-2.5-flash"


decompose_agent = Agent(
    name="primary_decompose_agent", model=MODEL,
    output_schema=DecomposerOutput,
    instruction=f"""You are a research coordinator for NCCA Primary Curriculum
(ages 4-12) questions. Break the user's open-ended question into 3-7
specific, non-overlapping, independently-researchable sub-questions across
these 12 canonical curriculum areas:
{chr(10).join('  - ' + a for a in PRIMARY_AREAS)}
Make sure the questions span the areas proportionally.""",
)

research_agent = Agent(
    name="primary_research_agent", model=MODEL,
    output_schema=ResearchFinding,
    instruction="""You are an NCCA Primary Curriculum research specialist. Given
ONE specific research question, produce a finding: a 2-3 sentence summary
and 3-5 specific insights.""",
)

synthesize_agent = Agent(
    name="primary_synthesize_agent", model=MODEL,
    output_schema=DeepResearchBriefing,
    instruction="""You are the NCCA Primary Curriculum synthesizer. Merge the findings
into one briefing: a 1-sentence headline + 3-7 sections, one per sub-question.""",
)


def _coerce(payload, schema_cls):
    if hasattr(payload, "model_dump_json"):
        return schema_cls.model_validate_json(payload.model_dump_json())
    if isinstance(payload, schema_cls):
        return payload
    if isinstance(payload, dict):
        return schema_cls.model_validate(payload)
    if isinstance(payload, str):
        return schema_cls.model_validate_json(payload)
    raise ValueError(f"Cannot coerce {type(payload).__name__} into {schema_cls.__name__}")


def _extract_text(node_input):
    if isinstance(node_input, str):
        return node_input
    if hasattr(node_input, "parts") and node_input.parts:
        return getattr(node_input.parts[0], "text", None) or str(node_input)
    return str(node_input)


@node(rerun_on_resume=True)
async def decompose(ctx, node_input):
    plan = _coerce(await ctx.run_node(decompose_agent, node_input=_extract_text(node_input)), DecomposerOutput)
    print(f"  [primary_decompose] {len(plan.sub_questions)} sub-questions")
    yield Event(output=[{"question": q, "original_query": _extract_text(node_input)} for q in plan.sub_questions])


RESEARCH_RETRY = RetryConfig(max_attempts=3, initial_delay=2.0, backoff_factor=2.0)


@node(parallel_worker=True, rerun_on_resume=True, retry_config=RESEARCH_RETRY)
async def research_topic(ctx, node_input):
    finding = _coerce(await ctx.run_node(
        research_agent, node_input=f"QUESTION: {node_input['question']}"
    ), ResearchFinding)
    yield Event(output={"question": node_input["question"], "summary": finding.summary, "key_facts": finding.key_facts})


@node(rerun_on_resume=True)
async def synthesize(ctx, node_input):
    briefing = _coerce(await ctx.run_node(synthesize_agent, node_input=json.dumps(node_input, indent=2)), DeepResearchBriefing)
    yield Event(output={"briefing": briefing.model_dump(), "findings": node_input})


primary_deep_research = Workflow(
    name="primary_deep_research",
    description="Decompose → flat parallel research across 12 primary areas → synthesize → render assets.",
    edges=[(START, decompose, research_topic, synthesize, render_assets)],
)


async def run(query="How can I integrate cross-curricular primary projects across the 12 NCCA areas?"):
    print(f"=== primary_deep_research · Pillar 3 dynamic ===\n  QUERY: {query}\n")
    runner = Runner(node=primary_deep_research, app_name="primary_dr",
                    session_service=InMemorySessionService(), auto_create_session=True)
    final = None
    async for event in runner.run_async(
        user_id="u1", session_id="s1",
        new_message=gtypes.Content(role="user", parts=[gtypes.Part(text=query)]),
    ):
        out = getattr(event, "output", None)
        if isinstance(out, dict) and "briefing" in out:
            final = out
    if final:
        print(f"\n📋 {final['briefing']['headline']}")


if __name__ == "__main__":
    asyncio.run(run(" ".join(sys.argv[1:]) or "How can I integrate cross-curricular primary projects across the 12 NCCA areas?"))
