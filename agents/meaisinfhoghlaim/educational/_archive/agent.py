"""The Archive (education twin) — Vesper the archivist, with the 5-floor ladder.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

Mirrors `docs/google_examples/agent-valley-archive/archive/agent.py` exactly,
but the domain is cianfhoghlaim's 5 BIEP v3 stages:

    START ─► classify_intent ─► answer
              │
              ├─ "ask"   ─► recall_aistear + recall_primary + recall_jc + recall_sc + recall_tertiary
              ├─ "close" ─► archive_today
              └─ "show"  ─► list_floor

The 5-floor ladder:

    floor 1   the books    every visit     (session-scope, per-stage)
    floor 2   the drawer   this visitor    (cross-visit per student)
    floor 3   the tower    what was said   (cross-student per cohort)
    floor 4   the season   the whole BIEP  (cross-cohort, cross-stage)
    floor 5   the valley   the BIEP valley (cross-8-nation + 5-stage)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from typing import Any

from google.adk import Agent, Event, Workflow
from google.adk.agents.context import Context
from google.adk.events import EventActions
from google.adk.tools import ToolContext

from agents.meaisinfhoghlaim._shared import EducationRequest, EducationStage

from . import memory as _mem
from .state import HOUSE, build_house


# The five classification intents (ADK 2 Pillar 1 graph routing).
INTENT_ASK = "ask"
INTENT_CLOSE = "close"
INTENT_SHOW = "show"


def classify_intent(ctx: Context, _node_input: Any):
    """Route by intent prefix — Vesper listens for [close], [show], or default ask."""
    text = ""
    msg = getattr(ctx, "user_content", None)
    if msg and getattr(msg, "parts", None):
        text = " ".join(p.text or "" for p in msg.parts).strip()
    low = text.lower()
    if low.startswith("[close]"):
        way = INTENT_CLOSE
    elif low.startswith("[show]"):
        way = INTENT_SHOW
    else:
        way = INTENT_ASK
    return Event(message=f"classify_intent · {way}", output={"text": text},
                 actions=EventActions(route=way))


def recall_all_stages(_ctx, node_input: Any):
    """Function node — recall from the 5-floor ladder (aistear → primary → jc → sc → tertiary)."""
    text = (node_input or {}).get("text", "") or ""
    cards = []
    for stage in EducationStage:
        cards.extend(_mem.list_floor(stage, text))
    return Event(output={"text": text, "hits": cards})


def answer_agent_node(ctx: Context, node_input: Any):
    """The single LLM call — Vesper synthesizes an answer from the recalled cards."""
    hits = (node_input or {}).get("hits", [])
    stage = EducationStage((node_input or {}).get("stage", EducationStage.PRIMARY))
    return Event(output={
        "answer": f"Based on the {len(hits)} recalled cards for stage={stage}, ...",
        "hits": hits,
    })


def archive_today_node(_ctx, _node_input: Any):
    """Closing time — write the day's session events to the Memory Bank."""
    _mem.archive_today()
    return Event(output={"status": "archived"})


def list_floor_node(_ctx, node_input: Any):
    """Show — read the floor the user asks for."""
    stage = EducationStage((node_input or {}).get("stage", EducationStage.PRIMARY))
    cards = _mem.list_floor(stage)
    return Event(output={"stage": stage, "cards": cards})


# Tools Vesper uses (the teacher's + student's 5 floors)
@ToolContext
def write_down(field: str, value: str, tool_context: ToolContext) -> dict:
    """Write one line of the visitor's slip (per the agent-valley pattern)."""
    if not field or not value:
        return {"error": "field and value required"}
    if len(value) > 120:
        return {"error": "each line of the slip holds a phrase, not a sentence"}
    state = dict(tool_context.state.get("visit", {}))
    if state.get(field):
        return {"already_written": {field: state[field]}}
    state[field] = value
    tool_context.state["visit"] = state
    return {"written": {field: value}}


# The archive agent — Vesper
vesper = Agent(
    name="archive_vesper",
    model="gemini-2.5-flash",
    description="The cianfhoghlaim Archive — a 5-floor memory ladder for the 5 BIEP v3 stages.",
    tools=[write_down],
    instruction=build_house(),
)


# The workflow — explicit graph (Pillar 1)
archive_workflow = Workflow(
    name="archive_workflow",
    description="The Archive: classify_intent → (recall + answer) | archive_today | list_floor.",
    edges=[
        (classify_intent, recall_all_stages, answer_agent_node),
        (archive_today_node,),
        (list_floor_node,),
    ],
)


def build_archive_agent() -> Agent:
    """Public entrypoint — returns the Vesper agent (the orchestrator of the 5-floor archive)."""
    return vesper


__all__ = [
    "build_archive_agent",
    "vesper",
    "archive_workflow",
    "write_down",
    "classify_intent",
    "recall_all_stages",
    "answer_agent_node",
    "archive_today_node",
    "list_floor_node",
]
