# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
# ]
# ///
"""05 — OpenSpec capability-spec discovery.

Demonstrates `openspec_list_specs` from
`cianfhoghlaim.agents.adk.tools.dev_env` — lists all openspec
capability specs (currently 37), filterable by quadrant.

See also:
- `openspec/AGENTS.md`
- `.agents/skills/indexing-and-cognition/SKILL.md`
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
        # 05 — openspec_list_specs (capability discovery)

        Live demo of `openspec_list_specs` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. Lists all 37
        capability specs in the Cianfhoghlaim monorepo.

        **Quadrant filter:**
        - `oideachais` — Celtic education data platform
        - `meaisinfhoghlaim` — AI/ML services
        - `tuatha` — Educational MMO
        - `croilar` — Multi-persona portfolio
        - `shared` — Cross-quadrant capabilities
        - `team` — Team workflow stack
        - `tooling` — Build / docs / code-search tooling
        - (blank) — all 37 specs
        """
    )
    return


@app.cell
def _quadrant_picker(mo):
    """Single-select dropdown for the quadrant to filter on."""
    quadrant = mo.ui.dropdown(
        options=[
            "", "oideachais", "meaisinfhoghlaim", "tuatha", "croilar",
            "shared", "team", "tooling",
        ],
        value="",
        label="Quadrant filter (blank = all)",
    )
    quadrant
    return (quadrant,)


@app.cell
def _run_listing(quadrant):
    """Call `openspec_list_specs` with the selected filter."""
    import asyncio
    import importlib.util
    from pathlib import Path

    # Phase 1 fix: compute absolute path from __file__ so the
    # notebook loads the dev_env tool module from any cwd.
    #   <repo>/cianfhoghlaim/notebooks/01_dev_env/0X.py
    # Tool:  <repo>/cianfhoghlaim/agents/adk/tools/dev_env.py
    # Path:  notebooks.parents[1] = cianfhoghlaim (package root)
    _HERE = Path(__file__).resolve().parent
    _TOOL = (
        _HERE.parents[1] / "agents" / "adk" / "tools" / "dev_env.py"
    )
    _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    result = asyncio.run(
        _mod.openspec_list_specs(quadrant=quadrant.value or None)
    )
    return Path, result


@app.cell
def _render(result, mo, quadrant):
    """Render the spec list as a markdown table."""
    specs = result.get("specs", [])
    count = result.get("count", 0)

    if not specs:
        mo.md(
            f"_No specs found for quadrant `{quadrant.value or 'all'}`._"
        )

    # Group by quadrant (if filter is blank)
    if not quadrant.value:
        by_quadrant: dict[str, list[dict]] = {}
        for s in specs:
            q = s.get("quadrant", "unknown")
            by_quadrant.setdefault(q, []).append(s)

        sections = []
        for q in sorted(by_quadrant.keys()):
            qspecs = by_quadrant[q]
            rows = "\n".join(
                f"| [`{s.get('id', s.get('name', '?'))}`](../specs/{s.get('id', '?')}/spec.md) | "
                f"{(s.get('one_liner') or s.get('description') or '')[:120]} |"
                for s in qspecs
            )
            sections.append(
                f"### {q} ({len(qspecs)} specs)\n\n"
                f"| spec id | one-liner |\n"
                f"|---------|-----------|\n"
                f"{rows}"
            )
        body = "\n\n".join(sections)
    else:
        rows = "\n".join(
            f"| `{s.get('id', '?')}` | {(s.get('one_liner') or s.get('description') or '')[:120]} |"
            for s in specs
        )
        body = f"| spec id | one-liner |\n|---------|-----------|\n{rows}"

    mo.md(
        f"""
        ## {count} spec(s) — `{quadrant.value or 'all quadrants'}`

        {body}

        **How to navigate:** click any spec id to open its `spec.md`.
        For pending changes (not yet archived), see
        `openspec/changes/<change-id>/proposal.md`.

        **Try next:** chain with `openspec_validate` (notebook 06)
        to check whether your in-flight change passes `--strict`.
        """
    )
    return body, by_quadrant, count, specs


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run 05_openspec_list.py as a CLI script from any cwd.

    Usage from any directory:
        python 05_openspec_list.py --help
        uv run notebooks/01_dev_env/05_openspec_list.py <flags>

    The marimo entry point is unchanged:
        marimo edit 05_openspec_list.py
        marimo run  05_openspec_list.py
    """
    import argparse
    import asyncio
    import importlib.util
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='05_openspec_list.py', description=__doc__)
    parser.add_argument("--quadrant", type=str, default="", help="Quadrant filter (oideachais/meaisinfhoghlaim/tuatha/croilar/shared/team/tooling, blank = all)")
    args = parser.parse_args(argv)

    # Load dev_env tool module (same absolute-path fix as Phase 1 cell above)
    _HERE = Path(__file__).resolve().parent
    _TOOL = _HERE.parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'
    _spec = importlib.util.spec_from_file_location('dev_env', _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    quad = args.quadrant or None
    results = asyncio.run(_mod.openspec_list_specs(quadrant=quad))
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
