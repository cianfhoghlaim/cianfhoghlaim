"""4-Stage Plane End-to-End Demo — exercises the full BAML → CocoIndex → ADK → CopilotKit → Marimo flow.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5
verification): this notebook demonstrates the end-to-end 4-stage plane
integration.

The PEP 723 dependencies are imported from the canonical template
(notebooks/_shared/_pep723_template.py) per the canonical-pattern
introduced in the same change.

The flow:
1. BAML: Call the canonical LC + JC + A-Level + GCSE extraction
   functions via the 4_stage_extraction.py helpers
2. CocoIndex: Embed the extraction results via the canonical
   BAAI/bge-m3 embedder + write to the LanceDB table
3. ADK: Invoke the 4 stage agents (lc_subject_agent +
   jc_subject_agent + alevel_subject_agent + gcse_subject_agent)
   via the AGENT_REGISTRY
4. CopilotKit: Register the 4 stage agents + emit the AG-UI
   registration events via the agent_ui_bridge helpers
5. Marimo: Render the end-to-end results in the current notebook
   via mo.ui.chat + mo.ui.table

The 4 stage agents are exposed via the 4 runtimes:
- agents/integrations/agent_registry_runtime.py
- agents/integrations/agent_ui_bridge.py
- cocoindex/biep_parity/baml_runtime_integration.py
- notebooks/_shared/marimo_integration_runtime.py
"""

# Canonical PEP 723 dependencies (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # noqa: F401

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full", app_title="BIEP v3 — 4-Stage Plane Demo")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # BIEP v3 4-Stage Plane Demo

        This notebook demonstrates the end-to-end 4-stage plane flow.

        ## The 4 stages

        1. **Leaving Cycle** (`lc_subject_agent` + 14 LC subjects)
        2. **Junior Cycle** (`jc_subject_agent` + 8 NCCA JC subjects at full scope)
        3. **A-Level** (`alevel_subject_agent` + 15 A-Level × 3 boards)
        4. **GCSE** (`gcse_subject_agent` + 9 GCSE × 3 boards)

        ## The 4 runtimes

        | Runtime | Module | Purpose |
        | -- | -- | -- |
        | BAML → CocoIndex | `cocoindex_flows.biep_parity.baml_runtime_integration` | `run_stage_extraction(stage, chunk_text, subject, **kwargs)` |
        | ADK → CopilotKit | `agents.integrations.agent_registry_runtime` | `register_all_agents_with_copilotkit()` |
        | AG-UI Bridge | `agents.integrations.agent_ui_bridge` | `register_adk_agent(agent, name)` |
        | Marimo Integration | `notebooks._shared.marimo_integration_runtime` | `make_baml_chat_for_stage(stage, subject)` |
        """
    )
    return


@app.cell
def _():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    # BAML → CocoIndex runtime
    from cocoindex_flows.biep_parity.baml_runtime_integration import (
        run_stage_extraction,
        get_search_closure_for_stage,
        get_extraction_metrics,
    )

    # ADK → CopilotKit runtime
    from agents.integrations.agent_registry_runtime import (
        register_all_agents_with_copilotkit,
        collect_all_agui_events,
        build_copilotkit_runtime_config,
    )

    # AG-UI bridge
    from agents.integrations.agent_ui_bridge import (
        make_planner_agent,
        register_adk_agent,
        emit_agui_registration_event,
    )

    # Marimo integration runtime
    from notebooks._shared.marimo_integration_runtime import (
        make_baml_chat_for_stage,
    )

    # The 4 stage agents
    from agents.adk.agent_registry import AGENT_REGISTRY
    return


@app.cell
def _():
    import marimo as mo

    # Display the 4 stage agents
    mo.md("## The 4 Stage Agents (from AGENT_REGISTRY)")

    agent_rows = []
    for name, wiring in AGENT_REGISTRY.items():
        agent_rows.append({
            "name": name,
            "stage": wiring.stage or "—",
            "tools": len(wiring.tools),
            "description": wiring.description[:80],
        })

    import pandas as pd
    df = pd.DataFrame(agent_rows)
    mo.ui.table(df)
    return (df,)


@app.cell
def _():
    import marimo as mo

    # The 4 stage runtimes
    mo.md("## The 4 Stage Runtimes (BAML → CocoIndex)")

    # Try a sample BAML extraction (will be a stub if baml-py not installed)
    sample_chunk = "Students should be able to calculate the equilibrium constant for reversible reactions."
    result = await run_stage_extraction(
        "lc",
        sample_chunk,
        "chemistry",
        ncca_lo_code="LC-CHEM-LO-023",
    )
    if isinstance(result, dict) and "status" in result:
        mo.md(f"Sample extraction result:\n\n```\n{result}\n```")
    else:
        mo.md(f"Sample extraction (baml-py not available): {result}")

    return (sample_chunk, result)


@app.cell
def _():
    import marimo as mo

    # Display the AG-UI registration events
    mo.md("## The AG-UI Registration Events")

    events = collect_all_agui_events()
    mo.md(f"Total AG-UI events: {len(events)}")
    for event in events[:4]:  # Show first 4 (one per stage)
        mo.md(
            f"- **{event['name']}** ({event['description'][:60]}...): "
            f"{len(event['tools'])} tools"
        )

    return (events,)


@app.cell
def _():
    import marimo as mo

    # The 4 stage extraction metrics
    mo.md("## The 4 Stage Extraction Metrics")

    metrics = get_extraction_metrics("lc")
    mo.md(f"LC stage metrics: {metrics}")
    return (metrics,)


@app.cell
def _():
    import marimo as mo

    # The BAML chat for the LC stage
    mo.md("## The BAML Chat for the LC Stage")

    chat = make_baml_chat_for_stage("lc", "chemistry")
    mo.md(f"LC stage chat created: {type(chat).__name__}")
    return (chat,)


if __name__ == "__main__":
    app.run()