# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
# ]
# ///
"""BAML drift audit — Cianfhoghlaim Oideachais (BIEP).

Per R7.6: BAML drift audit. For every BAML ``function`` declared in
``cianfhoghlaim/baml_src/**/*.baml``, count how many Python callers
import + invoke it via the generated ``cianfhoghlaim.baml_client.b.*``
client. Functions with zero callers are flagged as drift candidates;
functions with callers that don't match the v4 module naming
(``cianfhoghlaim.dlt.british_isles.ireland.education.*``) are flagged
as legacy.

Strategy:

1. Parse all BAML files under ``cianfhoghlaim/baml_src/`` to extract
   the ``function <Name>(...)`` declarations.
2. Walk the v4 Python source tree (skipping the generated
   ``baml_client/`` directory) and grep for ``b.<Name>(`` calls.
3. Cross-tabulate declarations × callers; render the drift matrix
   in marimo.
"""
from __future__ import annotations

import os
import pathlib
import re
from collections import defaultdict

import marimo

__generated_with_marimo = True
app = marimo.App(width="medium")


# -----------------------------------------------------------------------------
# Static analysis — find all BAML function declarations
# -----------------------------------------------------------------------------


_BAML_FUNCTION_RE = re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_PY_CALLER_RE = re.compile(r"\bb\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _find_baml_functions(baml_src_root: pathlib.Path) -> dict[str, list[pathlib.Path]]:
    """Map ``function_name -> [pathlib.Path(...)]`` of BAML files declaring it."""
    decls: dict[str, list[pathlib.Path]] = defaultdict(list)
    for baml_file in baml_src_root.rglob("*.baml"):
        if baml_file.name.startswith("clients"):
            continue
        for line in baml_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = _BAML_FUNCTION_RE.match(line)
            if m:
                decls[m.group(1)].append(baml_file)
    return decls


def _find_callers(
    py_root: pathlib.Path, names: set[str]
) -> dict[str, list[pathlib.Path]]:
    """Map ``function_name -> [pathlib.Path(...)]`` of Python files calling it."""
    callers: dict[str, list[pathlib.Path]] = defaultdict(list)
    skip_dirs = {"baml_client", "__pycache__", ".venv", "node_modules", ".git"}
    skip_dirs |= {"tests", "fixtures", "docs"}
    for py_file in py_root.rglob("*.py"):
        if any(part in skip_dirs for part in py_file.parts):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in _PY_CALLER_RE.finditer(content):
            if m.group(1) in names:
                callers[m.group(1)].append(py_file)
    return callers


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    repo_root = pathlib.Path(
        os.environ.get(
            "CIANFHOGHLAIM_ROOT",
            str(pathlib.Path.home() / "dev" / "kings_college_galway"),
        )
    )
    baml_src_root = repo_root / "cianfhoghlaim" / "baml_src"
    py_root = repo_root / "cianfhoghlaim"

    if not baml_src_root.exists():
        mo.md(f"⚠️ BAML source dir not found at `{baml_src_root}`.")
        return (None, None, None)

    decls = _find_baml_functions(baml_src_root)
    callers = _find_callers(py_root, set(decls.keys()))

    total_decl = len(decls)
    total_call = len(callers)
    drift = sorted(set(decls) - set(callers))
    legacy_callers: dict[str, list[str]] = {}
    for name, paths in callers.items():
        legacy = [
            str(p.relative_to(repo_root))
            for p in paths
            if "oideachais" in str(p).replace("cianfhoghlaim/", "")
        ]
        if legacy:
            legacy_callers[name] = legacy

    mo.md(
        f"""
        # BAML Drift Audit — BIEP

        Cross-checks the BAML ``function`` declarations under
        `cianfhoghlaim/baml_src/` against the Python callers under
        `cianfhoghlaim/`.

        - **{total_decl}** BAML functions declared
        - **{total_call}** BAML functions invoked from Python
        - **{len(drift)}** drift candidates (declared but never called)
        - **{len(legacy_callers)}** functions still called from a
          `oideachais/...` path (should be migrated to
          `cianfhoghlaim/dlt/british_isles/ireland/education/...`)
        """
    )
    return baml_src_root, callers, decls, drift, legacy_callers, mo, py_root, repo_root


@app.cell
def _(callers, decls, drift, mo):
    import pandas as pd

    rows = []
    for name in sorted(decls):
        caller_paths = callers.get(name, [])
        rows.append(
            {
                "function": name,
                "baml_file": str(decls[name][0].name),
                "callers": len(caller_paths),
                "drift": "⚠️" if not caller_paths else "",
                "first_caller": (
                    str(caller_paths[0]) if caller_paths else "(none)"
                ),
            }
        )
    df = pd.DataFrame(rows).sort_values(["drift", "callers"], ascending=[False, True])

    mo.vstack([
        mo.md("## Drift matrix — declared vs called"),
        mo.ui.table(df, page_size=25, selection=None),
    ])
    return df, pd, rows


@app.cell
def _(drift, mo):
    if drift:
        mo.md(
            "## Drift candidates (never called)\n\n"
            + "\n".join(f"- `{name}`" for name in drift[:50])
        )
    else:
        mo.md(
            "✅ **No drift candidates** — every declared BAML function "
            "has at least one Python caller."
        )
    return


@app.cell
def _(legacy_callers, mo):
    if not legacy_callers:
        mo.md(
            "✅ **No legacy callers** — every BAML invocation is routed "
            "through the v4 `cianfhoghlaim.dlt.british_isles.ireland.education.*` "
            "path (or a non-prefixed CIEP module)."
        )
    else:
        rows_md = []
        for name, paths in sorted(legacy_callers.items()):
            rows_md.append(
                f"- `{name}` ← {len(paths)} legacy caller(s) "
                f"(first: `{paths[0]}`)"
            )
        mo.md(
            "## Legacy callers (still routed via the old `oideachais/...` path)\n\n"
            + "\n".join(rows_md)
        )
    return


if __name__ == "__main__":
    app.run()