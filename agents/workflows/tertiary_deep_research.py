"""tertiary_deep_research — ADK 2 Pillar 3 dynamic deep-research pipeline for tertiary.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors the uoa_portal_pipeline ADK SequentialAgent but as a Pillar-3
dynamic-workflow graph. The 4 UoG colleges + 18 schools + 1500 modules
drive the sub-question generation at runtime.

This replaces the old uoa_portal_pipeline with the ADK 2 dynamic-workflow
pattern (parallel_worker + recursive ctx.run_node + MAX_DEPTH).

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


MAX_DEPTH = 2  # recursion bound (per the L4b_recursion pattern)


decompose_agent = Agent(
    name="tertiary_decompose_agent", model="gemini-2.5-flash",
    output_schema=DecomposerOutput,
    instruction="""You are a research coordinator for UoG tertiary questions
(across 4 colleges + 18 schools + ~1500 modules). Break the user's
open-ended question into 3-7 specific, non-overlapping, independently-
researchable sub-questions spanning colleges + schools + modules + cross-
university topics.""",
)

research_agent = Agent(
    name="tertiary_research_agent", model="gemini-2.5-flash",
    output_schema=ResearchFinding,
    instruction="""You are a UoG tertiary research specialist. Given ONE specific
research question, produce a finding with a 2-3 sentence summary + 3-5
specific insights. Reference the canonical module_id (e.g. 'cs203_data_structures')
when the topic aligns with a module.""",
)

synthesize_agent = Agent(
    name="tertiary_synthesize_agent", model="gemini-2.5-flash",
    output_schema=DeepResearchBriefing,
    instruction="""You are the UoG tertiary synthesizer. Merge the findings into
one briefing: 1-sentence headline + 3-7 sections. Use snake_case module_ids
where applicable.""",
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
    yield Event(output=[{"question": q, "original_query": _extract_text(node_input), "_depth": 0} for q in plan.sub_questions])


RESEARCH_RETRY = RetryConfig(max_attempts=3, initial_delay=2.0, backoff_factor=2.0)


@node(parallel_worker=True, rerun_on_resume=True, retry_config=RESEARCH_RETRY)
async def research_topic(ctx, node_input):
    depth = node_input.get("_depth", 0)
    finding = _coerce(await ctx.run_node(research_agent, node_input=f"QUESTION: {node_input['question']}"), ResearchFinding)
    # Pillar 3 recursive depth (bounded by MAX_DEPTH per L4b)
    children = []
    if depth < MAX_DEPTH and finding.needs_deeper:
        for child_q in finding.child_questions[:3]:
            sub = _coerce(await ctx.run_node(
                research_agent, node_input=f"QUESTION: {child_q}"
            ), ResearchFinding)
            children.append({"question": child_q, "summary": sub.summary, "key_facts": sub.key_facts, "_depth": depth + 1})
    yield Event(output={
        "question": node_input["question"], "summary": finding.summary,
        "key_facts": finding.key_facts, "children": children, "_depth": depth,
    })


@node(rerun_on_resume=True)
async def synthesize(ctx, node_input):
    briefing = _coerce(await ctx.run_node(synthesize_agent, node_input=json.dumps(node_input, indent=2)), DeepResearchBriefing)
    yield Event(output={"briefing": briefing.model_dump(), "findings": node_input})


tertiary_deep_research = Workflow(
    name="tertiary_deep_research",
    description="Decompose → bounded-recursive parallel research across 4 colleges → synthesize → render assets.",
    edges=[(START, decompose, research_topic, synthesize, render_assets)],
)


async def run(query="What courses at UoG cover machine learning and which would suit a student with a CS background?"):
    print(f"=== tertiary_deep_research · Pillar 3 dynamic ===\n  QUERY: {query}\n")
    runner = Runner(node=tertiary_deep_research, app_name="tertiary_dr",
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
    asyncio.run(run(" ".join(sys.argv[1:]) or "What courses at UoG cover machine learning and which would suit a student with a CS background?"))
