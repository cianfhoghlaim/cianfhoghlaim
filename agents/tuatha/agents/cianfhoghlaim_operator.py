"""cianfhoghlaim operator agent — the repo self-reference ADK agent.

The 9th of 9 ADK agents. The 8 NCCA subject specialists (math / appm /
chem / geog / hist / engl / gael / comp) handle the Leaving Certificate
content. The cianfhoghlaim operator handles questions about the
repo itself — how the dlt/ + cocoindex/ + baml_src/ + meaisinfhoghlaim/
+ apps/web/ + apps/api/ pipeline works.

This is the agentic tutorial for the repo itself: when a developer
runs `bun run dev` and asks the operator "how does the BAML extraction
work?", the operator can read the BAML files + the dlt sources + the
CocoIndex embeddings and explain the architecture.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

# Try to use the Google ADK LlmAgent + the LiteLLM gateway
try:
    from google.adk.agents import LlmAgent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    LlmAgent = None


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _list_subjects() -> dict[str, Any]:
    """List the 8 NCCA subjects + their agent + cocoindex path + baml path."""
    subjects = []
    for baml_file in sorted((REPO_ROOT / "baml_src" / "education" / "subjects").glob("qpack_*.baml")):
        slug = baml_file.stem.replace("qpack_", "")
        subjects.append({
            "subject": slug,
            "baml": str(baml_file.relative_to(REPO_ROOT)),
            "agent": f"agents/tuatha/agents/{slug.replace('applied_mathematics', 'appm')}_agent.py",
            "cocoindex": f"cocoindex_flows/{slug}_embedding.py",
        })
    return {"subjects": subjects, "count": len(subjects)}


def _list_agents() -> dict[str, Any]:
    """List the 9 ADK agents (8 NCCA + 1 operator)."""
    agents = []
    for agent_file in sorted((REPO_ROOT / "agents" / "tuatha" / "agents").glob("*_agent.py")):
        if agent_file.name == "__init__.py":
            continue
        slug = agent_file.stem.replace("_agent", "")
        agents.append({"agent": slug, "file": str(agent_file.relative_to(REPO_ROOT))})
    agents.append({
        "agent": "cianfhoghlaim",
        "file": "agents/tuatha/agents/cianfhoghlaim_operator.py",
        "role": "repo self-reference",
    })
    return {"agents": agents, "count": len(agents)}


def _list_foundations() -> dict[str, Any]:
    """List the 5 NCCA root-level PDFs in leaving_certificate/."""
    foundations = []
    pdfs = [
        "key-competencies-in-senior-cycle_en.pdf",
        "SC-L1-L2-Programme-Statement.pdf",
        "scr-advisory-report_en.pdf",
        "the-potential-of-online-learning-environments_en.pdf",
        "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    ]
    for pdf in pdfs:
        foundations.append({"name": pdf, "category": pdf.split("-")[0]})
    return {"foundations": foundations, "count": len(foundations)}


def _show_dlt_pipeline(topic: str) -> dict[str, Any]:
    """Show the DLT pipeline for a topic."""
    return {
        "topic": topic,
        "dlt_source": "dlt/british_isles/ireland/ncca_root_pdfs.py",
        "flow": "DLT source reads NCCA PDFs → extracts per-PDF JSON rows → writes to MotherDuck (LanceDB + DuckLake)",
    }


def _show_cocoindex_index(topic: str) -> dict[str, Any]:
    """Show the CocoIndex v1 app for a topic."""
    return {
        "topic": topic,
        "cocoindex_path": f"cocoindex/{topic}_embedding.py",
        "flow": "CocoIndex v1 reads the extracted content → embeds via BGE-M3 (1024-dim) → writes to LanceDB `oideachais.lc.<subject>.*`",
    }


def _show_baml_schema(name: str) -> dict[str, Any]:
    """Show the BAML schema for a function."""
    return {
        "name": name,
        "baml_source": f"baml_src/education/subjects/qpack_{name}.baml",
        "schemas": [
            "GenerateFormativeItem",
            "ScoreFormativeResponse",
            "ExtractLeavingCertSyllabus",
        ],
    }


def _list_eiraic_treasures() -> dict[str, Any]:
    """List the 13 éraic treasures (the 13-tier mastery progression)."""
    return {
        "count": 13,
        "baml": "baml_src/education/_shared/eiraic_treasures.baml",
    }


# The 7 tools available to the cianfhoghlaim operator agent
TOOLS = [
    _list_subjects,
    _list_agents,
    _list_foundations,
    _show_dlt_pipeline,
    _show_cocoindex_index,
    _show_baml_schema,
    _list_eiraic_treasures,
]


def build_system_prompt() -> str:
    """Build the system prompt for the cianfhoghlaim operator agent."""
    return """You are the cianfhoghlaim operator agent — the repo self-reference.

The cianfhoghlaim platform is a self-hostable consolidation of Leaving
Certificate education system resources. Anyone can `git clone` and run
their own instance.

Your job is to explain how the repo works. You have access to:
- The README at the repo root
- The dlt/ extraction sources
- The cocoindex/ v1 embedding apps
- The baml_src/ typed extraction schemas
- The meaisinfhoghlaim/ OCR/VLM registry (24 entries)
- The apps/web/ TanStack Start + CopilotKit v2 + Convex
- The apps/api/ Hono + oRPC + CopilotKit AG-UI runtime
- The 8 NCCA subject ADK specialists + the 1 cianfhoghlaim operator

When a developer asks "how does the X pipeline work?", answer with:
1. The entry point (file path)
2. The flow (what calls what)
3. The output (what gets written where)
4. The next pipeline step

The 9 ADK agents are:
  math, appm, chem, geog, hist, engl, gael, comp, cianfhoghlaim (operator)

The 8 NCCA subjects + the 5 NCCA root-level PDFs + the 5 NCCA Key
Competencies are the core content. The 13 éraic tier system is the
mastery progression.

Answer concisely + reference actual file paths + actual BAML function
names. The user is a developer who wants to understand the repo."""


if ADK_AVAILABLE:
    cianfhoghlaim_operator = LlmAgent(
        name="cianfhoghlaim_operator",
        model="minimax-m3",
        instruction=build_system_prompt(),
        tools=TOOLS,
    )
else:
    cianfhoghlaim_operator = None


__all__ = [
    "cianfhoghlaim_operator",
    "TOOLS",
    "build_system_prompt",
    "_list_subjects",
    "_list_agents",
    "_list_foundations",
    "_show_dlt_pipeline",
    "_show_cocoindex_index",
    "_show_baml_schema",
    "_list_eiraic_treasures",
]