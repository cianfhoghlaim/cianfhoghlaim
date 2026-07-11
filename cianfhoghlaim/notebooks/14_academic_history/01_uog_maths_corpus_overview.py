# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""UoG Mathematics Corpus Overview — academic-history notebook #01.

Reads the academic-history manifest + the L1 filesystem scan results
and renders a 5-panel dashboard of the user's math/statistics artefacts.
Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Panels:
- A: artefact count by module
- B: artefact type distribution (file extension)
- C: artefact size histogram (bytes)
- D: privacy-gating coverage (kept vs skipped rows)
- E: engine health banner

CLI:

    uv run cianfhoghlaim-marimo run 14_academic_history/01_uog_maths_corpus_overview \\
        -- --module-code ST311 --limit 50
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Helpers are imported in the _imports cell below so they survive the
# marimo flat-script export (which strips module-level relative imports).
import marimo

__generated_with_marimo__ = "0.23.13"

app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import (  # noqa: E402
        acad_engine_label,
        acad_health_md,
        pseudo_id,
        load_manifest_or_default,
    )
    return acad_engine_label, acad_health_md, load_manifest_or_default, mo, pseudo_id


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # UoG Mathematics Corpus Overview

        The 1st of 8 notebooks in `notebooks/14_academic_history/`
        (introduced by
        `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`).

        This dashboard reads the academic-history manifest and the
        L1 filesystem scan to show **what you have**, **how it is
        distributed**, and **what is privacy-gated**.
        """
    )
    return


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # UoG Mathematics Corpus Overview

        The 1st of 8 notebooks in `notebooks/14_academic_history/`
        (introduced by
        `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`).

        This dashboard reads the academic-history manifest and the
        L1 filesystem scan to show **what you have**, **how it is
        distributed**, and **what is privacy-gated**.
        """
    )
    return


@app.cell
def _manifest(load_manifest_or_default, mo):
    manifest = load_manifest_or_default()
    module_rows = [
        {
            "module_code": r.module_code,
            "module_title": r.module_title or "",
            "path": r.path,
            "academic_year": r.academic_year or "",
        }
        for r in manifest.module_roots
    ]
    mo.ui.table(module_rows, label="Configured modules")
    return (manifest,)


@app.cell
def _scan(manifest, mo):
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
                            "kept": True,
                            "rel_path": rel,
                        }
                    )
    mo.md(f"**Discovered**: {len(file_rows)} artefacts")
    return (file_rows,)


@app.cell
def _panels(
    acad_engine_label,
    acad_health_md,
    file_rows,
    manifest,
    mo,
    pseudo_id,
):
    no_data_md = mo.md(
        "**No artefacts yet** — populate `academic_history_manifest.yaml` "
        "and re-run the L1 ingestion asset."
    )
    has_data = bool(file_rows)

    by_module: dict[str, int] = {}
    for r in file_rows:
        by_module[r["module_code"]] = by_module.get(r["module_code"], 0) + 1
    panel_a_lines = [
        f"- `{code}`: {count} artefacts"
        for code, count in sorted(by_module.items(), key=lambda x: -x[1])
    ]
    panel_a_md = mo.md(
        "### Panel A — artefact count by module\n\n" + "\n".join(panel_a_lines)
    )

    by_ext: dict[str, int] = {}
    for r in file_rows:
        ext = r["extension"] or "<no-ext>"
        by_ext[ext] = by_ext.get(ext, 0) + 1
    panel_b_lines = [
        f"- `{ext}`: {count}"
        for ext, count in sorted(by_ext.items(), key=lambda x: -x[1])
    ]
    panel_b_md = mo.md(
        "### Panel B — extension distribution\n\n" + "\n".join(panel_b_lines)
    )

    sizes = [r["size_bytes"] for r in file_rows]
    sizes_sorted = sorted(sizes)
    n = len(sizes_sorted)
    if n >= 4:
        q1 = sizes_sorted[n // 4]
        q2 = sizes_sorted[n // 2]
        q3 = sizes_sorted[3 * n // 4]
        panel_c_text = (
            f"### Panel C — size histogram (n={n})\n\n"
            f"- min: {sizes_sorted[0]:,} B\n"
            f"- q1: {q1:,} B\n"
            f"- median: {q2:,} B\n"
            f"- q3: {q3:,} B\n"
            f"- max: {sizes_sorted[-1]:,} B\n"
        )
    else:
        panel_c_text = (
            f"### Panel C — size histogram (n={n})\n\n- sizes: {sizes_sorted}\n"
        )
    panel_c_md = mo.md(panel_c_text)

    panel_d_text = (
        f"### Panel D — privacy-gating\n\n"
        f"- rows kept: {len(file_rows)}\n"
        f"- pseudonymous id: `{pseudo_id(manifest)}`\n"
        f"- include_identity_records: `false` (default)\n"
    )
    panel_d_md = mo.md(panel_d_text)

    engine = acad_engine_label()
    health_md = mo.md(
        acad_health_md(engine, "offline fallback (synthetic)", len(file_rows))
    )

    # Use the no_data placeholder when there are no artefacts.
    final_a = panel_a_md if has_data else no_data_md
    final_b = panel_b_md if has_data else no_data_md
    final_c = panel_c_md if has_data else no_data_md
    final_d = panel_d_md if has_data else no_data_md
    mo.vstack([final_a, final_b, final_c, final_d, health_md])
    return


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📊 This dashboard backs the
        `oideachais-academic-history-pipeline` spec R3.
        See `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.
        """
    )
    return


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="01_uog_maths_corpus_overview",
        description="UoG Mathematics corpus overview (CLI mode).",
    )
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--module-title", default=None)
    parser.add_argument("--year", default=None)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)
    # Import the helpers at runtime so the CLI mode works whether or
    # not the notebook cells have run. The notebook's directory is
    # derived from the cianfhoghlaim package layout (the file is
    # always at <repo>/cianfhoghlaim/notebooks/14_academic_history/
    # even when the script is exported to /tmp).
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
        raise SystemExit(
            "Could not locate _common.py. Run this notebook from the "
            "cianfhoghlaim/notebooks/14_academic_history/ directory or "
            "export it via `marimo export script` to a location where "
            "_common.py is reachable."
        )
    sys.path.insert(0, str(notebook_dir))
    from _common import (  # noqa: E402
        acad_engine_label,
        load_manifest_or_default,
        pseudo_id,
    )

    manifest = load_manifest_or_default()
    rows = []
    for r in manifest.module_roots:
        if args.module_code and r.module_code != args.module_code:
            continue
        if args.module_title and (r.module_title or "") != args.module_title:
            continue
        path = manifest.resolve_path(r.path)
        if path.exists() and path.is_dir():
            for f in sorted(path.rglob("*"))[: args.limit]:
                if not f.is_file():
                    continue
                rel = str(f.relative_to(path))
                if manifest.include_file(rel):
                    rows.append(
                        {
                            "module_code": r.module_code,
                            "module_title": r.module_title or "",
                            "file_name": f.name,
                            "extension": f.suffix.lower(),
                            "size_bytes": f.stat().st_size,
                        }
                    )
    print(
        json.dumps(
            {
                "pseudonym": pseudo_id(manifest),
                "module_count": len(manifest.module_roots),
                "artefact_count": len(rows),
                "engine": acad_engine_label(),
                "rows": rows,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()