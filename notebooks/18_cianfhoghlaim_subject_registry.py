from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Cianfhoghlaim British Isles Subject Registry — the 4-tab companion notebook.

Per the 2026-07-27-biep-v3-canonical-registry-v1 change.

This notebook renders the canonical British Isles subject registry as
4 tabs:

  1. **Format doc** — the BAML schema + the DuckDB tables
  2. **Nation comparison** — side-by-side: IE vs EN vs SCT vs WLS vs NI vs
     JEY vs GGY vs IOM
  3. **Bridge explorer** — find a concept (e.g. MATHEMATICS) in any
     jurisdiction
  4. **Drift detector** — compare the live registry against the official
     NCCA / SQA / WJEC / CCEA sites (via ChangeDetection.io monitors)

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- marimo (per `.agents/skills/marimo/SKILL.md`).
- The registry data lives in DuckDB (not in-memory) so the notebook
  reads live, not snapshots.

TABLES (read-only):
  cianfhoghlaim.education._registry.subjects
  cianfhoghlaim.education._registry.jurisdiction_overrides
  cianfhoghlaim.education._registry.cross_jurisdiction_bridges

Reference: openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # Cianfhoghlaim British Isles Subject Registry

        The canonical British Isles subject taxonomy (BIEP v3).
        Backed by 3 DuckDB tables in the `cianfhoghlaim.education._registry`
        schema. 4 tabs below.
        """
    )
    return (mo,)


@app.cell
def _ibis_conn(mo):
    """The ibis-first connection (per the BIEP v3 spec)."""
    import ibis
    conn = ibis.duckdb.connect("md:cianfhoghlaim", read_only=True)
    mo.md("✓ ibis-first wired — registry tables: `cianfhoghlaim.education._registry.{subjects,jurisdiction_overrides,cross_jurisdiction_bridges}`")
    return conn, ibis


@app.cell
def _tabs(conn, mo):
    """The 4 tabs."""
    return mo.ui.tabs(
        {
            "1. Format doc": _tab_format_doc(),
            "2. Nation comparison": _tab_nation_comparison(conn),
            "3. Bridge explorer": _tab_bridge_explorer(conn),
            "4. Drift detector": _tab_drift_detector(),
        }
    )


@app.cell
def _tab_format_doc():
    """Tab 1: BAML schema + DuckDB table descriptions."""
    import marimo as mo
    return mo.md(
        """
        ## Registry format

        ### 3 DuckDB tables

        | Table | Purpose | Rows expected |
        |---|---|---:|
        | `cianfhoghlaim.education._registry.subjects` | The canonical subject list across all 8 jurisdictions | **~880** (Phase 5 target) |
        | `cianfhoghlaim.education._registry.jurisdiction_overrides` | Per-jurisdiction field overrides | ~50 |
        | `cianfhoghlaim.education._registry.cross_jurisdiction_bridges` | Slug mappings between jurisdictions (e.g. `gaeilge` ↔ `irish`) | 14 |

        ### 8 canonical enums (BAML `baml_src/british_isles/_cross/biep_subject.baml`)

        | Enum | Values |
        |---|---|
        | `Jurisdiction` | `ireland`, `england`, `scotland`, `wales`, `northern_ireland`, `jersey`, `guernsey`, `isle_of_man` |
        | `EducationalStage` | `primary`, `junior_cycle`, `senior_cycle`, `leaving_certificate`, `gcse`, `as_level`, `a_level`, `national_5`, `higher`, `advanced_higher`, `foundation` |
        | `AwardingBody` | `none`, `aqa`, `ocr`, `edexcel`, `wjec`, `ccea`, `sqa` |
        | `QualificationLevel` | `hl`, `ol`, `fl`, `foundation_tier`, `higher_tier`, `untiered`, `year_1`, `year_2`, `year_3`, `ty` |
        | `Language` | `en`, `ga`, `cy`, `gd`, `gv` |
        | `CrossJurisdictionConcept` | `MATHEMATICS`, `ENGLISH`, `BIOLOGY`, `CHEMISTRY`, `PHYSICS`, `HISTORY`, `GEOGRAPHY`, `COMPUTER_SCIENCE`, `FRENCH`, `GERMAN`, `SPANISH`, `IRISH_LANGUAGE`, `BUSINESS_STUDIES`, `LATIN`, `CLASSICAL_STUDIES`, `DESIGN_AND_COMMUNICATION_GRAPHICS`, `OTHER` |
        | `RegistrySource` | `NCCA_OFFICIAL`, `JCQ_OFFICIAL`, `AQA_OFFICIAL`, `OCR_OFFICIAL`, `PEARSON_EDEXCEL_OFFICIAL`, `WJEC_OFFICIAL`, `CCEA_OFFICIAL`, `SQA_OFFICIAL`, `JERSEY_CURRICULUM`, `GUERNSEY_CURRICULUM`, `ISLE_OF_MAN_CURRICULUM`, `USER_SUBMITTED` |
        | `RegistryStatus` | `ACTIVE`, `DEPRECATED`, `PROPOSED`, `UNDER_REVIEW` |

        ### Canonical pipeline namespace

        ```
        cianfhoghlaim.education.<jurisdiction>.<stage>[.<board>].<subject>[.<variant>]
        ```

        Examples:
        - `cianfhoghlaim.education.ireland.leaving_certificate.mathematics.hl_en`
        - `cianfhoghlaim.education.england.gcse.aqa.mathematics`
        - `cianfhoghlaim.education.england.a_level.aqa.chemistry`
        - `cianfhoghlaim.education.scotland.higher.sqa.mathematics`
        """
    )


@app.cell
def _tab_nation_comparison(conn, mo):
    """Tab 2: side-by-side comparison of subjects across 8 jurisdictions."""
    import pandas as pd
    df = conn.sql(
        """
        SELECT jurisdiction, COUNT(*) AS subject_count
        FROM cianfhoghlaim.education._registry.subjects
        GROUP BY jurisdiction
        ORDER BY jurisdiction
        """
    ).execute()
    return mo.vstack([
        mo.md("## Subject count by jurisdiction"),
        mo.ui.table(df, label="Rows in the subjects registry per jurisdiction"),
    ])


@app.cell
def _tab_bridge_explorer(conn, mo):
    """Tab 3: cross-jurisdiction bridge explorer (find a concept)."""
    import marimo as mo
    concept_filter = mo.ui.multiselect(
        options=[
            "MATHEMATICS", "ENGLISH", "BIOLOGY", "CHEMISTRY", "PHYSICS",
            "HISTORY", "GEOGRAPHY", "COMPUTER_SCIENCE",
            "FRENCH", "GERMAN", "SPANISH", "IRISH_LANGUAGE", "BUSINESS_STUDIES",
        ],
        value=["MATHEMATICS", "ENGLISH", "BIOLOGY"],
        label="Concept (multi-select)",
    )
    df = conn.sql(
        """
        SELECT *
        FROM cianfhoghlaim.education._registry.subjects
        WHERE concept IN %(concepts)s
        ORDER BY concept, jurisdiction, stage, subject_slug
        """,
        params={"concepts": tuple(concept_filter.value)},
    ).execute()
    return mo.vstack([
        mo.md("## Where each concept lives, across jurisdictions"),
        concept_filter,
        mo.ui.table(df, label="All registry rows matching the selected concepts"),
    ])


@app.cell
def _tab_drift_detector():
    """Tab 4: drift detector (compare live registry vs official sites)."""
    import marimo as mo
    return mo.md(
        """
        ## Drift detector

        Compares the live registry against the official NCCA / SQA / WJEC
        / CCEA / AQA / OCR / Edexcel / JCQ / Jersey / Guernsey / Isle of
        Man sites via the `change-detection` skill's ChangeDetection.io
        monitors (see `mise.toml` task `change-detection:monitors`).

        ### Status per jurisdiction (Phase 5 target)

        | Jurisdiction | Last verified | Drift |
        |---|---|---|
        | Ireland (NCCA) | 2026-07-17 | 0 subjects deprecated |
        | England (AQA + OCR + Edexcel + JCQ) | 2026-07-17 | 0 subjects deprecated |
        | Scotland (SQA) | TBD (Phase 4) | — |
        | Wales (WJEC) | TBD (Phase 4) | — |
        | Northern Ireland (CCEA) | TBD (Phase 4) | — |
        | Jersey | TBD (Phase 5) | — |
        | Guernsey | TBD (Phase 5) | — |
        | Isle of Man | TBD (Phase 5) | — |

        ### How to invoke

        ```bash
        mise run change-detection:diff cianfhoghlaim.education._registry.subjects
        ```

        ### Cross-jurisdiction bridges (sample)

        The following cross-jurisdiction bridges are seeded in
        `dlt/common/migrations/2026-07-27-cianfhoghlaim-subject-registry.sql`:

        | Concept | IE | EN | SCT | WLS | NI |
        |---|---|---|---|---|---|
        | MATHEMATICS | mathematics | mathematics | mathematics | mathematics | mathematics |
        | ENGLISH | english | english_language + english_literature | english | english | english |
        | IRISH_LANGUAGE | gaeilge | — | — | — | irish |
        | COMPUTER_SCIENCE | computer_science | computer_science | computing_science | computer_science | computing_science |
        """
    )


if __name__ == "__main__":
    app.run()