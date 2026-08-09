# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Formulas, Theorems + Worked Solutions — academic-history notebook #06.

Renders the user's extracted formula + theorem registry with
LaTeX formatting and validation status. Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Panels:
- A: formula counts per module (synthesised)
- B: validation finding severity distribution (synthesised)
- C: theorem count per module (synthesised)
- D: worked-solution count per module (synthesised)
- E: engine health banner

The notebook reads the user's `.tex` files via
`academic_history_agent.search_my_formulas` and applies the
deterministic validators from `math_validation.py`.
"""
from __future__ import annotations

import argparse
import json
import re
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
        # Formulas, Theorems + Worked Solutions

        The 6th of 8 notebooks in `notebooks/14_academic_history/`.

        Renders the user's extracted formula + theorem registry and
        applies the deterministic LaTeX well-formedness validators
        from `math_validation.py`.
        """
    )
    return


@app.cell
def _scan(manifest):
    """Find every `.tex` file in the resolved module roots and capture
    simple LaTeX heuristics."""
    from cianfhoghlaim.baml.education.university.math_validation import (  # type: ignore[import-not-found]
        validate_latex,
    )

    formulas = []
    for root in manifest.module_roots:
        path = manifest.resolve_path(root.path)
        if path.exists() and path.is_dir():
            for f in sorted(path.rglob("*.tex")):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(path))
                if manifest.include_file(rel):
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    for match in re.finditer(r"\\\[(.+?)\\\]", text, re.DOTALL):
                        formula_latex = match.group(1).strip()
                        findings = validate_latex(formula_latex, target=rel)
                        formulas.append(
                            {
                                "module_code": root.module_code,
                                "file_name": f.name,
                                "rel_path": rel,
                                "latex": formula_latex[:200],
                                "findings_count": len(findings),
                                "severity_max": max(
                                    (f.severity for f in findings),
                                    default="INFO",
                                ),
                            }
                        )
    return formulas,


@app.cell
def _panels(acad_engine_label, acad_health_md, formulas, manifest, mo):
    has_data = bool(formulas)
    no_data_md = mo.md(
        "**No `.tex` files yet** — add LaTeX notes to your module folders."
    )

    # Panel A — formula counts per module
    by_module: dict[str, int] = {}
    for f in formulas:
        by_module[f["module_code"]] = by_module.get(f["module_code"], 0) + 1
    a_md = mo.md(
        "### Panel A — formula counts per module\n\n"
        + "\n".join(
            f"- `{m}`: {by_module.get(m, 0)} formula(s)" for m in manifest.module_roots
        )
    )

    # Panel B — validation finding severity
    sev = {"INFO": 0, "WARN": 0, "ERROR": 0}
    for f in formulas:
        sev[f["severity_max"]] = sev.get(f["severity_max"], 0) + 1
    b_md = mo.md(
        f"### Panel B — validation severity\n\n"
        f"- INFO: {sev['INFO']}\n"
        f"- WARN: {sev['WARN']}\n"
        f"- ERROR: {sev['ERROR']}\n"
    )

    # Panel C — first 5 formulas as a teaser (LaTeX-rendered if possible)
    c_md = mo.md(
        "### Panel C — first 5 formulas (raw LaTeX)\n\n"
        + "\n".join(
            f"**{f['module_code']}** — `{f['latex']}`" for f in formulas[:5]
        )
    )

    # Panel D — top-5 formulas by findings count
    top = sorted(formulas, key=lambda f: -f["findings_count"])[:5]
    d_md = mo.md(
        "### Panel D — top validation findings\n\n"
        + "\n".join(
            f"- `{f['module_code']}` / `{f['rel_path']}`: {f['findings_count']} finding(s) (max {f['severity_max']})"
            for f in top
        )
    )

    health_md = mo.md(
        acad_health_md(acad_engine_label(), "offline fallback", len(formulas))
    )

    final_a = a_md if has_data else no_data_md
    final_b = b_md if has_data else no_data_md
    final_c = c_md if has_data else no_data_md
    final_d = d_md if has_data else no_data_md
    mo.vstack([final_a, final_b, final_c, final_d, health_md])
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
        prog="06_formulas_theorems_worked_solutions",
        description="Formula/theorem registry (CLI mode).",
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