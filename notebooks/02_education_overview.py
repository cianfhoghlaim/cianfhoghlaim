# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
# ]
#
# [tool.uv]
# package = "biep-v2-overview"
# ///

"""BIEP v2 Overview Notebook — the cross-jurisdiction portal.

Per the 2026-07-23-biep-v2-marimo-portal-v1 change.

The 4 BIEP v2 jurisdictions + the canonical LanceDB tables:

  🇮🇪 Leaving Cert (LC):  cianfhoghlaim.lc.<subject>.<level>_<lang>
                           (6 subjects × 2 languages × 3 levels = 18 tables)
  🇮🇪 Junior Cycle (JC):  cianfhoghlaim.jc.<subject>.<year>_<lang>
                           (18 subjects × 2 languages × 3 years = 108 tables)
  🇬🇧 A-Level (England):   cianfhoghlaim.england.<board>.<subject>.<level>
                           (3 boards × 9 subjects × 2 levels = 54 tables)
  🇬🇧 GCSE (England):     cianfhoghlaim.england.<board>.<subject>.<level>
                           (3 boards × 9 subjects × 2 levels = 54 tables)

Cross-jurisdiction filter UI: subject / level / language / year / awarding body / curriculum region.
Reads from the canonical Lakehouse via the **ibis-first contract**:

    conn = ibis.duckdb.connect("md:cianfhoghlaim")
    lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")

(no raw `ibis.duckdb.connect(uri)` — per the ibis-first spec).

KCG patterns used:
- ibis (per `.agents/skills/ibis/SKILL.md`)
- marimo (per `.agents/skills/marimo/SKILL.md`)

Reference: openspec/changes/2026-07-23-biep-v2-marimo-portal-v1/
"""

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

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # BIEP v2 Overview — cross-jurisdiction curriculum portal

        Filter the 4 BIEP v2 jurisdictions (Leaving Cert + Junior Cycle +
        A-Level + GCSE) and browse the canonical LanceDB tables.

        ## Filter

        Use the controls below to filter the cohort.
        """
    )
    return (mo,)


@app.cell
def _filter_ui(mo):
    jurisdiction_filter = mo.ui.multiselect(
        options=["ireland_lc", "ireland_jc", "england_aqa", "england_ocr", "england_edexcel"],
        value=["ireland_lc", "england_aqa"],
        label="Jurisdiction",
    )
    subject_filter = mo.ui.multiselect(
        options=[
            "mathematics", "english", "gaeilge", "chemistry", "biology", "physics",
            "computer_science", "history", "geography", "english_language",
            "english_literature",
        ],
        value=["mathematics", "english"],
        label="Subject",
    )
    level_filter = mo.ui.multiselect(
        options=["hl", "ol", "fl", "gcse", "a_level", "year_1", "year_2", "year_3"],
        value=["hl", "gcse", "year_1"],
        label="Level",
    )
    language_filter = mo.ui.multiselect(
        options=["en", "ga"],
        value=["en"],
        label="Language",
    )
    mo.vstack([jurisdiction_filter, subject_filter, level_filter, language_filter])
    return jurisdiction_filter, subject_filter, level_filter, language_filter


@app.cell
def _ibis_conn(mo):
    """The ibis-first contract per the BIEP v2 spec.

    First data cell executes the canonical ibis queries.
    No raw `ibis.duckdb.connect()` per the ibis-first contract.
    """
    import ibis

    # The DuckLake (analytics) side
    conn = ibis.duckdb.connect("md:cianfhoghlaim")
    # The Lance (vector + structured) side
    lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
    mo.md("✓ ibis-first contract wired (md:cianfhoghlaim + rest://lakehouse-lance-namespace:8182)")
    return conn, lance


@app.cell
def _cross_jurisdiction_table(conn, jurisdiction_filter, subject_filter, level_filter):
    """The cross-jurisdiction cohort view."""
    # ibis query: total chunk counts per jurisdiction × subject × level.
    # Real impl: union of 4 jurisdiction tables via ibis.
    cohort_table = conn.sql(
        """
        SELECT jurisdiction, board, subject, level, language, COUNT(*) AS chunk_count
        FROM cianfhoghlaim.education.british_isles._biep_v2_cohort
        WHERE jurisdiction IN %(jurisdictions)s
          AND subject IN %(subjects)s
        GROUP BY jurisdiction, board, subject, level, language
        ORDER BY jurisdiction, board, subject, level, language
        """,
        params={
            "jurisdictions": tuple(jurisdiction_filter.value),
            "subjects": tuple(subject_filter.value),
        },
    ).execute()
    cohort_table
    return (cohort_table,)


@app.cell
def _summary(cohort_table, mo):
    """The cross-jurisdiction summary."""
    mo.md(f"## Total cohort size: **{len(cohort_table)} jurisdiction × subject × level triples**")
    return


if __name__ == "__main__":
    app.run()
