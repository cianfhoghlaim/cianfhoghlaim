# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Module Syllabus + Assessment Map — academic-history notebook #02.

Joins the academic-history manifest rows (the user's personal
artefacts) to the official UoG module descriptors
(`oideachais.education.ie.university_modules`).

Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Panels:
- A: configured modules × descriptor availability
- B: LOs per module
- C: assessment pieces per module
- D: per-module artefact count (joined)
- E: engine health banner
"""
from __future__ import annotations

import argparse
import json
import os
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
        # Module Syllabus + Assessment Map

        The 2nd of 8 notebooks in `notebooks/14_academic_history/`.

        Joins the academic-history manifest rows (the user's personal
        artefacts) to the **official UoG module descriptors** populated
        by the `oideachais-university-deep-extraction` pipeline.
        """
    )
    return


@app.cell
def _load(load_manifest_or_default, mo):
    """Load the manifest + a synthetic per-module descriptor stub."""
    manifest = load_manifest_or_default()
    # In production this table is populated by the L2 baml_extraction
    # asset for the official UoG descriptors. For the default stub we
    # synthesise a small descriptor per manifest module so the join
    # is non-empty even before the lakehouse has been populated.
    descriptors = {
        r.module_code: {
            "module_code": r.module_code,
            "module_title": r.module_title or "",
            "learning_outcomes": [
                "Understand the core concepts.",
                "Apply the methods to novel problems.",
                "Communicate the results clearly.",
            ],
            "assessment_pieces": [
                "assignment_1",
                "midterm_test",
                "final_exam",
            ],
            "ects": 5,
            "prerequisites": [],
        }
        for r in manifest.module_roots
    }
    mo.md(f"**Modules in manifest**: {len(descriptors)}")
    return descriptors, manifest


@app.cell
def _panels(
    acad_engine_label,
    acad_health_md,
    descriptors,
    file_rows,
    manifest,
    mo,
    pseudo_id,
):
    """Render the 5 panels."""
    has_data = bool(file_rows)
    no_data_md = mo.md(
        "**No artefacts yet** — populate `academic_history_manifest.yaml` and re-run."
    )

    # Panel A — modules × descriptor availability
    a_rows = [
        {
            "module_code": code,
            "module_title": d["module_title"],
            "has_descriptor": "yes",
            "lo_count": len(d["learning_outcomes"]),
        }
        for code, d in descriptors.items()
    ]
    a_md = mo.md(
        "### Panel A — modules × descriptor availability\n\n"
        + "\n".join(
            f"- `{r['module_code']}`: {r['module_title']} ({r['lo_count']} LOs)"
            for r in a_rows
        )
    )

    # Panel B — LOs per module
    b_lines = []
    for code, d in descriptors.items():
        b_lines.append(f"**{code}** ({d['module_title']}):")
        for lo in d["learning_outcomes"]:
            b_lines.append(f"  - {lo}")
    b_md = mo.md("### Panel B — learning outcomes\n\n" + "\n".join(b_lines))

    # Panel C — assessment pieces
    c_lines = []
    for code, d in descriptors.items():
        c_lines.append(f"**{code}**: {', '.join(d['assessment_pieces'])}")
    c_md = mo.md("### Panel C — assessment pieces\n\n" + "\n".join(c_lines))

    # Panel D — per-module artefact count (joined)
    by_module: dict[str, int] = {}
    for r in file_rows:
        by_module[r["module_code"]] = by_module.get(r["module_code"], 0) + 1
    d_lines = [
        f"- `{code}`: {by_module.get(code, 0)} artefact(s)"
        for code in descriptors.keys()
    ]
    d_md = mo.md("### Panel D — artefacts per module (joined)\n\n" + "\n".join(d_lines))

    # Panel E — engine health
    health_md = mo.md(acad_health_md(acad_engine_label(), "offline fallback", len(file_rows)))

    final_a = a_md if has_data else no_data_md
    final_b = b_md if has_data else no_data_md
    final_c = c_md if has_data else no_data_md
    final_d = d_md if has_data else no_data_md
    mo.vstack([final_a, final_b, final_c, final_d, health_md])
    return


@app.cell
def _scan(manifest):
    """Yield file-level rows."""
    file_rows = []
    for root in manifest.module_roots:
        path = manifest.resolve_path(root.path)
        if path.exists() and path.is_dir():
            for f in sorted(path.rglob("*")):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(path))
                if manifest.include_file(rel):
                    file_rows.append(
                        {
                            "module_code": root.module_code,
                            "file_name": f.name,
                            "extension": f.suffix.lower(),
                            "size_bytes": f.stat().st_size,
                            "rel_path": rel,
                        }
                    )
    return (file_rows,)


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📊 This dashboard backs the
        `oideachais-university-deep-extraction` spec R5.
        See `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.
        """
    )
    return


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="02_module_syllabus_assessment_map",
        description="Module syllabus + assessment map (CLI mode).",
    )
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--module-title", default=None)
    parser.add_argument("--year", default=None)
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
    from _common import (  # noqa: E402
        acad_engine_label,
        load_manifest_or_default,
        pseudo_id,
    )

    manifest = load_manifest_or_default()
    descriptors = {
        r.module_code: {
            "module_code": r.module_code,
            "module_title": r.module_title or "",
            "learning_outcomes": ["LO 1", "LO 2", "LO 3"],
            "assessment_pieces": ["assignment", "final_exam"],
            "ects": 5,
        }
        for r in manifest.module_roots
    }
    print(
        json.dumps(
            {
                "pseudonym": pseudo_id(manifest),
                "module_count": len(descriptors),
                "descriptors": descriptors,
                "engine": acad_engine_label(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()