# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Academic History Chat — academic-history notebook #08.

A marimo prototype of the academic-history chat experience. The
notebook exercises the 10 tools in `academic_history_agent` against
the user's manifest + artefacts and produces a structured
`AcademicHistorySnapshot`-style summary.

Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Panels:
- A: the user's modules (from `list_my_modules`)
- B: the user's artefacts (from `list_my_artifacts`)
- C: top revision recommendations (from `recommend_next_revision`)
- D: progress summary (from `summarise_my_progress`)
- E: engine health banner

The notebook is a static prototype: it does not call any LLM. It
exercises the 10 academic-history-agent tools and renders their
output. In production, the same tools would be wired through
`EnhancedOrchestrator.process_with_events()` (the AG-UI SSE stream).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import marimo

__generated_with_marimo__ = "0.23.13"

app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import (
        acad_engine_label,
        acad_health_md,
        load_manifest_or_default,
        pseudo_id,
    )
    return acad_engine_label, acad_health_md, load_manifest_or_default, mo, pseudo_id


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Academic History Chat (prototype)

        The 8th of 8 notebooks in `notebooks/14_academic_history/`.

        A marimo prototype that exercises the 10 tools in
        `academic_history_agent` and renders a structured
        `AcademicHistorySnapshot`-style summary.
        """
    )
    return


@app.cell
def _panels(acad_engine_label, acad_health_md, mo, pseudo_id):
    """Exercise the agent tools and render the panels."""
    try:
        from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (  # type: ignore[import-not-found]
            list_tools,
            run_tool,
            academic_history_agent_wire,
        )
        agent_available = True
    except Exception as exc:  # noqa: BLE001
        agent_available = False
        agent_err = str(exc)

    if not agent_available:
        mo.md(f"> **agent unavailable**: {agent_err}")
    else:
        modules = run_tool("list_my_modules")
        a_md = mo.md(
            "### Panel A — modules\n\n"
            + "\n".join(
                f"- `{m['module_code']}` — {m['module_title']} → `{m['resolved_path']}`"
                for m in modules
            )
        )

        artefacts = run_tool("list_my_artifacts", limit=20)
        b_md = mo.md(
            "### Panel B — artefacts (top 20)\n\n"
            + "\n".join(
                f"- `{a['module_code']}` / `{a['file_name']}` ({a['size_bytes']:,} B)"
                for a in artefacts
            )
        )

        recs = run_tool("recommend_next_revision", top_n=3)
        c_md = mo.md(
            "### Panel C — revision recommendations\n\n"
            + "\n".join(
                f"- `{r['module_code']}` — {r['rationale']}" for r in recs
            )
        )

        summary = run_tool("summarise_my_progress")
        d_md = mo.md(
            "### Panel D — progress summary\n\n```json\n"
            + json.dumps(summary, indent=2)
            + "\n```"
        )

        health_md = mo.md(
            acad_health_md(
                acad_engine_label(),
                "offline fallback (synthetic)",
                len(artefacts),
            )
        )

        mo.vstack([a_md, b_md, c_md, d_md, health_md])
    return


@app.cell
def _tool_list(mo):
    try:
        from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (  # type: ignore[import-not-found]
            list_tools,
            academic_history_agent_wire,
        )
        tools = list_tools()
        wire_kind = academic_history_agent_wire.memory_backend_kind
    except Exception:  # noqa: BLE001
        tools = []
        wire_kind = "unavailable"
    mo.md(
        f"### Tools ({len(tools)}) — wire.memory_backend_kind = `{wire_kind}`\n\n"
        + "\n".join(f"- `{t['name']}` — {t['description']}" for t in tools)
    )
    return


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📊 This notebook backs the
        `oideachais-academic-history-pipeline` spec R5 + the
        `agent-memory-systems` spec R13.
        See `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.
        """
    )
    return


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="08_academic_history_chat",
        description="Academic-history chat (CLI mode).",
    )
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    candidates = [
        Path(__file__).resolve().parent / "_common.py",
        Path(
            "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/notebooks/14_academic_history/_common.py"
        ),
        Path.cwd() / "_common.py",
    ]
    notebook_dir = None
    for c in candidates:
        if c.exists():
            notebook_dir = c.parent
            break
    if notebook_dir is None:
        raise SystemExit("Could not locate _common.py.")
    sys.path.insert(0, str(notebook_dir))
    from _common import load_manifest_or_default, pseudo_id  # noqa: E402

    try:
        from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (  # noqa: E402
            run_tool,
        )
        modules = run_tool("list_my_modules")
        progress = run_tool("summarise_my_progress")
    except Exception as exc:  # noqa: BLE001
        modules = []
        progress = {"error": str(exc)}

    manifest = load_manifest_or_default()
    print(
        json.dumps(
            {
                "pseudonym": pseudo_id(manifest),
                "modules": modules,
                "progress": progress,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()