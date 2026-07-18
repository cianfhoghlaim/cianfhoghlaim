# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "altair>=5.0",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Shared helpers for the `14_academic_history` marimo notebooks.

Companion to the 8 notebooks introduced by
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Conventions:

- PEP 723 inline dependency block
- 5-panel Altair dashboard layout with health banner
- `mo.sql(engine=md:cianfhoghlaim)` for live queries (graceful local
  DuckDB fallback via `nb_utils.connect_biep_lakehouse()`)
- CLI dual-mode (`--module-code`, `--module-title`, `--year`,
  `--limit`) via `nb_utils.cl_argument_parser()` + `nb_utils.run_as_script()`
- Per-user pseudonymous ID via
  `academic_history_manifest.pseudonym_hash()`
- Privacy gate (default `INCLUDE_IDENTITY_RECORDS=false`)

Helpers exported:

- `load_manifest_or_default(path)` — load the manifest or return a
  sensible default pointing at the UoG case-study corpus.
- `acad_table(name)` — return the canonical DuckLake table name.
- `pseudo_id()` — compute the per-user pseudonym hash.
- `acad_engine_label()` — return one of
  `{"md:cianfhoghlaim", "local_duckdb", "unavailable"}`.
- `acad_health_md(engine_label, status, rows)` — render the canonical
  health banner.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Optional heavy imports — degraded gracefully if not installed.
try:
    import altair as alt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    alt = None  # type: ignore[assignment]

try:
    import duckdb  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    duckdb = None  # type: ignore[assignment]

try:
    import marimo as mo  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    mo = None  # type: ignore[assignment]

__all__ = [
    "load_manifest_or_default",
    "acad_table",
    "pseudo_id",
    "acad_engine_label",
    "acad_health_md",
    "render_5_panel",
]


# Canonical DuckLake table names (L2 layer).
ACAD_TABLES: dict[str, str] = {
    "coursework": "cianfhoghlaim.education.ie.uog_math_coursework",
    "formulas": "cianfhoghlaim.education.ie.uog_formula_records",
    "theorems": "cianfhoghlaim.education.ie.uog_theorem_records",
    "stats": "cianfhoghlaim.education.ie.uog_statistical_procedure_records",
    "numerical": "cianfhoghlaim.education.ie.uog_numerical_method_records",
    "nonlinear": "cianfhoghlaim.education.ie.uog_nonlinear_system_records",
    "findings": "oideachais_academic_history.validation_findings",
}


def acad_table(name: str) -> str:
    """Return the canonical DuckLake table name for `name`."""
    if name not in ACAD_TABLES:
        raise ValueError(f"unknown academic-history table alias: {name}")
    return ACAD_TABLES[name]


def load_manifest_or_default(path: str | os.PathLike[str] | None = None):
    """Load the academic-history manifest or return the default stub."""
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (  # type: ignore[import-not-found]
        AcademicHistoryManifest,
        ModuleRoot,
        Privacy,
        StudentProfile,
        load_manifest,
    )

    candidate = Path(
        path or os.environ.get(
            "ACADEMIC_HISTORY_MANIFEST", "academic_history_manifest.yaml"
        )
    )
    if candidate.exists():
        try:
            return load_manifest(candidate)
        except Exception:  # noqa: BLE001 - defensive
            pass

    # Default UoG case-study stub.
    return AcademicHistoryManifest(
        student_profile=StudentProfile(
            pseudonym="change-me",
            institution="University of Galway",
            programme="BSc Mathematics",
            years=["2024-2025", "2025-2026"],
        ),
        module_roots=[
            ModuleRoot(
                path="leabharlann/ollscoil_na_gaillimhe/mata",
                module_code="ST311",
                module_title="Probability & Statistics",
            ),
            ModuleRoot(
                path="leabharlann/ollscoil_na_gaillimhe/past",
                module_code="MA335",
                module_title="Numerical Analysis",
            ),
        ],
        privacy=Privacy(include_identity_records=False),
    )


def pseudo_id(manifest=None) -> str:
    """Return the per-user pseudonym hash."""
    if manifest is None:
        manifest = load_manifest_or_default()
    try:
        return manifest.pseudonym_hash()
    except Exception:  # noqa: BLE001 - defensive
        return "h:00000000000000000000000000000000"


def acad_engine_label() -> str:
    """Return the engine label (`md:cianfhoghlaim` / `local_duckdb` /
    `unavailable`)."""
    if duckdb is None:
        return "unavailable"
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            try:
                duckdb.sql(f"SET motherduck_token='{token}'")
                con = duckdb.connect("md:cianfhoghlaim")
                con.execute("SELECT 1").fetchall()
                con.close()
                return "md:cianfhoghlaim"
            except Exception:
                return "local_duckdb"
    return "local_duckdb"


def acad_health_md(engine_label: str, status: str, rows: int) -> str:
    """Render the canonical health banner."""
    badge = "🟢" if status == "live" else "🟡"
    return (
        f"### Panel E — engine health\n\n"
        f"| field | value |\n"
        f"|-------|-------|\n"
        f"| engine | `{engine_label}` |\n"
        f"| status | {badge} {status} |\n"
        f"| rows | {rows} |\n"
    )


def render_5_panel(
    panel_a: Any,
    panel_b: Any,
    panel_c: Any,
    panel_d: Any,
    health_md: Any,
    *,
    width: int = 720,
    height: int = 320,
) -> dict[str, Any]:
    """Render the canonical 5-panel dashboard layout.

    Each panel is an Altair chart. `health_md` is a marimo markdown cell.
    Returns a dict mapping panel letters to their rendered objects for
    the caller to `mo.vstack(...)` / `mo.hstack(...)`.
    """
    return {
        "A": panel_a.properties(width=width, height=height, title="Panel A —"),
        "B": panel_b.properties(width=width, height=height, title="Panel B —"),
        "C": panel_c.properties(width=width, height=height, title="Panel C —"),
        "D": panel_d.properties(width=width, height=height, title="Panel D —"),
        "E": health_md,
    }