"""Cross-Destination Join demo — dlt 1.30 §6.2.

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §6.2
change (dlt 1.30 cross-destination joins).

Demonstrates the canonical BIEP Ireland pattern of joining
**MotherDuck + R2 + local DuckLake** in a single marimo notebook
via dlt's `Relation.join(other, on=...)` API. The pattern uses:

- `dlt.dataset(destination, dataset_name)` to get a single Dataset
  handle for any of the 3 destinations.
- `dataset["table"]` to get the relation.
- `relation.join(other_dataset_relation, on="...")` — explicit `on=`
  is **required** for cross-destination joins per the dlt 1.30 docs
  (auto-discovered references only work for same-dataset joins).

The notebook is intentionally offline-by-default — it does NOT
contact any live destination unless the operator sets the
`CIANFHOGHLAIM_FETCH_DATA=1` env var. The default cell renders the
canonical join expression as SQL so a reviewer can audit the
predicate without needing a MotherDuck / R2 / DuckLake connection.

Reference: https://dlthub.com/docs/release-notes/1.30.0 (the
cross-destination joins item under "Improvements").
"""

# Canonical PEP 723 dependencies (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # noqa: F401

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full", app_title="BIEP v3 — Cross-Destination Join Demo (dlt 1.30 §6.2)")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # Cross-Destination Join Demo (dlt 1.30 §6.2)

        This marimo notebook demonstrates the canonical **BIEP Ireland**
        cross-destination join pattern:

        - **MotherDuck** (`md:cianfhoghlaim`) — managed DuckLake with the
          6 LC subjects
        - **R2** (Garage S3-compatible) — Parquet files for the
          per-jurisdiction extracted cohorts
        - **Local DuckLake** (Postgres catalog + Garage S3 storage) — the
          canonical BIEP v3 Ireland pipeline destination

        ## The §6.2 cross-destination join API

        Per dlt 1.30 release notes:

        > Cross-destination joins (join datasets that live on different
        > destinations — eager + lazy materialization; supported for
        > duckdb, motherduck, ducklake, lance, lancedb, filesystem).

        The API is:

        ```python
        import dlt

        motherduck_users = dlt.dataset(
            "md:cianfhoghlaim", dataset_name="lc_mathematics"
        )["users"]

        ducklake_orders = dlt.dataset(
            "ducklake", dataset_name="ireland_education"
        )["orders"]

        # 'on=' is REQUIRED for cross-destination joins
        joined = motherduck_users.join(
            ducklake_orders,
            on="motherduck_users.id = ducklake_orders.user_id",
        )

        # Render via marimo
        import pyarrow as pa
        result = joined.fetchall()       # lazy → pulls rows
        # or:   df = joined.df()           # eager pandas
        ```
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import os
    fetch_data = os.getenv("CIANFHOGHLAIM_FETCH_DATA") == "1"
    mo.md(
        f"""
        ## Cell 2 — Build the cross-destination relation

        `CIANFHOGHLAIM_FETCH_DATA = {os.getenv("CIANFHOGHLAIM_FETCH_DATA", "<unset>")}`

        {"**Live fetch enabled** — the cells below will attempt to contact the 3 destinations."
         if fetch_data else "**Offline mode** (the default) — the cross-destination join is rendered as SQL only. "
                              "Set `CIANFHOGHLAIM_FETCH_DATA=1` to execute the join against the live destinations."}
        """
    )
    return (fetch_data,)


