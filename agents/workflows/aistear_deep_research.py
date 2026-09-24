"""aistear_deep_research — ADK 2 Pillar 3 dynamic deep-research pipeline for Aistear.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors the L4a_flat_research pattern from docs/google_examples/adk2-tutorial:

    START ─► decompose ─► research_topic (parallel_worker, 4 Aistear themes)
                                 │  │  │  │
                                 └──┴──┴──┴─ (flat: no recursion)
                                              ▼
                                        synthesize

The fan-out width is runtime-chosen (3-7), bounded by the schema.
This level is FLAT — no recursion (that's L4b's pattern, which we apply
to the JC + LC deep-research pipelines instead).

The 4 canonical Aistear themes:
- Well-being (Biú Folláine)
- Identity-Belonging (Céannacht agus Muintearas)
- Communicating (Cumarsáid)
- Exploring-Thinking (Taiscéalaíocht agus Smaointeoireacht)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import asyncio
import json
import logging

from google.adk import Agent, Event, Runner, Workflow
from google.adk.workflow import RetryConfig, START, node
from google.adk.sessions import InMemorySessionService
from google.genai import types as gtypes

from agents.meaisinfhoghlaim._shared import (
    DeepResearchBriefing,
    DecomposerOutput,
    ResearchFinding,
)

logger = logging.getLogger(__name__)


# The 4 canonical Aistear themes (per baml_src/.../stages/aistear.baml)
AISTEAR_THEMES = [
    "Well-being (Biú Folláine)",
    "Identity-Belonging (Céannacht agus Muintearas)",
    "Communicating (Cumarsáid)",
    "Exploring-Thinking (Taiscéalaíocht agus Smaointeoireacht)",
]


MODEL = "gemini-2.5-flash"


# Three single-turn agents: decompose + research + synthesize.
decompose_agent = Agent(
    name="aistear_decompose_agent", model=MODEL,
    output_schema=DecomposerOutput,
    instruction=f"""You are a research coordinator for Aistear (Early Childhood,
ages 0-6) questions. Break the user's open-ended question into 3-7 specific,
non-overlapping, independently-researchable sub-questions across these 4
canonical themes:
{chr(10).join('  - ' + t for t in AISTEAR_THEMES)}
Make sure the questions span the themes proportionally.""",
)

research_agent = Agent(
    name="aistear_research_agent", model=MODEL,
    output_schema=ResearchFinding,
    instruction="""You are an Aistear research specialist. Given ONE specific
research question, produce a finding: a 2-3 sentence summary and 3-5 specific
insights. (For this level, keep needs_deeper=False.)""",
)

synthesize_agent = Agent(
    name="aistear_synthesize_agent", model=MODEL,
    output_schema=DeepResearchBriefing,
    instruction="""You are the Aistear research synthesizer. Merge the findings
into one briefing: a 1-sentence headline + 3-7 sections, one per sub-question.
Use Irish-appropriate language (aistear, luath-óige, céim).""",
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
    user_query = _extract_text(node_input)
    plan = _coerce(await ctx.run_node(decompose_agent, node_input=user_query), DecomposerOutput)
    print(f"  [aistear_decompose] {len(plan.sub_questions)} sub-questions")
    for q in plan.sub_questions:
        print(f"    • {q[:80]}")
    yield Event(output=[{"question": q, "original_query": user_query} for q in plan.sub_questions])


# parallel_worker — the ADK 2 dynamic-workflow primitive (Pillar 3)
RESEARCH_RETRY = RetryConfig(max_attempts=3, initial_delay=2.0, backoff_factor=2.0)


@node(parallel_worker=True, rerun_on_resume=True, retry_config=RESEARCH_RETRY)
async def research_topic(ctx, node_input):
    question = node_input["question"]
    finding = _coerce(await ctx.run_node(
        research_agent,
        node_input=f"QUESTION: {question}",
    ), ResearchFinding)
    yield Event(output={"question": question, "summary": finding.summary, "key_facts": finding.key_facts})


@node(rerun_on_resume=True)
async def synthesize(ctx, node_input):
    briefing = _coerce(await ctx.run_node(
        synthesize_agent, node_input=json.dumps(node_input, indent=2)
    ), DeepResearchBriefing)
    yield Event(output={"briefing": briefing.model_dump(), "findings": node_input})


aistear_deep_research = Workflow(
    name="aistear_deep_research",
    description="Decompose → flat parallel research across 4 Aistear themes → synthesize.",
    edges=[(START, decompose, research_topic, synthesize)],
)


# Harness
async def run(query="How do the 4 Aistear themes support early childhood wellbeing?"):
    print(f"=== aistear_deep_research · Pillar 3 dynamic ===\n  QUERY: {query}\n")
    runner = Runner(node=aistear_deep_research, app_name="aistear_dr",
                    session_service=InMemorySessionService(), auto_create_session=True)
    t0 = asyncio.get_event_loop().time()
    final = None
    async for event in runner.run_async(
        user_id="u1", session_id="s1",
        new_message=gtypes.Content(role="user", parts=[gtypes.Part(text=query)]),
    ):
        out = getattr(event, "output", None)
        if isinstance(out, dict) and "briefing" in out:
            final = out
    if final:
        b = final["briefing"]
        print(f"\n  {len(final['findings'])} sub-questions researched in parallel")
        print(f"\n📋 {b['headline']}")
        for i, s in enumerate(b["sections"], 1):
            print(f"  {i}. {s[:160]}")


if __name__ == "__main__":
    import sys
    asyncio.run(run(" ".join(sys.argv[1:]) or "How do the 4 Aistear themes support early childhood wellbeing?"))
