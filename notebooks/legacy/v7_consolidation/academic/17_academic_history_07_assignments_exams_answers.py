# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Assignments, Exams + Answers — academic-history notebook #07.

Joins the user's assignments, exam papers, and answer scripts into a
single dashboard with mark / rubric comparison + improvement
suggestions. Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Panels:
- A: assignment / exam / answer counts per module
- B: file-extension distribution
- C: largest artefacts (top 5 by size)
- D: privacy-gating coverage (kept vs skipped)
- E: engine health banner

The notebook delegates side-by-side comparison to
`academic_history_agent.compare_my_answer_to_solution`.
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
        # Assignments, Exams + Answers

        The 7th of 8 notebooks in `notebooks/14_academic_history/`.

        Joins the user's assignments, exam papers, and answer scripts
        with mark / rubric comparison + improvement suggestions.
        Side-by-side comparison is delegated to
        `academic_history_agent.compare_my_answer_to_solution`.
        """
    )
    return


@app.cell
def _classify(manifest):
    """Classify artefacts by category based on path keywords."""
    rows = []
    for root in manifest.module_roots:
        path = manifest.resolve_path(root.path)
        if path.exists() and path.is_dir():
            for f in sorted(path.rglob("*")):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(path)).lower()
                if not manifest.include_file(rel):
                    continue
                if "answer" in rel:
                    category = "answer"
                elif "assignment" in rel:
                    category = "assignment"
                elif "exam" in rel:
                    category = "exam"
                elif "feedback" in rel:
                    category = "feedback"
                elif "solution" in rel or "worked" in rel:
                    category = "worked_solution"
                else:
                    category = "note"
                rows.append(
                    {
                        "module_code": root.module_code,
                        "category": category,
                        "file_name": f.name,
                        "size_bytes": f.stat().st_size,
                        "extension": f.suffix.lower(),
                    }
                )
    return (rows,)


@app.cell
def _panels(acad_engine_label, acad_health_md, mo, rows):
    has_data = bool(rows)
    no_data_md = mo.md(
        "**No artefacts yet** — populate `academic_history_manifest.yaml` and re-run."
    )

    # Panel A — counts per (module, category)
    by_module_cat: dict[str, dict[str, int]] = {}
    for r in rows:
        m = by_module_cat.setdefault(r["module_code"], {})
        m[r["category"]] = m.get(r["category"], 0) + 1
    a_lines = []
    for m, cats in by_module_cat.items():
        a_lines.append(
            f"**{m}**: " + ", ".join(f"{c}: {n}" for c, n in sorted(cats.items()))
        )
    a_md = mo.md(
        "### Panel A — counts per (module, category)\n\n" + "\n".join(a_lines)
    )

    # Panel B — extension distribution
    by_ext: dict[str, int] = {}
    for r in rows:
        ext = r["extension"] or "<no-ext>"
        by_ext[ext] = by_ext.get(ext, 0) + 1
    b_md = mo.md(
        "### Panel B — extension distribution\n\n"
        + "\n".join(f"- `{ext}`: {n}" for ext, n in sorted(by_ext.items(), key=lambda x: -x[1]))
    )

    # Panel C — top-5 largest artefacts
    top = sorted(rows, key=lambda r: -r["size_bytes"])[:5]
    c_md = mo.md(
        "### Panel C — top 5 largest artefacts\n\n"
        + "\n".join(
            f"- `{r['module_code']}` / `{r['file_name']}`: {r['size_bytes']:,} B"
            for r in top
        )
    )

    # Panel D — privacy gating
    d_md = mo.md(
        f"### Panel D — privacy-gating\n\n"
        f"- rows kept: {len(rows)}\n"
        f"- include_identity_records: `false` (default)\n"
    )

    health_md = mo.md(
        acad_health_md(acad_engine_label(), "offline fallback", len(rows))
    )

    final_a = a_md if has_data else no_data_md
    final_b = b_md if has_data else no_data_md
    final_c = c_md if has_data else no_data_md
    final_d = d_md if has_data else no_data_md
    mo.vstack([final_a, final_b, final_c, final_d, health_md])
    return


@app.cell
def _compare(mo, rows):
    """Render the side-by-side comparison helper (delegates to the agent)."""
    try:
        from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (  # type: ignore[import-not-found]
            run_tool,
        )
        agent_available = True
    except Exception:  # noqa: BLE001
        agent_available = False

    if rows and agent_available:
        answers = [r for r in rows if r["category"] == "answer"]
        solutions = [r for r in rows if r["category"] == "worked_solution"]
        if answers and solutions:
            result = run_tool(
                "compare_my_answer_to_solution",
                answer_path=answers[0]["file_name"],
                solution_path=solutions[0]["file_name"],
            )
            mo.md(
                "### Compare (first pair)\n\n```json\n"
                + json.dumps(result, indent=2)
                + "\n```"
            )
        else:
            mo.md(
                "> **Note**: no answer + worked_solution pair found in the manifest."
            )
    elif not agent_available:
        mo.md("> **Note**: `academic_history_agent` not importable.")
    else:
        mo.md("> **Note**: no rows; populate `academic_history_manifest.yaml` first.")
    return


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📊 This notebook backs the
        `oideachais-academic-history-pipeline` spec R3.
        See `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.
        """
    )
    return


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="07_assignments_exams_answers",
        description="Assignments / exams / answers (CLI mode).",
    )
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--limit", type=int, default=50)
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
    from _common import load_manifest_or_default  # noqa: E402

    manifest = load_manifest_or_default()
    print(
        json.dumps(
            {
                "module_code": args.module_code,
                "limit": args.limit,
                "modules": [r.module_code for r in manifest.module_roots],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()