@app.cell
def _(fetch_data):
    import marimo as mo

    # ─── The canonical 3 BIEP destinations + the join expression ──────
    # Per the §6.2 change + the v2 plan §6.2 + the cross-destination
    # join canonical pattern: use `dlt.dataset(destination, dataset_name)`
    # to get one Dataset handle per destination, then call
    # `dataset["table"]` to get a Relation, then call
    # `Relation.join(other_relation, on=...)`.

    motherduck_dataset = "md:cianfhoghlaim"          # §7.1 MotherDuck per-quadrant
    ducklake_dataset = "ducklake"                    # §7.1 Postgres-catalog DuckLake
    filesystem_dataset = "filesystem"                # §7.1 R2/Garage S3 filesystem

    # The 3 canonical join predicates the BIEP Ireland pipeline uses:
    lc_mathematics_joins = {
        # NCCA syllabus provenance (MotherDuck) ⨝ Ireland LC cohort (DuckLake)
        "ncca_syllabus_to_ireland_lc_cohort": (
            "motherduck.ncca_syllabus.id = ducklake.ireland_education.cohort_id"
        ),
        # Ireland LC cohort (DuckLake) ⨝ R2 exam paper chunks (filesystem)
        "ireland_lc_cohort_to_exam_papers_r2": (
            "ducklake.ireland_education.cohort_id = filesystem.exam_papers.cohort_id"
        ),
        # NCCA syllabus (MotherDuck) ⨝ R2 exam papers (filesystem) via the LC cohort bridge
        "ncca_syllabus_to_exam_papers_r2": (
            "motherduck.ncca_syllabus.id = filesystem.exam_papers.cohort_id"
        ),
    }

    if fetch_data:
        import dlt

        ds_md = dlt.dataset(motherduck_dataset, dataset_name="lc_mathematics")
        ds_dl = dlt.dataset(ducklake_dataset, dataset_name="ireland_education")
        ds_fs = dlt.dataset(filesystem_dataset, dataset_name="exam_papers")

        # The 3 cross-destination join relations (lazy)
        rel_sylabus_to_cohort = ds_md["ncca_syllabus"].join(
            ds_dl["ireland_education"],
            on=lc_mathematics_joins["ncca_syllabus_to_ireland_lc_cohort"],
        )
        rel_cohort_to_papers = ds_dl["ireland_education"].join(
            ds_fs["exam_papers"],
            on=lc_mathematics_joins["ireland_lc_cohort_to_exam_papers_r2"],
        )
        rel_syllabus_to_papers = ds_md["ncca_syllabus"].join(
            ds_fs["exam_papers"],
            on=lc_mathematics_joins["ncca_syllabus_to_exam_papers_r2"],
        )

        mo.md(
            "### Live fetch enabled — fetched the 3 Relations from the canonical destinations."
        )
    else:
        mo.md(
            "### Offline mode\n\nThe 3 cross-destination join predicates are:\n\n"
            + "\n".join(f"- `{name}`: `{pred}`" for name, pred in lc_mathematics_joins.items())
        )
    return (lc_mathematics_joins,)


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        ## Cell 4 — Canonical project structure

        The cross-destination join pattern is the canonical BIEP v3
        Ireland pattern that surfaces in the following places:

        - `notebooks/29_cross_destination_join_lc6.ipynb` — this notebook
          (Jupyter mirror for the §6.2 reviewer's verification)
        - `notebooks/29_cross_destination_join_lc6.py` — the marimo source
        - `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` —
          the canonical singleton at instantiation time
        - `orchestration/defs/2_materials/ireland_education/` — the
          Dagster asset group that calls `.run_with_tenacity_retry(...)`
        - `tests/dlt/test_biep_v3_jurisdiction_smoke.py` — the §6.3
          parametrised smoke test (10 BIEP v3 jurisdictions)

        ## Cell 5 — The §6.2 dlt release-notes quote

        > **Cross-destination joins** — join datasets that live on
        > different destinations — eager + lazy materialization;
        > supported for `duckdb`, `motherduck`, `ducklake`, `lance`,
        > `lancedb`, `filesystem`. (Source: dlt 1.30 release notes.)

        The `Relation.join(other, on=...)` call requires an explicit
        `on=` for cross-destination joins (auto-discovered references
        work for same-dataset joins only).
        """
    )
    return


if __name__ == "__main__":
    app.run()
