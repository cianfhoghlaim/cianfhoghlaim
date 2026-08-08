# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""cianfhoghlaim.notebooks.dashboards.education.all_nations — Marimo
notebook that compares Irish, NI, EN, SCT, WLS education pipelines
side-by-side.

Phase 8 of the openspec change. Reads from
``cianfhoghlaim.education.<nation>.<entity>`` (MotherDuck + DuckLake lakehouse
via the ``md:cianfhoghlaim`` alias; falls back to a local DuckLake attach
when ``MOTHERDUCK_TOKEN`` is unset).
"""
from __future__ import annotations

import marimo


# Centralized registries (per the `centralized-model-registry` capability).
# Cascading effect: this notebook now uses MODEL_REGISTRY + the 5 schema
# introspection helpers from notebooks/_shared/schema.py instead of
# hardcoded table lists / hardcoded schema strings.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        schema_introspect, schema_introspect_table, read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import os
    import marimo as mo
    import duckdb
    import ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)
    return duckdb, ibis, mo, os


@app.cell
def _header(mo):
    mo.md(
        r"""
        # Education — All Nations (Phase 8)

        Cross-nation view of the unified MotherDuck + DuckLake lakehouse
        ``md:cianfhoghlaim`` — table ``cianfhoghlaim.education.<nation>.<entity>``.
        Filter by cycle and subject; charts render on the same x-axis.
        """
    )
    return ()


@app.cell
def _connect():
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this
    # cell's own hand-rolled DuckLake ATTACH (`ATTACH 'ducklake' (TYPE
    # DUCKLAKE, DATA_PATH ...)`) used a syntax that requires a
    # pre-created DuckDB SECRET named "ducklake" that never existed here
    # (confirmed live: `Secret "ducklake" was not found`) -- on top of
    # the separate `.execute()` vs `.raw_sql()` bug already fixed above.
    # Rather than debug a 3rd, notebook-specific ATTACH variant, this
    # now uses the real, live-verified canonical connection helper
    # (`notebooks/_shared/db.py::connect_local_lakehouse()`, tries the
    # real local DuckLake stack first, falls back to `connect_md()` for
    # MotherDuck, matching this notebook's own original docstring
    # intent) rather than reinventing per-notebook ATTACH logic.
    from notebooks._shared.db import connect_local_lakehouse

    # No `USE <schema>` needed -- the query below (`_summary`) already
    # fully-qualifies every table as `cianfhoghlaim.education.<nation>.
    # <entity>`. The `USE oideachais;` this cell used to run doesn't
    # correspond to any schema in the real catalog (confirmed live:
    # a raw DuckDB parser error) and served no purpose given the
    # already-qualified queries below.
    con = connect_local_lakehouse(read_only=True)
    return (con,)


@app.cell
def _summary(con):
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: the
    # original query referenced `cianfhoghlaim.education.<nation>.
    # <entity>` -- a 4-part catalog.schema.subschema.table name DuckDB's
    # parser can't handle at all (confirmed live: "NameListToString NOT
    # IMPLEMENTED"), against per-nation sub-schemas/tables
    # (`ncca_pages`, `ccea_pages`, `dfe_statistics`, ...) that don't
    # exist in the real catalog either -- the catalog alias
    # (`cianfhoghlaim.` — the real one, attached by
    # connect_local_lakehouse(), is `lakehouse.`) was also wrong.
    # Rewritten against the REAL live schema
    # (`lakehouse.education.subjects`, one row per jurisdiction/subject,
    # live-verified to hold real BIEP registry data) to give the same
    # "rows per nation" summary this cell is meant to show.
    rows = con.raw_sql(
        """
        SELECT jurisdiction AS nation, count(*) AS n
        FROM lakehouse.education.subjects
        GROUP BY jurisdiction
        ORDER BY jurisdiction
        """
    ).fetchall()
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Rows per nation/agency (snapshot):** {rows}")
    return ()


if __name__ == "__main__":
    app.run()