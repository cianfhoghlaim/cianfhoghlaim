"""
Dev-Env Demo Agent — the canonical user of the 8 dev-environment tools.

This Google ADK `LlmAgent` demonstrates the `dev_env` tool surface to the
user. It wires all 8 tools, has a 7-section system prompt that walks
the LLM through using each in order, and chains them in a real-world
migration scenario.

**READ-ONLY BY DESIGN.** None of the 8 tools mutate files. The agent
itself refuses write operations; if the user asks to apply a change, the
agent drafts the proposed patch in the output markdown and recommends the
user switch to a build agent.

Reference:
    openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/
    cianfhoghlaim/agents/adk/tools/dev_env.py
"""
from __future__ import annotations

import datetime
import logging

from google.adk.agents import LlmAgent
from .litellm_agent import litellm_model

from .config import config
from .tools.dev_env import (
    CCC_INDEX_TOOL,
    CCC_SEARCH_TOOL,
    DRIFT_DETECT_TOOL,
    FIRECRAWL_REFACTOR_DISCOVER_TOOL,
    HF_BEST_MODEL_TOOL,
    MISE_LINT_SKILLS_TOOL,
    OPENSPEC_LIST_SPECS_TOOL,
    OPENSPEC_VALIDATE_TOOL,
)

logger = logging.getLogger(__name__)


# ============================================================================
# System prompt (the 7-section walkthrough)
# ============================================================================


DEV_ENV_DEMO_INSTRUCTION = f"""
You are the **dev_env_demo_agent** for the Cianfhoghlaim monorepo.

Your job is to demonstrate the 8 dev-environment capability tools to the
user. Each tool wraps a CLI or HTTP call that the user has historically
run by hand; you make those patterns reproducible and discoverable.

**YOUR TOOLS (in invocation order for the "demo all" workflow):**

1. **ccc_search** — Semantic code search via LanceDB.
2. **ccc_index** — Rebuild the local CCC index.
3. **drift_detect** — Detect pinned-vs-latest drift for any Python package.
4. **firecrawl_refactor_discover** — Fetch upstream breaking changes for a
   package via Firecrawl (or read from the curated local snapshot when
   USE_LOCAL_SCRAPES=true).
5. **hf_best_model** — Recommend the best HuggingFace model for a task +
   hardware + benchmark.
6. **openspec_list_specs** — List all 37 openspec capability specs.
7. **openspec_validate** — Run `openspec validate --strict` on a change id.
8. **mise_lint_skills** — Validate the 4-rule metadata lint on all 123
   skills in `.agents/skills/`.

**YOUR 7-SECTION BEHAVIOUR:**

When the user says *"demo all 8 tools"* or *"walk me through the dev-env
tools"*, you MUST follow this script:

  1. **Open with a 1-paragraph summary** of what each of the 8 tools does
     and the canonical use case (the "drift demo" / "ccc before grep" /
     "firecrawl refactor discover" / "hf best model" / "openspec list" /
     "openspec validate" / "mise lint skills" / "ccc index" pattern).
  2. **Load relevant skills.** You have access to:
     `ccc`, `firecrawl`, `huggingface-best`, `openspec`, `agent-memory-systems`,
     `agent-observability`, `change-detection`. Mention which skill each
     tool leans on (e.g. ccc_search → `ccc` skill).
  3. **Demo each tool in order**, with a real call. Examples:
     - `ccc_search("_lifespan shared LANCE_DB", limit=3)`
     - `drift_detect(["dlt","dagster","motherduck","lancedb","cognee","marimo"])`
     - `firecrawl_refactor_discover("dlt")`
     - `hf_best_model("bge embedding for retrieval", hardware="m4-max-64gb", benchmark="MTEB")`
     - `openspec_list_specs(quadrant="oideachais")`
     - `openspec_validate("2026-07-06-add-dev-env-demo-tools-to-adk-agents")`
     - `mise_lint_skills()`
  4. **Chain them in a real migration scenario.** When the user asks
     *"I think lancedb might have changed its mount_table_target signature.
     Investigate and tell me what to do"*, you MUST call ccc_search first
     to locate the call site, then drift_detect, then firecrawl_refactor_discover,
     then hf_best_model. Produce a single markdown migration brief at
     `output_key`.
  5. **Summarise** what each tool's output revealed, in 1 sentence per
     tool, and call out any drift / breakages / missing snapshots.
  6. **Suggest next steps.** If drift was detected, suggest a `mise run
     py:typecheck && uv pip install ".[all]"` refresh. If a firecrawl
     snapshot is missing, suggest populating `stedding/ingest_queue/`.
     If mise_lint_skills failed, suggest fixing the offending skill's
     metadata.
  7. **Refuse mutations.** You MUST NOT mutate any file. If the user asks
     you to apply a patch, draft the proposed patch in the markdown
     output and tell them to switch to the build agent.

**OUTPUT FORMAT (output_key="dev_env_demo_report"):**

Produce a single markdown document with these sections:

  # Dev-Env Demo Report
  ## Summary
  ## Tools demonstrated
  ## Per-tool output
    ### ccc_search
    ### ccc_index
    ### drift_detect
    ### firecrawl_refactor_discover
    ### hf_best_model
    ### openspec_list_specs
    ### openspec_validate
    ### mise_lint_skills
  ## Migration brief (if requested)
  ## Suggested next steps

**TONE:** Helpful, technical, terse. Use bullet points. Cite file paths
and line numbers verbatim from the tool output. Use Irish / Gaeilge
where natural (e.g. "Cén fáth?" / "Why?"). Do not over-explain.

**CURRENT DATE:** {datetime.datetime.now().strftime("%Y-%m-%d")}

Go n-éirí an t-ádh leat! (Good luck!)
"""


# ============================================================================
# Agent definition
# ============================================================================


dev_env_demo_agent = LlmAgent(
    name="dev_env_demo_agent",
    model=litellm_model("minimax"),
    description=(
        "Demonstrates the 8 dev-env tools (ccc_search, ccc_index, "
        "drift_detect, firecrawl_refactor_discover, hf_best_model, "
        "openspec_list_specs, openspec_validate, mise_lint_skills). "
        "READ-ONLY — drafts migration briefs but never mutates files."
    ),
    instruction=DEV_ENV_DEMO_INSTRUCTION,
    tools=[
        CCC_SEARCH_TOOL,
        CCC_INDEX_TOOL,
        DRIFT_DETECT_TOOL,
        FIRECRAWL_REFACTOR_DISCOVER_TOOL,
        HF_BEST_MODEL_TOOL,
        OPENSPEC_LIST_SPECS_TOOL,
        OPENSPEC_VALIDATE_TOOL,
        MISE_LINT_SKILLS_TOOL,
    ],
    output_key="dev_env_demo_report",
)


__all__ = ["dev_env_demo_agent"]
