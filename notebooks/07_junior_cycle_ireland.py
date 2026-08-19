from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Junior Cycle Explorer — drill into JC learning outcomes + the 36 CBAs.

Per the 2026-07-23-biep-v2-marimo-portal-v1 change.

Reads from the Junior Cycle LanceDB tables:
    cianfhoghlaim.jc.<subject>.<year>_<lang>

The 18 NCCA JC subjects + the 36 CBAs are explorable via multi-select.

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
        # Junior Cycle Explorer — 18 NCCA JC subjects × 36 CBAs

        Drill into the 18 NCCA Junior Cycle subjects and the 36 Classroom-Based
        Assessments (2 per subject). The Year 3 → Year 4 (Ordinary Level LC)
        topic progression is shown when a subject overlaps with the BIEP v1
        Leaving Certificate pipeline.
        """
    )
    return (mo,)


@app.cell
def _filter_ui(mo):
    jc_subject_filter = mo.ui.multiselect(
        options=[
            "english", "gaeilge", "mathematics", "irish_history", "geography",
            "science", "business_studies", "french", "german", "spanish",
            "italian", "home_economics", "music", "art", "technology",
            "engineering", "graphics", "wood_technology",
        ],
        value=["english", "gaeilge", "mathematics", "science"],
        label="Junior Cycle subject",
    )
    year_filter = mo.ui.multiselect(
        options=["year_1", "year_2", "year_3"],
        value=["year_1", "year_2", "year_3"],
        label="Year",
    )
    language_filter = mo.ui.multiselect(
        options=["en", "ga"],
        value=["en", "ga"],
        label="Language",
    )
    mo.vstack([jc_subject_filter, year_filter, language_filter])
    return jc_subject_filter, year_filter, language_filter


@app.cell
def _ibis_conn(mo):
    """The ibis-first contract per the BIEP v2 spec."""
    import ibis

    conn = ibis.duckdb.connect("md:cianfhoghlaim")
    lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
    mo.md("✓ ibis-first contract wired — JC LanceDB namespace ready")
    return conn, lance


@app.cell
def _jc_outcomes_table(conn, jc_subject_filter, year_filter, language_filter):
    """The JC learning outcomes drill-down."""
    jc_outcomes = conn.sql(
        """
        SELECT subject, year, language, strand, learning_outcome_id,
               learning_outcome_text_en, learning_outcome_text_ga,
               blooms_taxonomy_level
        FROM cianfhoghlaim.education.british_isles.ireland.junior_cycle._all_outcomes
        WHERE subject IN %(subjects)s
          AND year IN %(years)s
          AND language IN %(languages)s
        ORDER BY subject, year, strand, learning_outcome_id
        """,
        params={
            "subjects": tuple(jc_subject_filter.value),
            "years": tuple(year_filter.value),
            "languages": tuple(language_filter.value),
        },
    ).execute()
    jc_outcomes
    return (jc_outcomes,)


@app.cell
def _jc_cbas_table(conn, jc_subject_filter):
    """The 36 NCCA JC CBAs (Classroom-Based Assessments)."""
    jc_cbas = conn.sql(
        """
        SELECT subject, cba_id, title_en, weighting, year,
               evidence_of_learning, success_criteria
        FROM cianfhoghlaim.education.british_isles.ireland.junior_cycle._all_cbas
        WHERE subject IN %(subjects)s
        ORDER BY subject, cba_id
        """,
        params={"subjects": tuple(jc_subject_filter.value)},
    ).execute()
    jc_cbas
    return (jc_cbas,)


@app.cell
def _year3_to_year4_progression(conn, jc_subject_filter):
    """The Year 3 (JC) → Year 4 (LC OL) topic progression.

    Joins the JC LanceDB table to the LC LanceDB table for the same subject.
    """
    progression = conn.sql(
        """
        SELECT
            jc.subject AS jc_subject,
            jc.year AS jc_year,
            jc.learning_outcome_id AS jc_lo_id,
            jc.learning_outcome_text_en AS jc_lo_text,
            lc.learning_outcome_id AS lc_lo_id,
            lc.learning_outcome_text_en AS lc_lo_text,
            'YEAR_3 -> LC_OL' AS progression_label
        FROM cianfhoghlaim.education.british_isles.ireland.junior_cycle._all_outcomes jc
        LEFT JOIN cianfhoghlaim.leaving_cert._all_syllabus lc
          ON lc.subject = jc.subject
         AND lc.level = 'ol'
         AND lc.language = jc.language
        WHERE jc.year = 'year_3'
          AND jc.subject IN %(subjects)s
        ORDER BY jc.subject, jc.learning_outcome_id
        """,
        params={"subjects": tuple(jc_subject_filter.value)},
    ).execute()
    progression
    return (progression,)


if __name__ == "__main__":
    app.run()
